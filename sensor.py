"""Support for Blueair sensors."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    TEMP_CELSIUS,
    PERCENTAGE,
)

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity

NAME_TEMPERATURE = "Temperature"
NAME_HUMIDITY = "Humidity"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair sensors from config entry."""
    devices: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for device in devices:
        entities.extend(
            [
                BlueairTemperatureSensor(f"{device.device_name}_temperature", device),
                BlueairHumiditySensor(f"{device.device_name}_humidity", device),
            ]
        )
    async_add_entities(entities)


class BlueairTemperatureSensor(BlueairEntity, SensorEntity):
    """Monitors the temperature."""

    _attr_device_class = DEVICE_CLASS_TEMPERATURE
    _attr_native_unit_of_measurement = TEMP_CELSIUS

    def __init__(self, name, device):
        """Initialize the temperature sensor."""
        super().__init__(NAME_TEMPERATURE, name, device)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current temperature."""
        if self._device.temperature is None:
            return None
        return round(self._device.temperature, 1)


class BlueairHumiditySensor(BlueairEntity, SensorEntity):
    """Monitors the humidity."""

    _attr_device_class = DEVICE_CLASS_HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, name, device):
        """Initialize the humidity sensor."""
        super().__init__(NAME_HUMIDITY, name, device)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current humidity."""
        if self._device.humidity is None:
            return None
        return round(self._device.humidity, 0)
