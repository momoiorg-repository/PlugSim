---
title: CLI Reference
nav_order: 3
---

# CLI Reference
{: .no_toc }

<details open markdown="block">
  <summary>Table of contents</summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

All commands are issued from the repository root after running `pip install -e .`.

```
plugsim <command> [options]
```

---

## setup

Build the Docker image and initialise Isaac Sim storage directories.

```bash
plugsim setup
```

**What it does, step by step:**

1. Creates `isaac-sim/` subdirectories (`cache/kit`, `cache/ov`, `cache/pip`, `cache/glcache`, `cache/computecache`, `logs`, `data`, `documents`, `config`) so Docker does not create them as root-owned.
2. Verifies `Dockerfile` is present in the repository root.
3. Builds (or offers to rebuild) the image `plugsim:jazzy`.
4. Marks `run_tests.sh` executable.
5. Prints next-step usage.

{: .note }
> Run this once after cloning. Re-run after modifying the `Dockerfile`.

---

## scan

List all discovered plugins.

```bash
plugsim scan
```

Scans every direct child of `plugin/` that contains a `METADATA.yaml` file. Prints name, version, plugin type, ROS distro, Isaac Sim constraint, and entry points.

**Example output:**

```
Discovered 2 plugin(s):

  [world ]  example_factory_world               v1.0.0   ros:jazzy  isaac:>=5.0.0
             entry: app:app.py | usd:assets/factory_base.usd
  [robot ]  example_melon_ros2                  v1.0.0   ros:jazzy  isaac:>=5.0.0
             entry: launch:melon_ws/src/melon_bringup/launch/melon_bringup.launch.py
```

---

## validate

Check cross-plugin compatibility.

```bash
plugsim validate
```

Runs two checks:

| Check | Description |
|-------|-------------|
| ROS distro consistency | All plugins must declare the same `ros_distro` |
| Dependency resolution | Every plugin listed in `dep_plugins` must be present |

Exits with code `1` if any check fails.

---

## up

Start the simulation container.

```bash
plugsim up
```

Runs `docker run` with:
- NVIDIA GPU pass-through (`--runtime=nvidia --gpus all`)
- `--network host`, `--ipc=host`, `--pid=host`
- All plugins mounted at `/plugin:rw`
- Isaac Sim cache and data directories mounted
- X11 display forwarding
- ROS 2 environment variables (`ROS_DOMAIN_ID=31`, `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`, `FASTDDS_BUILTIN_TRANSPORTS=UDPv4`)

The container runs `tail -f /dev/null` as its entrypoint and stays alive in the background.

{: .warning }
> `plugsim up` runs a compatibility check first. If `plugsim validate` would fail, the container will not start.

---

## down

Stop and remove the container.

```bash
plugsim down
```

Calls `docker stop` then `docker rm`. Isaac Sim cache data in `./isaac-sim/` is preserved on disk.

---

## shell

Open an interactive bash shell inside the running container.

```bash
plugsim shell
```

Equivalent to `docker exec -it plugsim-jazzy /bin/bash`. Type `exit` to leave — the container keeps running.

---

## exec

Run a plugin's entry point inside the container.

```bash
plugsim exec <plugin-name> [extra args...]
```

**Dispatch rules:**

| `entry_point` field set | Command run inside container |
|-------------------------|------------------------------|
| `app` | `python /plugin/<name>/<app>` |
| `launch` | `ros2 launch /plugin/<name>/<launch>` |

Extra arguments are forwarded verbatim to the app or launch file.

**Examples:**

```bash
plugsim exec example_factory_world
plugsim exec example_factory_world --headless
plugsim exec example_melon_ros2
```

{: .note }
> The container must be running (`plugsim up`) before calling `exec`.

---

## info

Show full details for a single plugin.

```bash
plugsim info <plugin-name>
```

**Example output:**

```
====================================================
  example_factory_world  (v1.0.0)
====================================================
  Type        : world
  Description : Isaac Sim factory environment
  Author      : —
  License     : MIT
  Repository  : —

  Compatibility
    Isaac Sim : >=5.0.0
    ROS distro: jazzy

  Entry Points
    USD    : assets/factory_base.usd
    App    : app.py
    Launch : —
    Config : —

  Directory   : /path/to/plugin/example_factory_world
```

---

## init

Interactively scaffold a new plugin directory.

```bash
plugsim init
```

Prompts for plugin type, name, version, description, ROS distro, and Isaac Sim constraint, then creates:

```
plugin/<name>/
├── METADATA.yaml
├── README.md
└── assets/
```

---

## Container and image names

| Item | Value |
|------|-------|
| Container name | `plugsim-jazzy` |
| Docker image | `plugsim:jazzy` |
| Plugin mount inside container | `/plugin` |
