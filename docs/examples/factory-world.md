---
title: example_factory_world
parent: Examples
nav_order: 1
---

# example\_factory\_world
{: .no_toc }

<details open markdown="block">
  <summary>Table of contents</summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Overview

`example_factory_world` is a `world`-type plugin that loads a factory floor environment in NVIDIA Isaac Sim using a standalone Python script. It places a robot (Melon) in the scene and serves as the base environment for factory simulation tasks.

| Field | Value |
|-------|-------|
| Plugin type | `world` |
| Entry point | `app.py` (Isaac Sim standalone) |
| USD scene | `assets/factory_base.usd` |
| Assets repo | [factory_world1](https://github.com/momoiorg-repository/factory_world1) |

---

## Prerequisites

Clone the asset repository:

```bash
git clone https://github.com/momoiorg-repository/factory_world1.git \
    plugin/example_factory_world/assets
```

---

## METADATA.yaml

```yaml
plugin_type: world
name: example_factory_world
version: 1.0.0
description: "Isaac Sim factory environment"
compatibility:
  isaac_sim: ">=5.0.0"
  ros_distro: jazzy
entry_point:
  usd: assets/factory_base.usd
  app: app.py
```

---

## Running

```bash
plugsim up
plugsim exec example_factory_world
```

The script opens Isaac Sim and loads `factory_base.usd`. The robot USD (`melon.usd` from `example_melon_ros2`) is referenced at `/plugin/example_melon_ros2/assets/melon.usd` inside the container.

{: .note }
> For the robot to appear correctly, `example_melon_ros2` assets must also be cloned. See [example_melon_ros2]({% link examples/melon-ros2.md %}).

---

## app.py

`app.py` is an Isaac Sim standalone Python script. Key paths it uses inside the container:

```python
usd_path       = "/plugin/example_factory_world/assets/factory_base.usd"
robot_usd_path = "/plugin/example_melon_ros2/assets/melon.usd"
```

These paths are fixed container-side paths, matched by the volume mounts configured in `plugsim up`.

---

## Directory structure

```
plugin/example_factory_world/
├── METADATA.yaml
├── app.py
└── assets/            ← cloned from factory_world1
    └── factory_base.usd
```
