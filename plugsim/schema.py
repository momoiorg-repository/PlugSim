"""Plugin metadata schema (stdlib dataclasses — no external deps beyond pyyaml)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

VALID_PLUGIN_TYPES = {"world", "robot", "logic", "app"}


@dataclass
class EntryPoint:
    usd: Optional[str] = None     # USD scene file (relative to plugin dir)
    app: Optional[str] = None     # Isaac Sim standalone Python script
    launch: Optional[str] = None  # ROS 2 .launch.py file
    config: Optional[str] = None  # Parameter file


@dataclass
class PluginMetadata:
    name: str
    plugin_type: str
    version: str
    description: str = ""
    isaac_sim: Optional[str] = None   # e.g. ">=5.0.0"
    ros_distro: Optional[str] = None  # e.g. "jazzy"
    entry_point: EntryPoint = field(default_factory=EntryPoint)
    dep_plugins: List[str] = field(default_factory=list)
    author: str = ""
    license: str = ""
    repository: str = ""
