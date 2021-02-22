"""Platform for blueair sensor integration."""
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

from datetime import timedelta

from . import blueair

SCAN_INTERVAL = timedelta(seconds=300)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    try:
        api = blueair.BlueAir(username=config["user"], password=config["password"])
    except KeyError as e:
        raise Unauthorized(f"BlueAir authorizarion failed")

    ha_entities = []
    devices = api.get_devices()
    for dev in devices:
        ha_entities.append(
            BlueAirFilter(config=config, uuid=dev["uuid"], name=dev["name"], api=api)
        )

    add_entities(ha_entities)


class BlueAirFilter(Entity):
    """Representation of BlueAir Sensor Data."""

    should_poll = True

    def __init__(self, config, uuid, name, api):
        """Initialize the sensor."""
        self._state = None
        self._api = api
        self._ba_uuid = uuid
        self._ba_name = name

        self.update()

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._ba_attrs

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"BlueAir {self._ba_name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._ba_attrs = self._api.get_current_data_point(self._ba_uuid)
        self._state = self._ba_attrs["temperature"]
