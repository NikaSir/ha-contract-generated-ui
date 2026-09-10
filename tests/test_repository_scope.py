from __future__ import annotations

import json
import struct
from pathlib import Path


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "custom_components" / "contract_generated_ui"


def test_release_is_common_registry_service() -> None:
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.40.2"
    assert manifest["dependencies"] == ["http"]
    assert "after_dependencies" not in manifest

    assert list((ROOT / "contracts").glob("*.yaml")) == []
    assert list((ROOT / "manifests").glob("*.yaml")) == []
    assert not (PACKAGE / "bundled_sources" / "contracts").exists()
    assert not (PACKAGE / "bundled_sources" / "manifests").exists()
    assert not (PACKAGE / "frontend").exists()


def test_no_panel_implementation_is_packaged() -> None:
    retired_modules = {
        "house_base.py",
        "house_navigation.py",
        "house_panel.py",
        "render.py",
        "runtime_dispatch.py",
        "runtime_house.py",
        "runtime_registration.py",
        "runtime_render_dispatch.py",
        "runtime_renderer.py",
    }
    assert not retired_modules.intersection(path.name for path in PACKAGE.glob("*.py"))
    assert not (ROOT / "generator" / "house_base.py").exists()
    assert not (ROOT / "generator" / "render_house.py").exists()
    assert not (ROOT / "generator" / "render_dispatch.py").exists()
    assert not (ROOT / "scripts" / "build_frontend_bundles.sh").exists()

    init = (PACKAGE / "__init__.py").read_text(encoding="utf-8")
    assert "async_register_static_paths" not in init
    assert "add_extra_js_url" not in init
    assert "panel_custom" not in init
    assert "async_register_house_panel" not in init


def test_common_renderer_has_no_panel_dispatch_dependency() -> None:
    cli = (ROOT / "generator" / "cli.py").read_text(encoding="utf-8")
    assert "from .render import RenderError" in cli
    assert "render_dispatch" not in cli


def test_registry_service_brand_icon_is_packaged() -> None:
    data = (PACKAGE / "brand" / "icon.png").read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert struct.unpack(">II", data[16:24]) == (256, 256)


def test_archive_and_repository_boundary_are_documented() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    scope = (ROOT / "docs" / "REPOSITORY_SCOPE.md").read_text(encoding="utf-8")
    assert "archive/multipanel-0.37.8" in readme
    assert "c525b30" in readme
    assert "owns no runtime dashboard" in scope
    assert "must never clean user-owned" in scope
