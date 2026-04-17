"""PlugSim CLI entry point."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PLUGIN_BASE = WORKSPACE / "plugin"


def _load(parse_metadata, scan_plugins):
    """Discover and parse all plugins. Returns (metadata_list, dir_list)."""
    dirs = scan_plugins(PLUGIN_BASE)
    if not dirs:
        print("[INFO] No plugins found in", PLUGIN_BASE)
        return [], []
    plugins, valid_dirs = [], []
    for d in dirs:
        try:
            plugins.append(parse_metadata(d))
            valid_dirs.append(d)
        except Exception as exc:
            print(f"[WARN] Skipping {d.name}: {exc}")
    return plugins, valid_dirs


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_scan(_args):
    from plugsim.scanner import scan_plugins
    from plugsim.parser import parse_metadata
    plugins, dirs = _load(parse_metadata, scan_plugins)
    if not plugins:
        return
    print(f"\nDiscovered {len(plugins)} plugin(s):\n")
    for m, d in zip(plugins, dirs):
        ros = m.ros_distro or "—"
        isaac = m.isaac_sim or "—"
        ep = []
        if m.entry_point.app:    ep.append(f"app:{m.entry_point.app}")
        if m.entry_point.launch: ep.append(f"launch:{m.entry_point.launch}")
        if m.entry_point.usd:    ep.append(f"usd:{m.entry_point.usd}")
        print(
            f"  [{m.plugin_type:6}]  {m.name:<35} v{m.version:<8} "
            f"ros:{ros}  isaac:{isaac}"
        )
        if ep:
            print(f"             entry: {' | '.join(ep)}")
    print()


def cmd_validate(_args):
    from plugsim.scanner import scan_plugins
    from plugsim.parser import parse_metadata, validate_compatibility
    plugins, _ = _load(parse_metadata, scan_plugins)
    errors = validate_compatibility(plugins)
    if errors:
        print(f"\n[FAIL] {len(errors)} compatibility issue(s):\n")
        for e in errors:
            print(f"  x  {e}")
        sys.exit(1)
    print(f"\n[OK]  All {len(plugins)} plugin(s) are compatible.\n")


def cmd_up(_args):
    from plugsim.scanner import scan_plugins
    from plugsim.parser import parse_metadata, validate_compatibility
    from plugsim.launcher import up
    plugins, _ = _load(parse_metadata, scan_plugins)
    errors = validate_compatibility(plugins)
    if errors:
        print("[FAIL] Compatibility check failed — run 'plugsim validate' for details.")
        sys.exit(1)
    print(f"\nStarting container with {len(plugins)} plugin(s) at /plugin ...\n")
    up(WORKSPACE, PLUGIN_BASE)
    print("\n[OK]  Container is up.\n")


def cmd_down(_args):
    from plugsim.launcher import down
    print("\nStopping container...")
    down()
    print("\n[OK]  Container stopped.\n")


def cmd_shell(_args):
    from plugsim.launcher import shell
    shell()


def cmd_exec(args):
    from plugsim.scanner import scan_plugins
    from plugsim.parser import parse_metadata
    from plugsim.launcher import exec_plugin
    plugins, dirs = _load(parse_metadata, scan_plugins)
    for meta, d in zip(plugins, dirs):
        if meta.name == args.plugin:
            exec_plugin(d, meta, args.args or [])
            return
    print(f"[ERROR] Plugin '{args.plugin}' not found.")
    sys.exit(1)


def cmd_info(args):
    from plugsim.scanner import scan_plugins
    from plugsim.parser import parse_metadata
    plugins, dirs = _load(parse_metadata, scan_plugins)
    for m, d in zip(plugins, dirs):
        if m.name == args.plugin:
            print(f"\n{'='*52}")
            print(f"  {m.name}  (v{m.version})")
            print(f"{'='*52}")
            print(f"  Type        : {m.plugin_type}")
            print(f"  Description : {m.description}")
            print(f"  Author      : {m.author or '—'}")
            print(f"  License     : {m.license or '—'}")
            print(f"  Repository  : {m.repository or '—'}")
            print(f"\n  Compatibility")
            print(f"    Isaac Sim : {m.isaac_sim or '—'}")
            print(f"    ROS distro: {m.ros_distro or '—'}")
            print(f"\n  Entry Points")
            print(f"    USD    : {m.entry_point.usd or '—'}")
            print(f"    App    : {m.entry_point.app or '—'}")
            print(f"    Launch : {m.entry_point.launch or '—'}")
            print(f"    Config : {m.entry_point.config or '—'}")
            if m.dep_plugins:
                print(f"\n  Depends on  : {', '.join(m.dep_plugins)}")
            print(f"\n  Directory   : {d}\n")
            return
    print(f"[ERROR] Plugin '{args.plugin}' not found.")
    sys.exit(1)


def cmd_setup(_args):
    from plugsim.launcher import setup
    setup(WORKSPACE)


def cmd_init(_args):
    """Interactive scaffold for a new plugin."""
    print("\n=== New Plugin Scaffold ===\n")
    plugin_type = input("Plugin type [world/robot/logic/app]: ").strip()
    if plugin_type not in {"world", "robot", "logic", "app"}:
        print("[ERROR] Invalid plugin type.")
        sys.exit(1)
    name = input("Plugin name: ").strip()
    if not name:
        print("[ERROR] Name cannot be empty.")
        sys.exit(1)
    version = input("Version [1.0.0]: ").strip() or "1.0.0"
    description = input("Description: ").strip()
    ros_distro = input("ROS distro [jazzy]: ").strip() or "jazzy"
    isaac_sim = input("Isaac Sim constraint [>=5.0.0]: ").strip() or ">=5.0.0"

    target = PLUGIN_BASE / name
    if target.exists():
        print(f"[ERROR] {target} already exists.")
        sys.exit(1)

    (target / "assets").mkdir(parents=True)

    (target / "METADATA.yaml").write_text(
        f'schema_version: "1.0"\n'
        f"plugin_type: {plugin_type}\n"
        f"name: {name}\n"
        f"version: {version}\n"
        f'description: "{description}"\n'
        f"compatibility:\n"
        f'  isaac_sim: "{isaac_sim}"\n'
        f"  ros_distro: {ros_distro}\n"
        f"entry_point:\n"
        f"  usd: null\n"
        f"  app: null\n"
        f"  launch: null\n"
        f"author: \"\"\n"
        f"license: MIT\n"
        f'repository: ""\n',
        encoding="utf-8",
    )
    (target / "README.md").write_text(f"# {name}\n\n{description}\n", encoding="utf-8")

    print(f"\n[OK]  Plugin scaffold created at {target}")
    print("      Edit METADATA.yaml and add your USD / app / launch files.\n")


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="PlugSim — METADATA.yaml-driven plugin orchestrator for Isaac Sim + ROS 2",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup",    help="Build Docker image and initialise storage dirs")
    sub.add_parser("scan",     help="List discovered plugins")
    sub.add_parser("validate", help="Check plugin compatibility")
    sub.add_parser("up",       help="Start simulation container")
    sub.add_parser("down",     help="Stop simulation container")
    sub.add_parser("shell",    help="Open a bash shell inside the running container")
    sub.add_parser("init",     help="Scaffold a new plugin interactively")

    p_exec = sub.add_parser("exec", help="Run a plugin's entry point in the container")
    p_exec.add_argument("plugin", help="Plugin name")
    p_exec.add_argument("args", nargs=argparse.REMAINDER,
                        help="Extra args forwarded to the app/launch")

    p_info = sub.add_parser("info", help="Show details for a plugin")
    p_info.add_argument("plugin", help="Plugin name")

    args = parser.parse_args()
    {
        "setup":    cmd_setup,
        "scan":     cmd_scan,
        "validate": cmd_validate,
        "up":       cmd_up,
        "down":     cmd_down,
        "shell":    cmd_shell,
        "exec":     cmd_exec,
        "info":     cmd_info,
        "init":     cmd_init,
    }[args.command](args)


if __name__ == "__main__":
    main()
