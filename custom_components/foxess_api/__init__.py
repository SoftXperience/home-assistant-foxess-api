"""The FoxESSCloud API integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_API_KEY
from homeassistant.core import HomeAssistant

from .const import CONF_SERIAL
from .const import DOMAIN, LOGGER
from .fox_ess_cloud_coordinator import FoxEssCloudCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FoxESSCloud API from a config entry."""
    api_key = entry.data.get(CONF_API_KEY) or None
    serial = entry.data.get(CONF_SERIAL) or None
    LOGGER.info("Setup FoxESSCloud API from config flow with api-key / serial: %s / %s", api_key, serial)
    coordinator = FoxEssCloudCoordinator(hass, api_key, serial)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
