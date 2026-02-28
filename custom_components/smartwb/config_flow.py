import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, AVAILABLE_ENTITIES

_LOGGER = logging.getLogger(__name__)


class SmartWBConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SmartWB."""

    VERSION = 1

    async def async_step_user(self, user_input: Dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            ip = user_input["ip_address"]
            port = user_input["port"]
            name = user_input["name"]

            await self.async_set_unique_id(f"{ip}:{port}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=name,
                data={
                    "ip_address": ip,
                    "port": port,
                    "name": name,
                },
            )

        schema = vol.Schema(
            {
                vol.Required("ip_address"): str,
                vol.Required("port", default=80): int,
                vol.Required("name", default="SmartWB"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_import(self, user_input: Dict[str, Any]) -> FlowResult:
        return await self.async_step_user(user_input)


class SmartWBOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options

        schema = {
            vol.Optional(
                key,
                default=options.get(key, True),
            ): bool
            for key in AVAILABLE_ENTITIES
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
        )