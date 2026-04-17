---
title: Getting Started
nav_order: 2
---

# Getting Started
{: .no_toc }

<details open markdown="block">
  <summary>Table of contents</summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Requirements

### Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | NVIDIA RTX 3060 | RTX 3080 or higher |
| RAM | 16 GB | 32 GB |
| Storage | 50 GB free | 100 GB free |

### Software

| Requirement | Notes |
|-------------|-------|
| Ubuntu 24.04 LTS | Other distros untested |
| Docker (latest) | |
| [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) | Required for GPU pass-through |
| NVIDIA driver 535.x or higher | |
| Python 3.10+ | For the host-side CLI only |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/momoiorg-repository/plugsim.git
cd plugsim
```

### 2. Clone plugin assets

Plugin `assets/` directories are separate git repositories. Clone them into the correct locations:

```bash
git clone https://github.com/momoiorg-repository/factory_world1.git \
    plugin/example_factory_world/assets

git clone https://github.com/momoiorg-repository/melon_ros2.git \
    plugin/example_melon_ros2/assets
```

{: .note }
> The `assets/` directories contain large USD files and are not bundled in this repository.

### 3. Install the PlugSim CLI

```bash
pip install -e .
```

This installs the `plugsim` command on your host system. It has a single runtime dependency: `pyyaml`.

### 4. Run setup

```bash
plugsim setup
```

This command:
1. Creates `isaac-sim/` persistent cache and data directories
2. Checks that `Dockerfile` is present
3. Builds the Docker image `plugsim:jazzy` (~10–20 min on first run)
4. Sets permissions on `run_tests.sh`

{: .tip }
> If the image already exists you will be asked whether to rebuild. Press `N` to skip.

### 5. Set your display

PlugSim uses X11 forwarding for GUI output:

```bash
export DISPLAY=<your-local-ip>:0
# e.g.: export DISPLAY=192.168.1.10:0
```

---

## First run

```bash
plugsim up                           # start container in background
plugsim exec example_factory_world  # run the factory world plugin
```

Verify everything is working:

```bash
plugsim scan      # list discovered plugins
plugsim validate  # check compatibility
docker ps         # confirm container is running
```

To open a shell inside the container:

```bash
plugsim shell
```
