from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


def run(operation, **options):
    result = subprocess.run(
        ["node", "tests/device_availability_panel_harness.mjs"],
        cwd=ROOT, input=json.dumps({"operation": operation, **options}),
        text=True, capture_output=True, check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("parent", ["/home/overview", None, "", "https://external.test/", "//external.test", "/dashboard-device-availability"])
def test_real_header_clicks_dispatch_menu_and_return_to_overview(parent):
    result = run("header_actions", parent=parent)
    assert result["menu"] == [{"type": "hass-toggle-menu", "bubbles": True, "composed": True}]
    assert result["paths"] == ["/home/overview"]
    assert result["events"] == ["location-changed"]


@pytest.mark.parametrize("mode", ["failure", "false", "no_entities"])
def test_refresh_failure_waits_for_minimum_and_never_becomes_success(mode):
    assert run("refresh_failure", mode=mode) == {
        "sleeps": [900], "rejected": True, "settledBeforeMinimum": False,
    }
