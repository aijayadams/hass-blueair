"""Base entity class for Blueair entities."""
from typing import Any

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator


class BlueairEntity(Entity):
    """A base class for Blueair entities."""

    _attr_force_update = False
    _attr_should_poll = False

    def __init__(
        self,
        entity_type: str,
        name: str,
        device: BlueairDataUpdateCoordinator,
        **kwargs,
    ) -> None:
        """Init Blueair entity."""
        self._attr_name = f"{name}"
        self._attr_unique_id = f"{device.id}_{entity_type}"

        self._device: BlueairDataUpdateCoordinator = device
        self._state: Any = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""
        return {
            "identifiers": {(DOMAIN, self._device.id)},
            "manufacturer": self._device.manufacturer,
            "model": self._device.model,
            "name": self._device.device_name,
        }

    async def async_update(self):
        """Update Blueair entity."""
        await self._device.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(self._device.async_add_listener(self.async_write_ha_state))
