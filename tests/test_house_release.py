from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "custom_components" / "contract_generated_ui"


def test_release_is_house_only() -> None:
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.38.1"
    assert set(manifest["dependencies"]) == {"frontend", "http"}
    assert manifest["after_dependencies"] == ["lovelace"]

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


def test_setup_registers_only_house_panel() -> None:
    init = (PACKAGE / "__init__.py").read_text(encoding="utf-8")
    constants = (PACKAGE / "const.py").read_text(encoding="utf-8")
    assert "async_register_house_panel" in init
    assert "async_register_infrastructure_panel" not in init
    assert "async_register_generated_subpanels" not in init
    assert "async_register_rooms_panel" not in init
    assert "INFRASTRUCTURE_PANEL" not in constants
    assert "ROOMS_PANEL" not in constants
    assert "GENERATED_SUBPANEL" not in constants


def test_archive_and_repository_boundary_are_documented() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    scope = (ROOT / "docs" / "REPOSITORY_SCOPE.md").read_text(encoding="utf-8")
    assert "archive/multipanel-0.37.8" in readme
    assert "c525b30" in readme
    assert "owns only the new main **Дом** overview" in scope
    assert "must never unload or replace a route" in scope
