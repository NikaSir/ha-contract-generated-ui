"""Snapshot acquisition must not fetch arbitrary hosts or overwrite checkouts."""

import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/checkout_nikas_contract_snapshots.py"
SPEC = importlib.util.spec_from_file_location("contract_checkout", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def profile(root, name="NikaSir/ha-test", revision="a" * 40, filename="one.json"):
    root.mkdir(exist_ok=True)
    (root / filename).write_text(json.dumps({"repository": name, "source_revision": revision}))


@pytest.mark.parametrize("name", ["NikaSir/../../escape", "Other/repo", "NikaSir/--upload-pack=x", "NikaSir/foo/bar"])
def test_rejects_untrusted_repository(tmp_path, name):
    profile(tmp_path, name)
    with pytest.raises(ValueError):
        MODULE.read_targets(tmp_path)


def test_rejects_floating_revision(tmp_path):
    profile(tmp_path, revision="main")
    with pytest.raises(ValueError):
        MODULE.read_targets(tmp_path)


def test_rejects_nonobject_before_downloading(tmp_path):
    (tmp_path / "invalid.json").write_text("[]")
    with patch.object(MODULE.subprocess, "run") as run:
        with pytest.raises(ValueError, match="Expected a profile object"):
            MODULE.checkout(tmp_path, tmp_path / "snapshots")
        run.assert_not_called()


def test_accepts_defaults_repository(tmp_path):
    profile(tmp_path, name="NikaSir/.github")
    assert MODULE.read_targets(tmp_path) == [("NikaSir/.github", "a" * 40)]


def test_rejects_duplicate_before_downloading(tmp_path):
    profile(tmp_path)
    profile(tmp_path, filename="two.json")
    with patch.object(MODULE.subprocess, "run") as run:
        with pytest.raises(ValueError):
            MODULE.checkout(tmp_path, tmp_path / "snapshots")
        run.assert_not_called()


def test_never_overwrites_existing_checkout(tmp_path):
    registry = tmp_path / "profiles"
    profile(registry)
    existing = tmp_path / "snapshots/ha-test"
    existing.mkdir(parents=True)
    keep = existing / "user-work.txt"
    keep.write_text("keep")
    with patch.object(MODULE.subprocess, "run") as run:
        with pytest.raises(ValueError):
            MODULE.checkout(registry, existing.parent)
        run.assert_not_called()
    assert keep.read_text() == "keep"
