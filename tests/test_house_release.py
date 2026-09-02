from __future__ import annotations

import json
import struct
from pathlib import Path


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "custom_components" / "contract_generated_ui"


def test_release_is_registry_service() -> None:
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.39.0"
    assert manifest["dependencies"] == ["http"]
    assert "after_dependencies" not in manifest

    assert sorted(path.name for path in (ROOT / "contracts").glob("*.yaml")) == [
        "house_home.yaml"
    ]
    assert sorted(path.name for path in (ROOT / "manifests").glob("*.yaml")) == [
        "house_v11_preview.yaml"
    ]
    assert sorted(
        path.name
        for path in (PACKAGE / "bundled_sources" / "contracts").glob("*.yaml")
    ) == ["house_home.yaml"]
    assert sorted(
        path.name
        for path in (PACKAGE / "bundled_sources" / "manifests").glob("*.yaml")
    ) == ["house_v11_preview.yaml"]


def test_only_house_frontend_is_packaged() -> None:
    frontend = PACKAGE / "frontend"
    assert sorted(path.name for path in frontend.glob("*.js")) == [
        "nikas-house-hero.js",
        "nikas-house-overview.js",
        "nikas-ui.js",
    ]
    assert sorted(path.name for path in (frontend / "dist").glob("*.js")) == [
        "nikas-house-overview.js"
    ]
    assert sorted(path.name for path in (frontend / "assets").iterdir()) == [
        "house-hero-photo-day-v3.webp"
    ]
    packaged = (frontend / "dist" / "nikas-house-overview.js").read_text(
        encoding="utf-8"
    )
    assert not any(line.lstrip().startswith("import ") for line in packaged.splitlines())


def test_global_frontend_does_not_modify_legacy_yaml_dashboards() -> None:
    bundle = (PACKAGE / "frontend" / "nikas-ui.js").read_text(encoding="utf-8")
    assert "NikasPanelNavigation" in bundle
    assert "history.pushState" in bundle
    assert "location-changed" in bundle
    assert "MutationObserver" not in bundle
    assert "querySelector" not in bundle
    assert "createElement" not in bundle
    assert "appendChild" not in bundle
    assert "innerHTML" not in bundle
    assert 'return "/dashboard-house-v12/home"' in bundle


def test_setup_registers_no_dashboard_or_global_frontend() -> None:
    init = (PACKAGE / "__init__.py").read_text(encoding="utf-8")
    button = (PACKAGE / "button.py").read_text(encoding="utf-8")
    assert "async_register_house_panel" not in init
    assert "add_extra_js_url" not in init
    assert "panel_custom" not in init
    assert "ContractGeneratedUIGenerateDashboardsButton" not in button
    assert "render_all_manifests" not in button


def test_registry_service_brand_icon_is_packaged() -> None:
    icon = PACKAGE / "brand" / "icon.png"
    data = icon.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert struct.unpack(">II", data[16:24]) == (256, 256)


def test_archive_and_repository_boundary_are_documented() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    scope = (ROOT / "docs" / "REPOSITORY_SCOPE.md").read_text(encoding="utf-8")
    assert "archive/multipanel-0.37.8" in readme
    assert "c525b30" in readme
    assert "owns no runtime dashboard" in scope
    assert "must never clean private inventory" in scope
