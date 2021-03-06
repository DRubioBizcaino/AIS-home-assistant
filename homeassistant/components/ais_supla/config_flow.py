"""Config flow to configure Supla component."""

import voluptuous as vol
from pysupla import SuplaAPI

from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import callback
from homeassistant.util import slugify
import logging

from .const import DOMAIN, CONF_SERVER

_LOGGER = logging.getLogger(__name__)


@callback
def configured_supla_hosts(hass):
    """Return a set of the configured supla hosts."""
    return set(
        (slugify(entry.data[CONF_SERVER]))
        for entry in hass.config_entries.async_entries(DOMAIN)
    )


@config_entries.HANDLERS.register(DOMAIN)
class AisSuplaFlowHandler(config_entries.ConfigFlow):
    """AIS Supla config flow."""

    VERSION = 1

    def __init__(self):
        """Initialize Supla configuration flow."""
        pass

    async def async_step_import(self, import_config):
        """Import the supla server as config entry."""
        _LOGGER.warning("Go to async_step_user")
        return await self.async_step_init(user_input=import_config)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return await self.async_step_init(user_input=None)
        return self.async_show_form(step_id="confirm")

    async def async_step_confirm(self, user_input=None):
        """Handle a flow start."""
        errors = {}
        if user_input is not None:
            return await self.async_step_init(user_input=None)
        return self.async_show_form(step_id="confirm", errors=errors)

    async def async_step_init(self, user_input=None):
        """Handle a flow start."""
        errors = {}
        description_placeholders = {"error_info": ""}
        if user_input is not None:
            # Test connection
            server = SuplaAPI(user_input[CONF_SERVER], user_input[CONF_ACCESS_TOKEN])
            srv_info = server.get_server_info()
            if srv_info.get("authenticated"):
                """Finish config flow"""
                return self.async_create_entry(
                    title="AIS " + user_input[CONF_SERVER], data=user_input
                )
            else:
                _LOGGER.error(
                    "Server: %s not configured. API call returned: %s",
                    user_input[CONF_SERVER],
                    srv_info,
                )
                errors = {CONF_SERVER: "supla_no_connection"}
                description_placeholders = {"error_info": str(srv_info)}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Required(CONF_SERVER): str, vol.Required(CONF_ACCESS_TOKEN): str}
            ),
            errors=errors,
            description_placeholders=description_placeholders,
        )
