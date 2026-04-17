---
title: example_melon_ros2
parent: Examples
nav_order: 2
---

# example\_melon\_ros2
{: .no_toc }

<details open markdown="block">
  <summary>Table of contents</summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Overview

`example_melon_ros2` is a `robot`-type plugin for the **Melon mobile manipulator**. It provides the robot's USD model and a ROS 2 bringup launch file. When executed via `plugsim exec`, it starts the full ROS 2 stack for Melon inside the container.

| Field | Value |
|-------|-------|
| Plugin type | `robot` |
| Entry point | `ros2 launch` |
| Launch file | `melon_ws/src/melon_bringup/launch/melon_bringup.launch.py` |
| USD model | `assets/melon.usd` |
| Plugin repo | [melon_ros2](https://github.com/momoiorg-repository/melon_ros2) |

---

## Prerequisites

Clone the plugin repository (which includes the ROS 2 workspace and assets):

```bash
git clone https://github.com/momoiorg-repository/melon_ros2.git \
    plugin/example_melon_ros2
```

{: .note }
> The entire `example_melon_ros2` directory is its own git repository. It is gitignored in the PlugSim root repo and must be cloned separately.

---

## METADATA.yaml

```yaml
plugin_type: robot
name: example_melon_ros2
version: 1.0.0
description: "Melon mobile manipulator ROS 2 plugin"
compatibility:
  isaac_sim: ">=5.0.0"
  ros_distro: jazzy
entry_point:
  usd: assets/melon.usd
  launch: melon_ws/src/melon_bringup/launch/melon_bringup.launch.py
```

---

## Running

```bash
plugsim up
plugsim exec example_melon_ros2
```

This runs inside the container:

```bash
ros2 launch /plugin/example_melon_ros2/melon_ws/src/melon_bringup/launch/melon_bringup.launch.py
```

---

## Running with the factory world

To load Melon into the factory environment, run the factory world plugin — it references Melon's USD automatically:

```bash
plugsim exec example_factory_world
```

In a separate terminal, optionally also bring up the ROS 2 stack:

```bash
plugsim exec example_melon_ros2
```

---

## ROS 2 workspace

The `melon_ws/` ROS 2 workspace inside the plugin directory is pre-built and mounted into the container at `/plugin/example_melon_ros2/`. The container's ROS 2 installation at `/opt/ros/jazzy` is sourced automatically.

---

## Directory structure

```
plugin/example_melon_ros2/      ← cloned from melon_ros2
├── METADATA.yaml
├── melon_ws/
│   └── src/
│       └── melon_bringup/
│           └── launch/
│               └── melon_bringup.launch.py
└── assets/
    └── melon.usd
```
