# PlugSim

**PlugSim** is a METADATA.yaml-driven plugin orchestration platform for NVIDIA Isaac Sim + ROS 2 robotics simulation.

Drop a plugin folder into `plugin/`, add a `METADATA.yaml`, and PlugSim handles discovery, compatibility checking, and container lifecycle — all from a single CLI.

---

## Requirements

### Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | NVIDIA RTX 3060 | RTX 3080 or higher |
| RAM | 16 GB | 32 GB |
| Storage | 50 GB free | 100 GB free |

### Software

- Ubuntu 24.04 LTS
- Docker (latest)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- NVIDIA driver 535.x or higher
- Python 3.10+

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/momoiorg-repository/plugsim.git
cd plugsim
```

### 2. Clone plugin assets (USD files)

Plugin `assets/` directories are separate git repositories and are not included here. Clone them into the appropriate plugin folders:

```bash
git clone https://github.com/momoiorg-repository/factory_world1.git \
    plugin/example_factory_world/assets

git clone https://github.com/momoiorg-repository/melon_ros2.git \
    plugin/example_melon_ros2
```

### 3. Install the PlugSim CLI

```bash
pip install -e .
```

### 4. Run setup

`plugsim setup` creates the Isaac Sim cache directories, builds the Docker image (~10–20 min on first run), and sets script permissions.

```bash
plugsim setup
```

> You will be prompted before rebuilding if the image already exists.

### 5. Set your display (X11 forwarding)

```bash
export DISPLAY=<your-local-ip>:0
# e.g.: export DISPLAY=192.168.1.10:0
```

### 6. Start the container and run a plugin

```bash
plugsim up
plugsim exec example_factory_world
```

---

## PlugSim CLI Reference

| Command | Description |
|---------|-------------|
| `plugsim setup` | Build the Docker image and initialise Isaac Sim storage dirs |
| `plugsim scan` | List all discovered plugins with version and compatibility info |
| `plugsim validate` | Check cross-plugin compatibility (ROS distro, deps) |
| `plugsim up` | Start the simulation container |
| `plugsim down` | Stop and remove the container |
| `plugsim shell` | Open an interactive bash shell inside the running container |
| `plugsim exec <name> [args]` | Run a plugin's entry point inside the container |
| `plugsim info <name>` | Show full details for a specific plugin |
| `plugsim init` | Interactively scaffold a new plugin directory with `METADATA.yaml` |

### Examples

```bash
# See what plugins are loaded
plugsim scan

# Check compatibility before launching
plugsim validate

# Start the container
plugsim up

# Open a shell inside the container
plugsim shell

# Run example plugins
plugsim exec example_factory_world
plugsim exec example_melon_ros2

# Inspect a specific plugin
plugsim info example_factory_world

# Scaffold a new plugin
plugsim init
```

---

## Plugin System

### Directory layout

```
plugin/
├── example_factory_world/
│   ├── METADATA.yaml     ← required
│   ├── app.py
│   └── assets/
└── example_melon_ros2/
    ├── METADATA.yaml     ← required
    └── assets/
```

All plugins live directly under `plugin/`. There are no `robot/` or `world/` subdirectories — the plugin type is declared inside `METADATA.yaml`.

Supported plugin types: `world`, `robot`, `logic`, `app`

### METADATA.yaml schema

```yaml
schema_version: "1.0"
plugin_type: world          # world | robot | logic | app
name: my_plugin
version: 1.0.0
description: "Short description"

compatibility:
  isaac_sim: ">=5.0.0"
  ros_distro: jazzy

entry_point:
  usd: assets/scene.usd                  # USD scene file (relative to METADATA.yaml)
  app: app.py                            # Isaac Sim standalone Python script
  launch: launch/my_plugin.launch.py    # ROS 2 launch file
  config: config/params.yaml            # optional parameter file

dep_plugins: []     # other PlugSim plugin names required

author: "Your Name"
license: MIT
repository: "https://github.com/..."
```

**Entry point precedence:** `app` is executed with `python`; `launch` is executed with `ros2 launch`. Only one is used per `plugsim exec` call.

### Adding a plugin

**Option A — manually:**
1. Create `plugin/<name>/METADATA.yaml`
2. Run `plugsim scan` to verify it is detected

**Option B — scaffold:**
```bash
plugsim init
# follow the prompts
```

---

## Container Management

```bash
plugsim up       # start container
plugsim shell    # open interactive bash shell
plugsim down     # stop and remove container

docker ps        # check container status
```

The container is named **`plugsim-jazzy`** and uses image **`plugsim:jazzy`**.

All plugins are mounted read-write at `/plugin` inside the container.

---

## Running Isaac Sim inside the container

```bash
# Connect first
plugsim shell

# GUI mode
cd /isaac-sim && ./isaac-sim.sh

# Headless / livestream mode
cd /isaac-sim && ./runheadless.sh
```

---

## Running tests

```bash
bash run_tests.sh -v
```

Tests cover the core orchestration modules (`scanner`, `parser`). ROS 2 pytest plugins are automatically excluded to avoid Python 3.13 conflicts.

---

## Repository Structure

```
plugsim/
├── plugsim/                      # Orchestration library (pip package)
│   ├── __init__.py
│   ├── schema.py                 # METADATA.yaml dataclasses
│   ├── scanner.py                # Plugin discovery
│   ├── parser.py                 # YAML parsing + compatibility checks
│   ├── launcher.py               # Container lifecycle (up/down/exec/setup)
│   └── cli.py                    # CLI entry point
├── plugin/                       # Plugins directory
│   ├── example_factory_world/    # Factory environment example
│   │   ├── METADATA.yaml
│   │   ├── app.py
│   │   └── assets/
│   └── example_melon_ros2/       # Melon robot ROS 2 example
│       ├── METADATA.yaml
│       └── assets/
├── tests/                        # Unit tests
├── IsaacSim-ros_workspaces/      # ROS 2 workspaces (Jazzy)
├── Dockerfile                    # Isaac Lab 2.3.0 + ROS 2 Jazzy image
├── pyproject.toml                # Package definition + CLI entry point
└── run_tests.sh                  # Test runner
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
