---
title: Container
nav_order: 6
---

# Container
{: .no_toc }

<details open markdown="block">
  <summary>Table of contents</summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Container details

| Property | Value |
|----------|-------|
| Container name | `plugsim-jazzy` |
| Docker image | `plugsim:jazzy` |
| Base | Isaac Lab 2.3.0 + ROS 2 Jazzy |
| Plugin mount | `./plugin` → `/plugin` (read-write) |
| ROS workspaces mount | `./IsaacSim-ros_workspaces` → `/IsaacSim-ros_workspaces` |
| ROS domain ID | `31` |
| RMW implementation | `rmw_fastrtps_cpp` |

---

## Lifecycle commands

```bash
plugsim up       # start container in background
plugsim down     # stop and remove container
plugsim shell    # open interactive bash shell
docker ps        # check running containers
```

{: .note }
> `plugsim down` removes the container. The Isaac Sim cache and data in `./isaac-sim/` are preserved on disk and reused on the next `plugsim up`.

---

## Volume mounts

| Host path | Container path | Purpose |
|-----------|----------------|---------|
| `./plugin` | `/plugin` | All plugins |
| `./IsaacSim-ros_workspaces` | `/IsaacSim-ros_workspaces` | ROS 2 workspaces |
| `./isaac-sim/cache/kit` | `/isaac-sim/kit/cache` | Kit cache |
| `./isaac-sim/cache/ov` | `/root/.cache/ov` | Omniverse cache |
| `./isaac-sim/cache/pip` | `/root/.cache/pip` | pip cache |
| `./isaac-sim/cache/glcache` | `/root/.cache/nvidia/GLCache` | OpenGL cache |
| `./isaac-sim/cache/computecache` | `/root/.nv/ComputeCache` | CUDA compute cache |
| `./isaac-sim/logs` | `/root/.nvidia-omniverse/logs` | Omniverse logs |
| `./isaac-sim/data` | `/root/.local/share/ov/data` | Omniverse data |
| `./isaac-sim/documents` | `/root/isaac-sim/Documents` | Isaac Sim documents |
| `/tmp/.X11-unix` | `/tmp/.X11-unix` | X11 display socket |
| `~/.Xauthority` | `/root/.Xauthority` | X11 auth |

---

## Environment variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `ACCEPT_EULA` | `Y` | NVIDIA EULA acceptance |
| `PRIVACY_CONSENT` | `Y` | NVIDIA privacy consent |
| `FASTDDS_BUILTIN_TRANSPORTS` | `UDPv4` | Fast-DDS transport |
| `RMW_IMPLEMENTATION` | `rmw_fastrtps_cpp` | ROS 2 middleware |
| `ROS_DOMAIN_ID` | `31` | ROS 2 domain isolation |
| `DISPLAY` | from host `$DISPLAY` | X11 display forwarding |
| `QT_X11_NO_MITSHM` | `1` | Qt X11 compatibility |
| `QT_QPA_PLATFORM` | `xcb` | Qt platform plugin |

---

## Running Isaac Sim inside the container

Open a shell first:

```bash
plugsim shell
```

Then from inside the container:

```bash
# GUI mode
cd /isaac-sim && ./isaac-sim.sh

# Headless / livestream mode
cd /isaac-sim && ./runheadless.sh
```

---

## Building the image

The Docker image is built automatically by `plugsim setup`. To rebuild manually:

```bash
docker build -t plugsim:jazzy .
```

The `Dockerfile` is based on the official NVIDIA Isaac Lab 2.3.0 image and adds ROS 2 Jazzy.

---

## Troubleshooting

### Container exits immediately

Check that the NVIDIA Container Toolkit is installed and the driver version meets the minimum requirement (535.x+):

```bash
nvidia-smi
docker run --rm --runtime=nvidia --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### X11 display errors

Make sure `DISPLAY` is set and `xhost` allows the container:

```bash
export DISPLAY=<your-ip>:0
xhost +local:docker
plugsim up
```

### Permission errors in isaac-sim/ directories

Run `plugsim setup` again to recreate the directories with correct permissions. Docker creates missing mount targets as root-owned dirs if they don't exist beforehand.
