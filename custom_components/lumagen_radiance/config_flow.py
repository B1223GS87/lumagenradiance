"""Config flow for Lumagen Radiance integration."""

import logging
from typing import Any, Dict

import voluptuous

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, INPUT_LABELS

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = voluptuous.Schema(
    {
        voluptuous.Required("host"): str,
        voluptuous.Required("port", default=10001): int,
    }
)

class LumagenRadianceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lumagen Radiance."""

    VERSION = 1

    async def async_step_user(self, user_input: Dict[str, Any] | None = None) -> config_entries.FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Validate host and port (basic check)
        # In a real integration, you might try to connect here

        return self.async_create_entry(
            title="Lumagen Radiance",
            data=user_input,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for the config entry."""
        return LumagenRadianceOptionsFlowHandler(config_entry)

class LumagenRadianceOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Lumagen Radiance."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Dict[str, Any] | None = None) -> config_entries.FlowResult:
        """Manage the options."""
        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=voluptuous.Schema(
                    {
                        voluptuous.Optional("input_labels", default=dict(self.config_entry.options.get("input_labels", INPUT_LABELS))): dict,
                    }
                ),
            )

        return self.async_create_entry(
            title="",
            data=user_input,
        )
