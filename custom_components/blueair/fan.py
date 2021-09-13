"""Support for Blueair fans."""
from homeassistant.components.fan import (
    FanEntity,
    SUPPORT_SET_SPEED,
    SUPPORT_PRESET_MODE,
)
from homeassistant.util.percentage import (
    int_states_in_range,
    ranged_value_to_percentage,
    percentage_to_ranged_value,
)
from homeassistant.const import (
    PERCENTAGE,
)

from typing import Any, Optional

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair fans from config entry."""
    devices: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for device in devices:
        entities.extend(
            [
                BlueairFan(f"{device.device_name}_fan", device),
            ]
        )
    async_add_entities(entities)


class BlueairFan(BlueairEntity, FanEntity):
    """Controls Fan."""

    def __init__(self, name, device):
        """Initialize the temperature sensor."""
        super().__init__("Fan", name, device)
        self._state: float = None

    @property
    def supported_features(self) -> int:
        return SUPPORT_SET_SPEED

    @property
    def is_on(self) -> int:
        return self._device.fan_speed > 0

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        return int(round(self._device.fan_speed * 33.33, 0))

    def set_percentage(self, percentage: int) -> None:
        """Sets fan speed percentage."""
        if percentage == 100:
            new_speed = "3"
        elif percentage > 50:
            new_speed = "2"
        elif percentage > 20:
            new_speed = "1"
        else:
            new_speed = "0"

        self._device.api_client.set_fan_speed(self._device.id, new_speed)
        self._device._attribute["fan_speed"] = str(percentage)
        self._device._update_device()


    def turn_off(self) -> None:
        self._device.api_client.set_fan_speed(self._device.id, "0")
        self._device._attribute["fan_speed"] = str(0)

    def turn_on(self) -> None:
        self._device.api_client.set_fan_speed(self._device.id, "2")
        self._device._attribute["fan_speed"] = str(66)


    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return 3
