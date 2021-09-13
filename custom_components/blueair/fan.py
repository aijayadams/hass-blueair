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
        return self._device.is_on

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        return int(round(self._device.fan_speed * 33.33, 0))

    async def async_set_percentage(self, percentage: int) -> None:
        """Sets fan speed percentage."""
        if percentage == 100:
            new_speed = "3"
        elif percentage > 50:
            new_speed = "2"
        elif percentage > 20:
            new_speed = "1"
        else:
            new_speed = "0"

        await self._device.set_fan_speed(new_speed)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.set_fan_speed("0")

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._device.set_fan_speed("2")

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return 3
