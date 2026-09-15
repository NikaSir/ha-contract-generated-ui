"""Supplemental release-metadata checks; DOM behavior is tested in Chromium."""
from pathlib import Path
import ast

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "custom_components" / "contract_generated_ui"


def constants():
    tree = ast.parse((PACKAGE / "const.py").read_text())
    return {
        node.targets[0].id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Constant)
    }


def test_beta004_version_and_loading_key():
    panel = (PACKAGE / "frontend/device-availability-panel.js").read_text()
    assert 'UI_VERSION = "1.0.0-beta004"' in panel
    assert constants()["DEVICE_AVAILABILITY_PANEL_BUILD"] == "b004"


def test_validation_attribute_keeps_its_public_name():
    assert constants()["ATTR_VALIDATION_LEVEL"] == "validation_level"
    assert constants()["VALIDATION_LEVEL"] == "contract_core_v1"
