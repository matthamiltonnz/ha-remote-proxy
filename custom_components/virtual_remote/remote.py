"""Virtual Remote entity."""
from __future__ import annotations

import logging
from typing import Any, Iterable

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_COMMANDS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a VirtualRemote entity for this config entry."""
    commands = entry.options.get(CONF_COMMANDS) or entry.data.get(CONF_COMMANDS, [])
    command_map = {c["command"]: c["entity_id"] for c in commands}
    async_add_entities([VirtualRemote(entry, command_map)])


class VirtualRemote(RemoteEntity):
    """A remote entity that proxies commands to individual button entities."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_is_on = True
    _attr_should_poll = False

    def __init__(
        self, entry: ConfigEntry, command_map: dict[str, str]
    ) -> None:
        """Initialise the virtual remote."""
        self._entry = entry
        self._command_map = command_map
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose available command names so external systems can discover them."""
        return {"commands": sorted(self._command_map.keys())}

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Press the button entity mapped to each command."""
        for cmd in command:
            entity_id = self._command_map.get(cmd)
            if entity_id is None:
                _LOGGER.warning(
                    "Virtual remote '%s' received unknown command '%s'. "
                    "Available: %s",
                    self._entry.title,
                    cmd,
                    sorted(self._command_map),
                )
                continue
            await self.hass.services.async_call(
                "button",
                "press",
                {"entity_id": entity_id},
                blocking=True,
            )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Virtual remotes are always on."""

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Virtual remotes are always on."""
