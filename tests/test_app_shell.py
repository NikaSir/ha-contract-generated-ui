from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from generator.app_shell import APP_SHELL_ITEMS, append_app_shell, manifest_app_shell_active

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


def test_app_shell_is_full_width_fixed_navigation_placeholder() -> None:
    source = _dashboard()
    rendered = append_app_shell(source, active="infrastructure")

    assert len(source["views"][0]["sections"]) == 1
    sections = rendered["views"][0]["sections"]
    assert len(sections) == 2
    card = sections[-1]["cards"][0]
    assert card["type"] == "custom:nikas-app-shell"
    assert card["active"] == "infrastructure"
    assert card["grid_options"] == {"columns": "full"}
    assert tuple(item["id"] for item in card["items"]) == (
        "home",
        "actions",
        "infrastructure",
    )
    assert tuple(item["path"] for item in card["items"]) == tuple(
        item["path"] for item in APP_SHELL_ITEMS
    )


def test_app_shell_manifest_contract_is_explicit() -> None:
    manifest = {"spec": {"app_shell": {"active": "home"}}}
    assert manifest_app_shell_active(manifest) == "home"
    assert manifest_app_shell_active({"spec": {}}) is None
    with pytest.raises(ValueError):
        manifest_app_shell_active({"spec": {"app_shell": {"active": "other"}}})


def test_runtime_and_generator_app_shell_sources_are_byte_equivalent() -> None:
    generator_source = (ROOT / "generator" / "app_shell.py").read_text(encoding="utf-8")
    runtime_source = (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "runtime_app_shell.py"
    ).read_text(encoding="utf-8")
    assert generator_source == runtime_source


def test_infrastructure_v07_uses_single_view_app_shell() -> None:
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

    assert manifest["metadata"]["version"] == "0.7.0"
    assert manifest["spec"]["app_shell"] == {"active": "infrastructure"}
    assert [view["id"] for view in manifest["spec"]["views"]] == ["overview"]
    assert bundled_path.read_bytes() == manifest_path.read_bytes()


def test_app_shell_frontend_asset_is_packaged() -> None:
    asset = (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "frontend"
        / "nikas-app-shell.js"
    ).read_text(encoding="utf-8")
    assert 'customElements.define("nikas-app-shell"' in asset
    assert "position: fixed" in asset
    assert "env(safe-area-inset-bottom" in asset
    assert 'window.dispatchEvent(new Event("location-changed"))' in asset
