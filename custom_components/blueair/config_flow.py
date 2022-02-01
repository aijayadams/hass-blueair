"""Config flow for blueair integration."""
import voluptuous as vol
from . import blueair


from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOGGER

DATA_SCHEMA = vol.Schema({vol.Required("username"): str, vol.Required("password"): str})


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    session = async_get_clientsession(hass)
    try:
        client = await hass.async_add_executor_job(
            lambda: blueair.BlueAir(
                username=data[CONF_USERNAME],
                password=data[CONF_PASSWORD]
            )
        )
        LOGGER.debug(f"Connecting as {data[CONF_USERNAME]}")
    except KeyError as e:
        raise InvalidAuth(f"BlueAir authorization failed")
    except Exception as e:
        raise CannotConnect()

    return {"title": f"BlueAir {data[CONF_USERNAME]}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for blueair."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USERNAME])
            self._abort_if_unique_id_configured()
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate we can't authenticate."""
