"""Tests for plugsim.parser"""
import pytest
from pathlib import Path

from plugsim.parser import parse_metadata, validate_compatibility


VALID_WORLD = """\
schema_version: "1.0"
plugin_type: world
name: example_factory_world
version: 1.0.0
description: "Test world"
compatibility:
  isaac_sim: ">=5.0.0"
  ros_distro: jazzy
entry_point:
  usd: assets/scene.usd
  app: app.py
"""

VALID_ROBOT = """\
schema_version: "1.0"
plugin_type: robot
name: example_melon_ros2
version: 1.0.0
description: "Test robot"
compatibility:
  isaac_sim: ">=5.0.0"
  ros_distro: jazzy
entry_point:
  usd: assets/robot.usd
  launch: melon_ws/src/bringup/launch/robot.launch.py
"""


def make_dir(tmp_path, content, name="plugin"):
    d = tmp_path / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "METADATA.yaml").write_text(content, encoding="utf-8")
    return d


# --- parse_metadata ---

def test_parse_world(tmp_path):
    m = parse_metadata(make_dir(tmp_path, VALID_WORLD))
    assert m.name == "example_factory_world"
    assert m.plugin_type == "world"
    assert m.entry_point.app == "app.py"
    assert m.entry_point.usd == "assets/scene.usd"
    assert m.ros_distro == "jazzy"


def test_parse_robot(tmp_path):
    m = parse_metadata(make_dir(tmp_path, VALID_ROBOT))
    assert m.plugin_type == "robot"
    assert m.entry_point.launch.endswith(".launch.py")


def test_missing_metadata(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    with pytest.raises(FileNotFoundError):
        parse_metadata(d)


def test_invalid_plugin_type(tmp_path):
    bad = VALID_WORLD.replace("plugin_type: world", "plugin_type: spaceship")
    with pytest.raises(ValueError, match="plugin_type"):
        parse_metadata(make_dir(tmp_path, bad))


def test_not_a_mapping(tmp_path):
    with pytest.raises(ValueError):
        parse_metadata(make_dir(tmp_path, "- list item\n"))


# --- validate_compatibility ---

def test_compatible_plugins(tmp_path):
    w = parse_metadata(make_dir(tmp_path, VALID_WORLD, "world"))
    r = parse_metadata(make_dir(tmp_path, VALID_ROBOT, "robot"))
    assert validate_compatibility([w, r]) == []


def test_ros_distro_mismatch(tmp_path):
    humble = VALID_ROBOT.replace("ros_distro: jazzy", "ros_distro: humble")
    w = parse_metadata(make_dir(tmp_path, VALID_WORLD, "world"))
    r = parse_metadata(make_dir(tmp_path, humble, "robot"))
    errors = validate_compatibility([w, r])
    assert any("mismatch" in e.lower() for e in errors)


def test_missing_dep_plugin(tmp_path):
    app_yaml = """\
schema_version: "1.0"
plugin_type: app
name: my_app
version: 1.0.0
compatibility:
  ros_distro: jazzy
entry_point:
  app: app.py
dependencies:
  plugins:
    - missing_plugin
"""
    m = parse_metadata(make_dir(tmp_path, app_yaml))
    errors = validate_compatibility([m])
    assert any("missing_plugin" in e for e in errors)


def test_empty_list():
    assert validate_compatibility([]) == []
