from collections import defaultdict
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER
from .fox_ess_cloud_api import FoxEssCloudApi


class FoxEssCloudCoordinator(DataUpdateCoordinator[defaultdict]):
    """FoxEssCloudCoordinator"""

    def __init__(self, hass: HomeAssistant, api_key, serial) -> None:
        """Initialize the coordinator."""

        self.serial = serial

        self.api = FoxEssCloudApi(
            hass,
            api_key,
            self.serial
        )

        update_interval = timedelta(minutes=3)

        super().__init__(hass, LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self) -> defaultdict:
        result = await self.api.update_data()
        LOGGER.debug("Update finished, processed data: %s", result)
        return result
