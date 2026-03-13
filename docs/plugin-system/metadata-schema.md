---
title: METADATA.yaml Schema
parent: Plugin System
nav_order: 1
---

# METADATA.yaml Schema
{: .no_toc }

<details open markdown="block">
  <summary>Table of contents</summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Full example

```yaml
schema_version: "1.0"
plugin_type: world          # world | robot | logic | app
name: my_plugin
version: 1.0.0
description: "Short description shown in plugsim scan"

compatibility:
  isaac_sim: ">=5.0.0"
  ros_distro: jazzy

entry_point:
  usd: assets/scene.usd                  # USD scene file
  app: app.py                            # Isaac Sim standalone Python script
  launch: launch/my_plugin.launch.py    # ROS 2 launch file (.launch.py)
  config: config/params.yaml            # optional parameter file

dep_plugins:
  - example_factory_world               # other PlugSim plugin names required

author: "Your Name"
license: MIT
repository: "https://github.com/your-org/my_plugin"
```

---

## Field reference

### Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | No | Schema version, currently `"1.0"` |
| `plugin_type` | string | **Yes** | One of `world`, `robot`, `logic`, `app` |
| `name` | string | **Yes** | Plugin identifier — must be unique across all plugins |
| `version` | string | No | Semantic version string (defaults to `"0.0.0"`) |
| `description` | string | No | Short human-readable description |
| `author` | string | No | Author name |
| `license` | string | No | License identifier (e.g. `MIT`) |
| `repository` | string | No | URL to the plugin's source repository |

---

### `compatibility`

Declares runtime requirements. Both fields are optional but recommended.

| Field | Type | Description |
|-------|------|-------------|
| `isaac_sim` | string | Version constraint, e.g. `">=5.0.0"` |
| `ros_distro` | string | ROS 2 distro name, e.g. `jazzy` |

{: .warning }
> `plugsim validate` requires all plugins to declare the **same** `ros_distro`. Mismatches are reported as errors.

---

### `entry_point`

Declares how the plugin is executed. All sub-fields are optional, but at least one of `app` or `launch` is needed for `plugsim exec` to work.

| Field | Type | Description |
|-------|------|-------------|
| `usd` | string | Path to USD scene file, relative to `METADATA.yaml` |
| `app` | string | Path to Isaac Sim standalone Python script, relative to `METADATA.yaml` |
| `launch` | string | Path to ROS 2 `.launch.py` file, relative to `METADATA.yaml` |
| `config` | string | Path to a parameter/config file, relative to `METADATA.yaml` |

**Dispatch precedence:** `plugsim exec` prefers `app` over `launch`. If `app` is set, the plugin runs as:

```
python /plugin/<name>/<app>
```

If only `launch` is set:

```
ros2 launch /plugin/<name>/<launch>
```

All paths are relative to the plugin's own directory and are translated to absolute container paths at runtime (`/plugin/<name>/...`).

---

### `dep_plugins`

List of other PlugSim plugin **names** this plugin depends on.

```yaml
dep_plugins:
  - example_factory_world
```

`plugsim validate` checks that every listed name exists among the discovered plugins.

---

## Minimal valid example

For a plugin that only provides a USD asset with no executable entry point:

```yaml
plugin_type: world
name: my_world
```

For a plugin that runs an Isaac Sim script:

```yaml
plugin_type: app
name: my_app
entry_point:
  app: main.py
```
