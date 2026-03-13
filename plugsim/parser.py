"""METADATA.yaml parser and compatibility checker."""
from __future__ import annotations

from pathlib import Path
from typing import List

import yaml

from .schema import EntryPoint, PluginMetadata, VALID_PLUGIN_TYPES


def parse_metadata(plugin_path: Path) -> PluginMetadata:
    """Parse and validate METADATA.yaml in *plugin_path*."""
    meta_file = plugin_path / "METADATA.yaml"
    if not meta_file.exists():
        raise FileNotFoundError(f"METADATA.yaml not found in {plugin_path}")

    raw = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"METADATA.yaml in {plugin_path} must be a YAML mapping")

    plugin_type = raw.get("plugin_type", "")
    if plugin_type not in VALID_PLUGIN_TYPES:
        raise ValueError(
            f"plugin_type must be one of {sorted(VALID_PLUGIN_TYPES)}, got '{plugin_type}'"
        )

    compat = raw.get("compatibility") or {}
    ep_raw = raw.get("entry_point") or {}

    return PluginMetadata(
        name=raw["name"],
        plugin_type=plugin_type,
        version=str(raw.get("version", "1.0.0")),
        description=raw.get("description", ""),
        isaac_sim=compat.get("isaac_sim") if isinstance(compat, dict) else None,
        ros_distro=compat.get("ros_distro") if isinstance(compat, dict) else None,
        entry_point=EntryPoint(
            usd=ep_raw.get("usd"),
            app=ep_raw.get("app"),
            launch=ep_raw.get("launch"),
            config=ep_raw.get("config"),
        ),
        dep_plugins=(raw.get("dependencies") or {}).get("plugins", []),
        author=raw.get("author", ""),
        license=raw.get("license", ""),
        repository=raw.get("repository", ""),
    )


def validate_compatibility(plugins: List[PluginMetadata]) -> List[str]:
    """Return list of compatibility error strings (empty = all OK)."""
    errors: List[str] = []
    if not plugins:
        return errors

    # All loaded plugins must agree on ROS distro
    distros = {p.name: p.ros_distro for p in plugins if p.ros_distro}
    if len(set(distros.values())) > 1:
        errors.append(
            "ROS distro mismatch: "
            + ", ".join(f"{n}={d}" for n, d in distros.items())
        )

    # Every declared plugin dependency must be present
    loaded = {p.name for p in plugins}
    for plugin in plugins:
        for dep in plugin.dep_plugins:
            dep_name = dep.split(">=")[0].split("==")[0].split("<=")[0].strip()
            if dep_name not in loaded:
                errors.append(
                    f"'{plugin.name}' depends on '{dep_name}' which is not loaded"
                )

    return errors
