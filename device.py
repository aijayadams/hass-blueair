"""Blueair device object."""
import asyncio
from datetime import datetime, timedelta
from typing import Any
from async_timeout import timeout


from . import blueair

API = blueair.BlueAir

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .const import DOMAIN, LOGGER


class BlueairDataUpdateCoordinator(DataUpdateCoordinator):
    """Blueair device object."""

    def __init__(
        self, hass: HomeAssistant, api_client: API, uuid: str, device_name: str
    ) -> None:
        """Initialize the device."""
        self.hass: HomeAssistant = hass
        self.api_client: API = api_client
        self._uuid: str = uuid
        self._name: str = device_name
        self._manufacturer: str = "BlueAir"
        self._device_information: dict[str, Any] = {}
        self._datapoint: dict[str, Any] = {}
        self._attribute: dict[str, Any] = {}

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}-{device_name}",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with timeout(10):
                await asyncio.gather(*[self._update_device()])
        except Exception as error:
            print(error)
            raise error
            raise UpdateFailed(error) from error

    @property
    def id(self) -> str:
        """Return Blueair device id."""
        return self._uuid

    @property
    def device_name(self) -> str:
        """Return device name."""
        return self._device_information.get("nickname", f"{self.name}")

    @property
    def manufacturer(self) -> str:
        """Return manufacturer for device."""
        return self._manufacturer

    @property
    def model(self) -> str:
        """Return model for device, or the UUID if it's not known."""
        return self._device_information.get("compatibility", self.id)

    @property
    def temperature(self) -> float:
        """Return the current temperature in degrees C."""
        return self._datapoint["temperature"]

    @property
    def humidity(self) -> float:
        """Return the current relative humidity percentage."""
        return self._datapoint["humidity"]

    @property
    def fan_speed(self) -> int:
        """Return the current fan speed."""
        return int(self._attribute["fan_speed"])

    @property
    def fan_mode(self) -> str:
        """Return the current fan mode."""
        return self._attribute["fan_mode"]

    @property
    def filter_status(self) -> str:
        """Return the current filter status."""
        return self._attribute["filter_status"]

    async def _update_device(self, *_) -> None:
        """Update the device information from the API."""
        self._device_information = await self.hass.async_add_executor_job(
            lambda: self.api_client.get_info(self._uuid)
        )
        self._datapoint = await self.hass.async_add_executor_job(
            lambda: self.api_client.get_current_data_point(self._uuid)
        )
        self._attribute = await self.hass.async_add_executor_job(
            lambda: self.api_client.get_attributes(self._uuid)
        )
