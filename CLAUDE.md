# Virtual Remotes — Home Assistant Custom Integration

Wraps any set of `button` entities into a single `remote` entity, making them callable
via `remote.send_command`. Designed for MQTT-discovered buttons (e.g. LinknLink eRemote Mini)
that need to be exposed as a remote to external controllers like Unfolded Circle Remote 3.

## How it works

1. User creates a config entry via the UI, gives the remote a name, and selects button entities.
2. User assigns a command name to each button (e.g. `button.unnamed_device_53` → `"Play"`).
3. The integration creates a `remote` entity. Calling `remote.send_command` with a command
   name triggers `button.press` on the mapped entity.
4. The `commands` attribute on the entity lists all available command names — Unfolded Circle
   and other external controllers can read this to discover what commands exist.

## File structure

```
custom_components/virtual_remote/
  __init__.py       # Entry setup/unload, options reload listener
  config_flow.py    # Two-step config flow: entity selection → command naming
                    # Same two steps used for options flow (reconfigure)
  const.py          # DOMAIN, CONF_COMMANDS
  manifest.json
  remote.py         # VirtualRemote entity — proxies send_command → button.press
  strings.json      # UI string keys (references common:: keys for standard messages)
  translations/
    en.json         # English translations
```

## Data model

Config entry data:
```python
{
    "commands": [
        {"entity_id": "button.unnamed_device_53", "command": "Home"},
        {"entity_id": "button.unnamed_device_35", "command": "Up"},
        ...
    ]
}
```

Options (written by options flow, takes priority over data):
```python
{
    "commands": [...]  # Same structure — full replacement when options are saved
}
```

The entity reads: `entry.options.get("commands") or entry.data.get("commands", [])`.

## Usage

```yaml
# Call a command
service: remote.send_command
target:
  entity_id: remote.blu_ray_player
data:
  command: Play

# Call multiple commands sequentially
service: remote.send_command
target:
  entity_id: remote.blu_ray_player
data:
  command:
    - Home
    - Up
    - Select
```

## Config flow UX notes

- **Step 1 (names)**: Field labels are the raw entity_id strings (e.g. `button.unnamed_device_53`)
  because HA config flow labels come from static strings.json keys and can't be dynamic.
  The entity picker in step 0 shows friendly names to help the user identify entities.
- **Options flow**: Same two steps as initial setup. Reconfiguring replaces the full command list.
  The previous command names are pre-filled as defaults.

## Unfolded Circle integration

UC reads the `commands` state attribute to discover available commands. Map them in the
UC integration using the exact command name strings set during config flow.

The remote entity is always `is_on = True` — virtual remotes have no meaningful power state.

## Planned extensibility: additional command sources

Currently every command maps to `button.press`. Future versions should extend the data
model so each command can specify a different service:

```python
# Proposed extended command entry
{"command": "Volume Up", "entity_id": "remote.tcl_tv", "service": "remote.send_command", "service_data": {"command": "VOLUME_UP"}}
{"command": "Pause",     "entity_id": "media_player.lounge", "service": "media_player.media_pause", "service_data": {}}
{"command": "Play",      "entity_id": "button.unnamed_device_39", "service": "button.press", "service_data": {}}
```

The `remote.py` `async_send_command` method would then call `hass.services.async_call`
using the per-command `service` and `service_data` rather than always calling `button.press`.

The config flow would need a per-command source type picker (button / remote / media_player / script)
that shows the appropriate entity selector and optional service data fields.

Backward compatibility: existing entries without a `service` key default to `button.press`.

## Community sharing checklist

- [x] Update `manifest.json` `documentation` URL to the real GitHub repo
- [x] Add `README.md` with install instructions and usage examples
- [ ] Tag with semantic version matching `manifest.json` `version`
- [ ] Submit to HACS default repository list (requires `hacs.json` + README + info.md)
