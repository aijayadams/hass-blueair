"""The blueair integration."""
import asyncio
import logging

from . import blueair

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CLIENT, DOMAIN
from .device import BlueairDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up blueair from a config entry."""
    session = async_get_clientsession(hass)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    try:
        client = await hass.async_add_executor_job(
            lambda: blueair.BlueAir(
                username=entry.data[CONF_USERNAME], password=entry.data[CONF_PASSWORD]
            )
        )
        hass.data[DOMAIN][entry.entry_id][CLIENT] = client
    except KeyError as e:
        raise Unauthorized(f"BlueAir authorizarion failed")

    devices = await hass.async_add_executor_job(lambda: client.get_devices())
    hass.data[DOMAIN][entry.entry_id]["devices"] = [
        BlueairDataUpdateCoordinator(hass, client, device["uuid"], device["name"])
        for device in devices
    ]
    _LOGGER.debug(f"BlueAir Devices {devices}")

    tasks = [
        device.async_refresh()
        for device in hass.data[DOMAIN][entry.entry_id]["devices"]
    ]
    await asyncio.gather(*tasks)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
