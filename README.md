# Virtual Remotes

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration that groups individual button entities into a single `remote` entity, callable via `remote.send_command`.

Useful when devices expose controls as separate buttons (common with MQTT-discovered devices like LinknLink eRemote Mini) but you need a unified remote entity for external controllers such as [Unfolded Circle Remote 3](https://www.unfoldedcircle.com/).

---

## Features

- Create as many virtual remotes as you need — one per device
- Assign meaningful command names to each button (e.g. `button.unnamed_device_53` → `"Play"`)
- Works with any `button` entity regardless of source (MQTT, LinknLink, Z-Wave, etc.)
- Exposes a `commands` attribute listing all available commands — external controllers can read this to discover what's available
- Bind the remote's power toggle to real device commands (e.g. `Power On` / `Power Off`)
- Reconfigure at any time via the integration's **Configure** button — add/remove buttons and rename commands without recreating the entry

---

## Installation

### HACS (recommended)

1. In HACS, go to **Integrations** → three-dot menu → **Custom repositories**
2. Add `https://github.com/matthamiltonnz/ha-virtual-remotes` as an **Integration**
3. Search for **Virtual Remotes** and install
4. Restart Home Assistant

> **Note:** A restart is required after every install or update — HACS copies the files but HA only loads custom components on startup.

### Manual

1. Copy `custom_components/virtual_remote/` into your HA `config/custom_components/` folder
2. Restart Home Assistant

---

## Setup

1. Go to **Settings → Devices & Services → Add Integration** and search for **Virtual Remotes**
2. Enter a name for the remote (e.g. `Blu-ray Player`)
3. Select the button entities you want to include (pick a device to grab all its buttons at once, or choose individually)
4. Review and remove any buttons you don't need
5. Give each button a command name (e.g. `Play`, `Pause`, `Home`, `Up`, `Select`)
6. Optionally bind the power toggle to turn-on and turn-off commands
7. A `remote.<name>` entity is created

Repeat for each device you want to expose as a remote.

---

## Usage

```yaml
# Single command
service: remote.send_command
target:
  entity_id: remote.blu_ray_player
data:
  command: Play

# Multiple commands in sequence
service: remote.send_command
target:
  entity_id: remote.blu_ray_player
data:
  command:
    - Home
    - Up
    - Select
```

The `commands` state attribute lists every available command name:

```yaml
commands:
  - Home
  - Menu
  - Pause
  - Play
  - Select
  - Skip Backward
  - Skip Forward
  - Up
  - Down
  - Left
  - Right
```

---

## Reconfiguring

To add/remove buttons or rename commands, go to **Settings → Devices & Services → Integrations → Virtual Remotes**, then click the **gear icon** on your entry. This opens the full options flow.

> The pencil/edit icon on the remote entity only changes the entity name and area — use the gear icon on the integration entry for button mappings.

---

## Button entity sources

Virtual Remotes works with any `button` entity in Home Assistant, regardless of how it was created. A common use case is **LinknLink devices connected via MQTT** — the LinknLink MQTT integration auto-discovers each button on a device and creates individual `button` entities (e.g. `button.unnamed_device_35`, `button.unnamed_device_53`). These can't be controlled as a unified remote out of the box.

Virtual Remotes solves this: use **Select all button entities** during setup to pull in all of them at once, then give each one a meaningful command name (e.g. `Play`, `Home`, `Up`). The result is a single `remote.blu_ray_player` entity you can drive with `remote.send_command`.

Other supported sources include any integration that exposes `button` entities — Z-Wave, Zigbee, custom MQTT devices, scripts exposed as buttons, and more.

---

## Compatible controllers

### Unfolded Circle Remote 3

Virtual Remotes is a native fit — UC reads the `commands` state attribute to auto-discover
available commands, then you map them to physical buttons in the UC integration.

### Astrion Remote (via [RosCard](https://github.com/yyqclhy/RosCard))

The [Astrion Remote](https://github.com/yyqclhy/RosCard) runs a Home Assistant Lovelace dashboard directly on the remote's screen. [RosCard](https://github.com/yyqclhy/RosCard) is the card collection that powers it, calling HA services from card button actions. To use a Virtual Remote with RosCard, configure each button action in your RosCard card to call `remote.send_command`:

```yaml
type: custom:ros-tv-card
entity: media_player.living_room_tv
power_on:
  service: remote.send_command
  target:
    entity_id: remote.blu_ray_player
  data:
    command: Power
up:
  service: remote.send_command
  target:
    entity_id: remote.blu_ray_player
  data:
    command: Up
select:
  service: remote.send_command
  target:
    entity_id: remote.blu_ray_player
  data:
    command: Select
```

Check the `commands` state attribute on your virtual remote entity (Developer Tools → States)
to see the exact command names to use in your RosCard configuration.

---

## License

MIT
