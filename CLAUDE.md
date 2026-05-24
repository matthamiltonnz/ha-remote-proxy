# Remote Proxy — Home Assistant Custom Integration

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
custom_components/remote_proxy/
  __init__.py       # Entry setup/unload, options reload listener
  config_flow.py    # Two-step config flow: entity selection → command naming
                    # Same two steps used for options flow (reconfigure)
  const.py          # DOMAIN, CONF_COMMANDS
  manifest.json
  remote.py         # ProxyRemote entity — proxies send_command → button.press
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
    ],
    "turn_on_command": "Power On",   # optional — one of the command names above
    "turn_off_command": "Power Off"  # optional
}
```

Options (written by options flow, takes priority over data):
```python
{
    "commands": [...],         # Full replacement when options are saved
    "turn_on_command": "...",  # optional
    "turn_off_command": "..."  # optional
}
```

The entity reads: `entry.options.get(key) or entry.data.get(key)`.

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
- **Step 2 (power)**: Two optional select dropdowns built from the command names entered in step 1.
  If left blank, the toggle buttons on the remote card do nothing (no error).
- **Options flow**: Same steps as initial setup. Reconfiguring replaces the full command list.
  Previous command names and power bindings are pre-filled as defaults.

## Power toggle behaviour

`is_on` always returns `True` — the virtual remote has no meaningful on/off state.
`async_turn_on` and `async_turn_off` fire `async_send_command` with the configured command
name, which in turn calls `button.press` on the mapped entity. If no command is bound, the
toggle is a no-op (HA still shows the toggle but pressing it has no effect).

## Compatible controller notes

### Unfolded Circle Remote 3
UC reads the `commands` state attribute to auto-discover available commands.

### Astrion Remote (RosCard — https://github.com/yyqclhy/RosCard)
RosCard is a Lovelace card collection that runs on the Astrion Remote's screen. It works
by calling HA services from card button actions — there is no native remote entity protocol.
To use Remote Proxy with RosCard, configure each card button action to call
`remote.send_command` targeting the virtual remote entity with the relevant command name.

RosCard card types that can call arbitrary HA services: ros-tv-card (power_on/off, directional,
long-press bindings), ros-scene-card (scripts/scenes). Map each button to a
`remote.send_command` service call with the command string from the `commands` attribute.

No code changes needed — compatibility is purely through HA service calls.

## Unfolded Circle integration

UC reads the `commands` state attribute to discover available commands. Map them in the
UC integration using the exact command name strings set during config flow.

The remote entity is always `is_on = True` — virtual remotes have no meaningful power state.

## Community sharing checklist

- [x] Update `manifest.json` `documentation` URL to the real GitHub repo
- [x] Add `README.md` with install instructions and usage examples
- [ ] Tag with semantic version matching `manifest.json` `version`
- [ ] Submit to HACS default repository list (requires `hacs.json` + README + info.md)
