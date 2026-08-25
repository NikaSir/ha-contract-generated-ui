from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from custom_components.contract_generated_ui.generated_panels import (
    build_generated_panel_specs,
    strip_standalone_navigation_groups,
)
from generator.subpanel_shell import (
    apply_navigation_shell,
    compile_navigation_registry,
    navigation_shell_engine_sha256,
)

ROOT = Path(__file__).parents[1]
INTEGRATION = ROOT / "custom_components" / "contract_generated_ui"


def _sections_dashboard(view_count: int) -> dict:
    return {
        "views": [
            {
                "title": f"Tab {index}",
                "path": f"tab-{index}",
                "type": "sections",
                "max_columns": 1,
                "sections": [
                    {
                        "type": "grid",
                        "cards": [
                            {"type": "markdown", "content": f"placeholder {index}"}
                        ],
                    }
                ],
            }
            for index in range(view_count)
        ]
    }


def _standalone_manifest(panel_id: str = "example") -> dict:
    return {
        "api_version": "nikas.home-assistant/panel-manifest/v1",
        "kind": "PanelManifest",
        "metadata": {
            "id": panel_id,
            "title": "Example",
            "version": "1.0.0",
            "description": "Generic standalone subpanel test.",
        },
        "spec": {
            "dashboard_path": f"/dashboard-{panel_id}",
            "subpanel": {
                "template": "standard_v1",
                "navigation": "main",
                "parent": "house.heating",
                "source": {
                    "kind": "entity_registry",
                    "platforms": ["example"],
                    "include_disabled": False,
                },
            },
            "views": [
                {
                    "id": "overview",
                    "title": "Обзор",
                    "icon": "mdi:view-dashboard-outline",
                    "path": "overview",
                    "order": 0,
                    "renderer": "subpanel_placeholder_v1",
                    "placeholder": "Example overview.",
                    "readonly": {"domains": ["sensor"], "limit": 20},
                    "modules": [],
                },
                {
                    "id": "diagnostics",
                    "title": "Диагностика",
                    "icon": "mdi:heart-pulse",
                    "path": "diagnostics",
                    "order": 1,
                    "renderer": "subpanel_placeholder_v1",
                    "placeholder": "Example diagnostics.",
                    "readonly": {"domains": ["sensor"], "limit": 20},
                    "modules": [],
                },
            ],
        },
    }


def _source_tree(tmp_path: Path, manifest: dict) -> Path:
    source = tmp_path / "source"
    (source / "manifests").mkdir(parents=True)
    (source / "navigation").mkdir()
    (source / "manifests" / "example.yaml").write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    shutil.copy2(ROOT / "navigation" / "main.yaml", source / "navigation" / "main.yaml")
    return source


def test_zont_is_fully_handed_off_to_its_dedicated_integration() -> None:
    frontend = INTEGRATION / "frontend"
    assert not (ROOT / "manifests" / "zont.yaml").exists()
    assert not (INTEGRATION / "bundled_sources" / "manifests" / "zont.yaml").exists()
    assert not (frontend / "nikas-generated-zont.js").exists()
    assert not (frontend / "assets" / "zont-boiler-casing-v0812.webp").exists()
    assert not (frontend / "assets" / "zont-dhw-shell-v0812.webp").exists()

    constants = (INTEGRATION / "const.py").read_text(encoding="utf-8")
    setup = (INTEGRATION / "__init__.py").read_text(encoding="utf-8")
    panels = (INTEGRATION / "generated_panels.py").read_text(encoding="utf-8")
    shell = (frontend / "nikas-specialized-panel-shell.js").read_text(encoding="utf-8")
    zoom = (frontend / "nikas-panel-zoom.js").read_text(encoding="utf-8")
    assert "GENERATED_ZONT" not in constants
    assert "GENERATED_ZONT" not in setup
    assert "ZONT_WEB_COMPONENT_NAME" not in panels
    assert '"nikas-generated-zont"' not in shell
    assert '"NIKAS-GENERATED-ZONT"' not in zoom


def test_stale_zont_manifest_cannot_register_a_panel(tmp_path: Path) -> None:
    manifest = _standalone_manifest("zont")
    source = _source_tree(tmp_path, manifest)
    assert build_generated_panel_specs(source) == []


def test_generic_standalone_subpanel_remains_supported(tmp_path: Path) -> None:
    manifest = _standalone_manifest()
    source = _source_tree(tmp_path, manifest)
    dashboard = _sections_dashboard(len(manifest["spec"]["views"]))
    rendered, groups = apply_navigation_shell(dashboard, manifest, source)

    assert len(groups) == 1
    group = groups[0]
    assert group["id"] == "example"
    assert group["parent"]["path"] == "/dashboard-house/heating"
    assert group["embedded"] is False
    assert [tab["path"] for tab in group["tabs"]] == [
        "/dashboard-example/overview",
        "/dashboard-example/diagnostics",
    ]
    assert [view["path"] for view in rendered["views"]] == [
        "overview",
        "diagnostics",
    ]
    assert navigation_shell_engine_sha256("0" * 64, groups) != "0" * 64

    specs = build_generated_panel_specs(source)
    assert len(specs) == 1
    assert specs[0]["id"] == "example"
    assert specs[0]["webcomponent_name"] == "nikas-generated-subpanel"
    assert specs[0]["module_url"].startswith(
        "/contract_generated_ui/frontend/nikas-generated-subpanel.js"
    )


def test_global_navigation_overlay_drops_standalone_groups(tmp_path: Path) -> None:
    registry = compile_navigation_registry(ROOT)
    registry["subpanels"].append({"id": "example", "embedded": False})
    path = tmp_path / "navigation.json"
    path.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    assert strip_standalone_navigation_groups(path) is True
    filtered = json.loads(path.read_text(encoding="utf-8"))
    groups = {group["id"]: group for group in filtered["subpanels"]}
    assert "power" in groups
    assert groups["power"]["embedded"] is True
    assert "example" not in groups
    assert "zont" not in groups
    assert "starline" not in groups


def test_generator_and_runtime_subpanel_sources_are_byte_equivalent() -> None:
    assert (ROOT / "generator" / "subpanel_shell.py").read_bytes() == (
        INTEGRATION / "runtime_subpanel_shell.py"
    ).read_bytes()
    assert (ROOT / "generator" / "render_subpanel_placeholder.py").read_bytes() == (
        INTEGRATION / "runtime_render_subpanel_placeholder.py"
    ).read_bytes()


def test_navigation_contract_is_packaged_without_zont_manifest() -> None:
    assert (ROOT / "navigation" / "main.yaml").read_bytes() == (
        INTEGRATION / "bundled_sources" / "navigation" / "main.yaml"
    ).read_bytes()
    assert not (ROOT / "manifests" / "zont.yaml").exists()
    assert not (INTEGRATION / "bundled_sources" / "manifests" / "zont.yaml").exists()
    assert not (INTEGRATION / "bundled_sources" / "manifests" / "starline.yaml").exists()
