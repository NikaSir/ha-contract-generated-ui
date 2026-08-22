from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from generator.app_shell import (
    append_app_shell,
    manifest_app_shell_active,
    manifest_app_shell_config,
)

ROOT = Path(__file__).parents[1]


def _dashboard() -> dict:
    return {
        "views": [
            {
                "title": "Test",
                "path": "overview",
                "type": "sections",
                "max_columns": 2,
                "sections": [
                    {
                        "type": "grid",
                        "cards": [{"type": "heading", "heading": "Content"}],
                    }
                ],
            }
        ]
    }


def _spacer_card(rendered: dict) -> dict:
    return rendered["views"][0]["sections"][-1]["cards"][0]


def test_app_shell_uses_only_native_bottom_clearance_in_lovelace() -> None:
    source = _dashboard()
    rendered = append_app_shell(source, active="infrastructure")

    assert len(source["views"][0]["sections"]) == 1
    sections = rendered["views"][0]["sections"]
    assert len(sections) == 2
    card = _spacer_card(rendered)
    assert card == {
        "type": "markdown",
        "content": "<br><br><br>",
        "text_only": True,
        "grid_options": {"columns": "full"},
    }
    assert "custom:" not in str(rendered)


def test_app_shell_route_overrides_remain_validated_without_custom_card() -> None:
    rendered = append_app_shell(
        _dashboard(),
        active="home",
        routes={
            "home": "/dashboard-house-preview/home",
            "actions": "/dashboard-actions-preview/home",
        },
    )
    assert _spacer_card(rendered)["type"] == "markdown"


def test_app_shell_manifest_contract_is_explicit() -> None:
    manifest = {
        "spec": {
            "app_shell": {
                "active": "home",
                "routes": {
                    "home": "/dashboard-house-preview/home",
                    "actions": "/dashboard-actions-preview/home",
                },
            }
        }
    }
    assert manifest_app_shell_active(manifest) == "home"
    assert manifest_app_shell_config(manifest) == (
        "home",
        {
            "home": "/dashboard-house-preview/home",
            "actions": "/dashboard-actions-preview/home",
        },
    )
    assert manifest_app_shell_active({"spec": {}}) is None
    with pytest.raises(ValueError):
        manifest_app_shell_active({"spec": {"app_shell": {"active": "other"}}})
    with pytest.raises(ValueError):
        manifest_app_shell_config(
            {"spec": {"app_shell": {"active": "home", "routes": {"other": "/x"}}}}
        )
    with pytest.raises(ValueError):
        manifest_app_shell_config(
            {"spec": {"app_shell": {"active": "home", "routes": {"home": "relative"}}}}
        )


def test_runtime_and_generator_app_shell_sources_are_byte_equivalent() -> None:
    generator_source = (ROOT / "generator" / "app_shell.py").read_text(encoding="utf-8")
    runtime_source = (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "runtime_app_shell.py"
    ).read_text(encoding="utf-8")
    assert generator_source == runtime_source


def test_infrastructure_v012_uses_central_power_subviews() -> None:
    manifest_path = ROOT / "manifests" / "infrastructure.yaml"
    bundled_path = (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "bundled_sources"
        / "manifests"
        / "infrastructure.yaml"
    )
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert manifest["metadata"]["version"] == "0.12.0"
    assert manifest["spec"]["app_shell"] == {"active": "infrastructure"}
    assert [view["id"] for view in manifest["spec"]["views"]] == [
        "overview",
        "power-overview",
        "power-before",
        "power-after",
        "power-history",
    ]
    assert all(
        view["renderer"] == "infrastructure_summary_v1"
        for view in manifest["spec"]["views"]
    )
    assert bundled_path.read_bytes() == manifest_path.read_bytes()


def test_nikas_ui_bundle_switches_to_local_power_navigation() -> None:
    asset = (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "frontend"
        / "nikas-ui.js"
    ).read_text(encoding="utf-8")
    assert 'const BAR_ID = "nikas-global-tabbar"' in asset
    assert "position: fixed" in asset
    assert "env(safe-area-inset-bottom" in asset
    assert 'window.addEventListener("location-changed"' in asset
    assert 'pathname.startsWith("/dashboard-infrastructure")' in asset
    assert "const POWER_ITEMS" in asset
    assert 'label: "Обзор"' in asset
    assert 'label: "До стаб."' in asset
    assert 'label: "После стаб."' in asset
    assert 'label: "История"' in asset
    assert 'path: "/dashboard-infrastructure/power-overview"' in asset
    assert 'path: "/dashboard-infrastructure/power-before"' in asset
    assert 'path: "/dashboard-infrastructure/power-after"' in asset
    assert 'path: "/dashboard-infrastructure/power-history"' in asset
    assert "--nikas-nav-columns" in asset
