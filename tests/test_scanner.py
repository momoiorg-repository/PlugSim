"""Tests for plugsim.scanner"""
from pathlib import Path
from plugsim.scanner import scan_plugins


def _make(tmp_path: Path, name: str, with_meta: bool = True) -> Path:
    d = tmp_path / name
    d.mkdir(parents=True)
    if with_meta:
        (d / "METADATA.yaml").write_text("name: stub\n")
    return d


def test_discovers_plugins_with_metadata(tmp_path):
    _make(tmp_path, "plugin_a")
    _make(tmp_path, "plugin_b")
    names = {p.name for p in scan_plugins(tmp_path)}
    assert {"plugin_a", "plugin_b"} == names


def test_ignores_dirs_without_metadata(tmp_path):
    _make(tmp_path, "good")
    _make(tmp_path, "bad", with_meta=False)
    names = {p.name for p in scan_plugins(tmp_path)}
    assert "bad" not in names


def test_empty_base(tmp_path):
    assert scan_plugins(tmp_path) == []


def test_nonexistent_base(tmp_path):
    assert scan_plugins(tmp_path / "nope") == []


def test_result_is_sorted(tmp_path):
    for n in ["zzz", "aaa", "mmm"]:
        _make(tmp_path, n)
    names = [p.name for p in scan_plugins(tmp_path)]
    assert names == sorted(names)
