"""Container lifecycle and plugin execution."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import List, Optional

from .schema import PluginMetadata

CONTAINER_NAME = "plugsim-jazzy"
IMAGE_TAG = "plugsim:jazzy"
PLUGIN_MOUNT = "/plugin"

_ISAAC_SIM_CACHE_DIRS = [
    "cache/kit",
    "cache/ov",
    "cache/pip",
    "cache/glcache",
    "cache/computecache",
    "logs",
    "data",
    "documents",
    "config",
]


def _run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"  [RUN]  {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def _ensure_isaac_dirs(isaac_sim: Path) -> None:
    """Create Isaac Sim cache/data directories if they don't exist.

    Docker creates missing mount targets as root-owned dirs, which causes
    permission errors inside the container. Pre-creating them here avoids that.
    """
    for sub in _ISAAC_SIM_CACHE_DIRS:
        (isaac_sim / sub).mkdir(parents=True, exist_ok=True)


def is_running() -> bool:
    """Return True if the PlugSim container is currently running."""
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True, text=True,
    )
    return CONTAINER_NAME in result.stdout.splitlines()


def up(workspace: Path, plugin_base: Path) -> None:
    """Start the PlugSim container with all plugins mounted at /plugin."""
    if is_running():
        print(f"[INFO] Container '{CONTAINER_NAME}' is already running.")
        return

    isaac_sim = workspace / "isaac-sim"
    ros_ws = workspace / "IsaacSim-ros_workspaces"

    _ensure_isaac_dirs(isaac_sim)

    cmd = [
        "docker", "run", "--name", CONTAINER_NAME, "-d",
        "--runtime=nvidia", "--gpus", "all",
        "--network", "host",
        "--ipc=host",
        "--pid=host",
        "-e", "ACCEPT_EULA=Y",
        "-e", "PRIVACY_CONSENT=Y",
        "-e", "FASTDDS_BUILTIN_TRANSPORTS=UDPv4",
        "-e", f"DISPLAY={os.environ.get('DISPLAY', ':0')}",
        "-e", "QT_X11_NO_MITSHM=1",
        "-e", "QT_GRAPHICSSYSTEM=native",
        "-e", "QT_QPA_PLATFORM=xcb",
        "-e", "RMW_IMPLEMENTATION=rmw_fastrtps_cpp",
        "-e", "ROS_DOMAIN_ID=31",
        # All plugins at a single, flat mount point
        "-v", f"{plugin_base.resolve()}:{PLUGIN_MOUNT}:rw",
        # ROS workspaces (built packages)
        "-v", f"{ros_ws.resolve()}:/IsaacSim-ros_workspaces:rw",
        # Isaac Sim persistent cache / data
        "-v", f"{(isaac_sim / 'cache/kit').resolve()}:/isaac-sim/kit/cache:rw",
        "-v", f"{(isaac_sim / 'cache/ov').resolve()}:/root/.cache/ov:rw",
        "-v", f"{(isaac_sim / 'cache/pip').resolve()}:/root/.cache/pip:rw",
        "-v", f"{(isaac_sim / 'cache/glcache').resolve()}:/root/.cache/nvidia/GLCache:rw",
        "-v", f"{(isaac_sim / 'cache/computecache').resolve()}:/root/.nv/ComputeCache:rw",
        "-v", f"{(isaac_sim / 'logs').resolve()}:/root/.nvidia-omniverse/logs:rw",
        "-v", f"{(isaac_sim / 'data').resolve()}:/root/.local/share/ov/data:rw",
        "-v", f"{(isaac_sim / 'documents').resolve()}:/root/isaac-sim/Documents:rw",
        # X11 display
        "-v", "/tmp/.X11-unix:/tmp/.X11-unix:rw",
        "-v", f"{Path.home() / '.Xauthority'}:/root/.Xauthority:ro",
        "--entrypoint", "/bin/bash",
        IMAGE_TAG,
        "-c", "tail -f /dev/null",
    ]
    _run(cmd)


def down() -> None:
    """Stop and remove the PlugSim container."""
    _run(["docker", "stop", CONTAINER_NAME], check=False)
    _run(["docker", "rm",   CONTAINER_NAME], check=False)


def shell() -> None:
    """Open an interactive bash shell inside the running container."""
    if not is_running():
        print(
            f"[ERROR] Container '{CONTAINER_NAME}' is not running. "
            "Run 'plugsim up' first."
        )
        return
    _run(["docker", "exec", "-it", CONTAINER_NAME, "/bin/bash"], check=False)


def setup(workspace: Path) -> None:
    """Bootstrap: create cache dirs, build Docker image, set permissions, show usage."""
    # Step 1: persistent storage dirs
    _ensure_isaac_dirs(workspace / "isaac-sim")
    print("[INFO] Storage directories ready.")

    # Step 2: Dockerfile required
    if not (workspace / "Dockerfile").exists():
        print(f"[ERROR] Dockerfile not found in {workspace}")
        return

    # Step 3: Docker image
    existing = subprocess.run(
        ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
        capture_output=True, text=True,
    ).stdout.splitlines()
    if IMAGE_TAG in existing:
        ans = input(f"[INFO] Image '{IMAGE_TAG}' already exists. Rebuild? (y/N): ").strip()
        if ans.lower() != "y":
            print("[INFO] Skipping build.")
        else:
            _run(["docker", "build", "-t", IMAGE_TAG, str(workspace)])
    else:
        print(f"[INFO] Building '{IMAGE_TAG}' (10-20 min on first run)...")
        _run(["docker", "build", "-t", IMAGE_TAG, str(workspace)])

    # Step 4: script permissions
    for name in ["run_tests.sh"]:
        p = workspace / name
        if p.exists():
            p.chmod(p.stat().st_mode | 0o111)
    print("[INFO] Script permissions set.")

    # Step 5: usage
    print(
        "\n=========================================="
        "\nSetup complete. Next steps:"
        "\n=========================================="
        "\n"
        "\n1. Start the container:"
        "\n   plugsim up"
        "\n"
        "\n2. Run an example plugin:"
        "\n   plugsim exec example_factory_world"
        "\n   plugsim exec example_melon_ros2"
        "\n"
        "\n3. List all plugins:"
        "\n   plugsim scan"
        "\n=========================================="
    )


def exec_plugin(
    plugin_dir: Path,
    meta: PluginMetadata,
    extra_args: Optional[List[str]] = None,
) -> None:
    """Run a plugin's entry point inside the running container."""
    if not is_running():
        print(
            f"[ERROR] Container '{CONTAINER_NAME}' is not running. "
            "Run 'plugsim up' first."
        )
        return

    container_dir = f"{PLUGIN_MOUNT}/{plugin_dir.name}"
    ep = meta.entry_point

    if ep.app:
        cmd = [
            "docker", "exec", "-it", CONTAINER_NAME,
            "python", f"{container_dir}/{ep.app}",
        ]
    elif ep.launch:
        cmd = [
            "docker", "exec", "-it", CONTAINER_NAME,
            "ros2", "launch", f"{container_dir}/{ep.launch}",
        ]
    else:
        print(
            f"[ERROR] Plugin '{meta.name}' has no runnable entry point. "
            "Set entry_point.app or entry_point.launch in METADATA.yaml."
        )
        return

    if extra_args:
        cmd.extend(extra_args)

    _run(cmd, check=False)
