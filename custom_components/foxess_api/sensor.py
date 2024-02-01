from datetime import datetime

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER, API_VERSION, CONF_SERIAL
from .fox_ess_cloud_coordinator import FoxEssCloudCoordinator
from .sensor_descriptions import SENSORS, FoxEssEntityDescription

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_SERIAL): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    api_key = config.get(CONF_API_KEY)
    serial = config.get(CONF_SERIAL)
    LOGGER.info("Setup FoxESSCloud API from platform config with api-key / serial: %s / %s", api_key, serial)
    coordinator = FoxEssCloudCoordinator(hass, api_key, serial)
    await coordinator.async_config_entry_first_refresh()
    await add_sensors(async_add_entities, coordinator, serial)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: FoxEssCloudCoordinator = hass.data[DOMAIN][entry.entry_id]
    await add_sensors(async_add_entities, coordinator, entry.entry_id)


async def add_sensors(async_add_entities, coordinator, serial):
    sanitized_sensors = filter(lambda sensor: sensor.variable is not None and sensor.state is not None, SENSORS)
    async_add_entities(
        FoxEssSensorEntity(
            entry_id=serial,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in sanitized_sensors
    )


class FoxEssSensorEntity(CoordinatorEntity[FoxEssCloudCoordinator], SensorEntity):
    entity_description: FoxEssEntityDescription
    _attr_has_entity_name = True

    def __init__(
            self,
            *,
            entry_id: str,
            coordinator: FoxEssCloudCoordinator,
            entity_description: FoxEssEntityDescription
    ) -> None:
        super().__init__(coordinator=coordinator)
        self.entity_description = entity_description
        self.entity_id = f"{SENSOR_DOMAIN}.{self.coordinator.serial}_{entity_description.key}"
        self._attr_unique_id = f"{entry_id}_{entity_description.key}"

        # self._attr_device_info = coordinator.device_info
        # DeviceInfo(
        #         identifiers={(DOMAIN, self.serial)},
        #         manufacturer="Fox ESS",
        #         model="Fox ESS Cloud",
        #         name="Foxx Name",
        #         configuration_url=BASE_URL
        #     )

    @property
    def native_value(self) -> datetime | StateType:
        self.available
        if self.entity_description.state is None:
            return None
        else:
            try:
                value = self.entity_description.state(self.coordinator.data)
                if self.entity_description.process is not None:
                    value = self.entity_description.process(value)
                return value
            except KeyError:
                LOGGER.warning("Could not get state for %s. If this error persists, "
                               "check API for changes. (Current version is %s)",
                               self.entity_description.key,
                               API_VERSION)
                return None
            except TypeError as te:
                LOGGER.error(te)
                LOGGER.warning("Type error for %s. If this error persists, "
                               "check API for changes. (Current version is %s)",
                               self.entity_description.key,
                               API_VERSION)
                return None
            except Exception as e:
                LOGGER.error(e)
