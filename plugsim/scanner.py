"""Plugin scanner — finds all plugin directories containing METADATA.yaml."""
from __future__ import annotations

from pathlib import Path
from typing import List


def scan_plugins(plugin_base: Path) -> List[Path]:
    """Return sorted list of plugin dirs (each must contain METADATA.yaml)."""
    if not plugin_base.is_dir():
        return []
    return sorted(
        d for d in plugin_base.iterdir()
        if d.is_dir() and (d / "METADATA.yaml").exists()
    )
