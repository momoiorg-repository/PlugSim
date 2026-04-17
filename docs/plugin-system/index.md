---
title: Plugin System
nav_order: 4
has_children: true
---

# Plugin System

PlugSim discovers and manages plugins stored in the `plugin/` directory. A plugin is any folder that contains a `METADATA.yaml` file.

---

## Directory layout

```
plugin/
├── example_factory_world/
│   ├── METADATA.yaml        ← required
│   ├── app.py               ← Isaac Sim standalone script
│   └── assets/              ← USD files (separate git repo)
│       └── factory_base.usd
└── example_melon_ros2/
    ├── METADATA.yaml        ← required
    ├── melon_ws/            ← ROS 2 workspace
    └── assets/              ← robot USD files (separate git repo)
        └── melon.usd
```

{: .highlight }
> There are no `robot/` or `world/` subdirectories. All plugins live directly under `plugin/`. The plugin type is declared inside `METADATA.yaml`.

---

## Supported plugin types

| Type | Purpose |
|------|---------|
| `world` | Isaac Sim environment / scene |
| `robot` | Robot definition with USD and ROS 2 launch |
| `logic` | Standalone application or behaviour |
| `app` | Generic Isaac Sim app |

---

## How discovery works

On every `plugsim scan`, `plugsim validate`, `plugsim up`, or `plugsim exec` call, PlugSim:

1. Lists every direct child directory of `plugin/`
2. Keeps only those that contain `METADATA.yaml`
3. Parses each `METADATA.yaml` into a `PluginMetadata` object
4. Returns them sorted alphabetically by directory name

Plugins that fail to parse are skipped with a warning — they do not block other plugins.

---

## In this section

- [METADATA.yaml Schema]({% link plugin-system/metadata-schema.md %}) — full field reference
- [Adding a Plugin]({% link plugin-system/adding-a-plugin.md %}) — manual and scaffold-based approaches
