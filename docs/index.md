---
title: Home
layout: home
nav_order: 1
permalink: /
description: "PlugSim — METADATA.yaml-driven plugin orchestrator for NVIDIA Isaac Sim + ROS 2 Jazzy"
---

# PlugSim

**METADATA.yaml-driven plugin orchestrator for NVIDIA Isaac Sim + ROS 2 Jazzy**

PlugSim lets you drop a folder into `plugin/`, describe it with a `METADATA.yaml`, and run it inside a pre-built Isaac Sim container — all from a single CLI.

---

## What it does

{: .highlight }
> One command to start the container. One command to run a plugin. No Docker flags to memorise.

| Concern | How PlugSim handles it |
|---------|------------------------|
| Plugin discovery | Scans `plugin/*/METADATA.yaml` automatically |
| Compatibility | Checks ROS distro and inter-plugin dependencies before launch |
| Container lifecycle | `plugsim up` / `plugsim down` with correct NVIDIA GPU mounts |
| Plugin execution | `plugsim exec <name>` dispatches to `python app.py` or `ros2 launch` |
| Setup | `plugsim setup` builds the Docker image and creates cache dirs |

---

## Quick look

```bash
pip install -e .
plugsim setup                        # build image, create cache dirs
plugsim up                           # start container
plugsim exec example_factory_world  # run a plugin
plugsim shell                        # open a shell inside the container
```

---

## Navigation

- [Getting Started]({% link getting-started.md %}) — requirements, installation, first run
- [CLI Reference]({% link cli-reference.md %}) — all `plugsim` commands
- [Plugin System]({% link plugin-system/index.md %}) — directory layout, METADATA.yaml schema, adding plugins
- [Examples]({% link examples/index.md %}) — walkthrough of the bundled example plugins
- [Container]({% link container.md %}) — container management and Isaac Sim inside
