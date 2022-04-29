"""Support for Blueair sensors."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    DEVICE_CLASS_CO2,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PM1,
    DEVICE_CLASS_PM10,
    DEVICE_CLASS_PM25,
    DEVICE_CLASS_VOLATILE_ORGANIC_COMPOUNDS,
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
        # Only add sensors to non-classic models
        if not device.model.startswith('classic') and not device.model == 'foobot':
            entities.extend(
                [
                    BlueairTemperatureSensor(f"{device.device_name}_temperature", device),
                    BlueairHumiditySensor(f"{device.device_name}_humidity", device),
                    BlueairCO2Sensor(f"{device.device_name}_co2", device),
                    BlueairVOCSensor(f"{device.device_name}_voc", device),
                    BlueairAllPollutionSensor(
                        f"{device.device_name}_all_pollution", device
                    ),
                    BlueairPM1Sensor(f"{device.device_name}_pm1", device),
                    BlueairPM10Sensor(f"{device.device_name}_pm10", device),
                    BlueairPM25Sensor(f"{device.device_name}_pm25", device),
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


class BlueairCO2Sensor(BlueairEntity, SensorEntity):
    """Monitors the CO2."""

    _attr_device_class = DEVICE_CLASS_CO2
    _attr_native_unit_of_measurement = "ppm"

    def __init__(self, name, device):
        """Initialize the CO2 sensor."""
        super().__init__("co2", name, device)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current co2."""
        if self._device.co2 is None:
            return None
        return round(self._device.co2, 0)


class BlueairVOCSensor(BlueairEntity, SensorEntity):
    """Monitors the VOC."""

    _attr_device_class = DEVICE_CLASS_VOLATILE_ORGANIC_COMPOUNDS
    _attr_native_unit_of_measurement = "ppb"

    def __init__(self, name, device):
        """Initialize the VOC sensor."""
        super().__init__("voc", name, device)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current voc."""
        if self._device.voc is None:
            return None
        return round(self._device.voc, 0)


class BlueairAllPollutionSensor(BlueairEntity, SensorEntity):
    """Monitors the all pollution."""
    """The API returns the unit for this measurement as as % """
    _attr_native_unit_of_measurement = "%"

    def __init__(self, name, device):
        """Initialize the all pollution sensor."""
        super().__init__("all_pollution", name, device)
        self._state: float = None
        self._attr_icon = "mdi:molecule"

    @property
    def native_value(self) -> float:
        """Return the current all pollution."""
        if self._device.all_pollution is None:
            return None
        return round(self._device.all_pollution, 0)


class BlueairPM1Sensor(BlueairEntity, SensorEntity):
    """Monitors the pm1"""

    _attr_device_class = DEVICE_CLASS_PM1
    _attr_native_unit_of_measurement = "µg/m³"

    def __init__(self, name, device):
        """Initialize the pm1 sensor."""
        super().__init__("pm1", name, device)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current pm1."""
        if self._device.pm1 is None:
            return None
        return round(self._device.pm1, 0)


class BlueairPM10Sensor(BlueairEntity, SensorEntity):
    """Monitors the pm10"""

    _attr_device_class = DEVICE_CLASS_PM10
    _attr_native_unit_of_measurement = "µg/m³"

    def __init__(self, name, device):
        """Initialize the pm10 sensor."""
        super().__init__("pm10", name, device)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current pm10."""
        if self._device.pm10 is None:
            return None
        return round(self._device.pm10, 0)


class BlueairPM25Sensor(BlueairEntity, SensorEntity):
    """Monitors the pm25"""

    _attr_device_class = DEVICE_CLASS_PM25
    _attr_native_unit_of_measurement = "µg/m³"

    def __init__(self, name, device):
        """Initialize the pm25 sensor."""
        super().__init__("pm25", name, device)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current pm25."""
        if self._device.pm25 is None:
            return None
        return round(self._device.pm25, 0)

class BlueairFilterStatusSensor(BlueairEntity, SensorEntity):
    """Monitors the status of the Filter"""

    def __init__(self, name, device):
        """Initialize the filter_status sensor."""
        super().__init__("filter_status", name, device)
        self._state: str = None
        self._attr_icon = "mdi:air-filter"

    @property
    def native_value(self) -> float:
        """Return the current filter_status."""
        if self._device.filter_status is None:
            return None
        return str(self._device.filter_status)
