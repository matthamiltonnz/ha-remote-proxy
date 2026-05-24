"""Config flow for Virtual Remote."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import device_registry as dr, entity_registry as er, selector

from .const import CONF_COMMANDS, DOMAIN


def _default_command_name(entity_id: str, registry: er.EntityRegistry) -> str:
    """Derive a readable command name from an entity."""
    entry = registry.async_get(entity_id)
    if entry:
        name = entry.name or entry.original_name
        if name:
            return name
    slug = entity_id.split(".", 1)[-1]
    return slug.replace("_", " ").title()


def _active_commands(entry: config_entries.ConfigEntry) -> list[dict]:
    """Return the current command list, preferring options over data."""
    return entry.options.get(CONF_COMMANDS) or entry.data.get(CONF_COMMANDS, [])


def _buttons_for_device(device_id: str, entity_reg: er.EntityRegistry) -> list[str]:
    """Return all enabled button entity IDs belonging to a device."""
    return [
        entry.entity_id
        for entry in entity_reg.entities.values()
        if entry.device_id == device_id
        and entry.domain == "button"
        and not entry.disabled_by
    ]


def _resolve_entities(user_input: dict, entity_reg: er.EntityRegistry) -> list[str]:
    """Return entity list: device-based if a device was selected, else manual pick."""
    if device_id := user_input.get("select_device"):
        return _buttons_for_device(device_id, entity_reg)
    return user_input.get("button_entities") or []


_ENTITY_SELECTOR = selector.selector(
    {"entity": {"multiple": True, "filter": {"domain": "button"}}}
)
_DEVICE_SELECTOR = selector.selector({"device": {}})


class VirtualRemoteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Virtual Remote config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise flow state."""
        self._remote_name: str = ""
        self._selected_entities: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: remote name + button source selection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entity_reg = er.async_get(self.hass)
            entities = _resolve_entities(user_input, entity_reg)
            if not entities:
                errors["base"] = "no_entities"
            else:
                self._remote_name = user_input["name"]
                self._selected_entities = entities
                return await self.async_step_names()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("name"): selector.selector({"text": {}}),
                    vol.Optional("select_device"): _DEVICE_SELECTOR,
                    vol.Optional("button_entities"): _ENTITY_SELECTOR,
                }
            ),
            errors=errors,
        )

    async def async_step_names(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: assign a command name to each selected button."""
        if user_input is not None:
            commands = [
                {"entity_id": eid, "command": user_input[eid]}
                for eid in self._selected_entities
            ]
            return self.async_create_entry(
                title=self._remote_name,
                data={CONF_COMMANDS: commands},
            )

        entity_reg = er.async_get(self.hass)
        schema = vol.Schema(
            {
                vol.Required(
                    eid, default=_default_command_name(eid, entity_reg)
                ): selector.selector({"text": {}})
                for eid in self._selected_entities
            }
        )
        return self.async_show_form(step_id="names", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> VirtualRemoteOptionsFlow:
        """Return the options flow handler."""
        return VirtualRemoteOptionsFlow()


class VirtualRemoteOptionsFlow(config_entries.OptionsFlow):
    """Handle options for an existing Virtual Remote entry."""

    def __init__(self) -> None:
        """Initialise options flow state."""
        self._selected_entities: list[str] = []

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: edit the button source selection."""
        errors: dict[str, str] = {}
        current_entities = [
            c["entity_id"] for c in _active_commands(self.config_entry)
        ]

        if user_input is not None:
            entity_reg = er.async_get(self.hass)
            entities = _resolve_entities(user_input, entity_reg)
            if not entities:
                errors["base"] = "no_entities"
            else:
                self._selected_entities = entities
                return await self.async_step_names()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional("select_device"): _DEVICE_SELECTOR,
                    vol.Optional(
                        "button_entities", default=current_entities
                    ): _ENTITY_SELECTOR,
                }
            ),
            errors=errors,
        )

    async def async_step_names(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: edit command names for each button."""
        if user_input is not None:
            commands = [
                {"entity_id": eid, "command": user_input[eid]}
                for eid in self._selected_entities
            ]
            return self.async_create_entry(data={CONF_COMMANDS: commands})

        current_names = {
            c["entity_id"]: c["command"]
            for c in _active_commands(self.config_entry)
        }
        entity_reg = er.async_get(self.hass)
        schema = vol.Schema(
            {
                vol.Required(
                    eid,
                    default=current_names.get(
                        eid, _default_command_name(eid, entity_reg)
                    ),
                ): selector.selector({"text": {}})
                for eid in self._selected_entities
            }
        )
        return self.async_show_form(step_id="names", data_schema=schema)
