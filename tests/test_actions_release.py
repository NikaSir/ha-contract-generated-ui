from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_release_version_and_schema_are_packaged() -> None:
    manifest = json.loads((ROOT / "custom_components" / "contract_generated_ui" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.36.14"
    assert set(manifest["dependencies"]) == {"frontend", "http"}
    assert manifest["after_dependencies"] == ["lovelace"]

    repo_schema = json.loads((ROOT / "schemas" / "manifest.schema.json").read_text(encoding="utf-8"))
    packaged_schema = json.loads((ROOT / "custom_components" / "contract_generated_ui" / "schemas" / "manifest.schema.json").read_text(encoding="utf-8"))
    assert repo_schema == packaged_schema
    enum_values = repo_schema["$defs"]["view"]["properties"]["renderer"]["enum"]
    assert "actions_home_v1" in enum_values
    assert "infrastructure_summary_v1" in enum_values
    assert "subpanel_placeholder_v1" in enum_values
    assert "subpanel" in repo_schema["properties"]["spec"]["properties"]

    navigation_schema = json.loads((ROOT / "schemas" / "navigation.schema.json").read_text(encoding="utf-8"))
    packaged_navigation_schema = json.loads((ROOT / "custom_components" / "contract_generated_ui" / "schemas" / "navigation.schema.json").read_text(encoding="utf-8"))
    assert navigation_schema == packaged_navigation_schema

    registry_schema = json.loads((ROOT / "schemas" / "registry-snapshot.schema.json").read_text(encoding="utf-8"))
    packaged_registry_schema = json.loads((ROOT / "custom_components" / "contract_generated_ui" / "schemas" / "registry-snapshot.schema.json").read_text(encoding="utf-8"))
    assert registry_schema == packaged_registry_schema


def test_brand_assets_are_valid_pngs() -> None:
    for filename in ("icon.png", "logo.png"):
        payload = (ROOT / "custom_components" / "contract_generated_ui" / "brand" / filename).read_bytes()
        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
        width, height = struct.unpack(">II", payload[16:24])
        assert width > 0
        assert height > 0


def test_hacs_metadata_is_present() -> None:
    hacs = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
    assert hacs["name"] == "Contract Generated UI"
    assert hacs["render_readme"] is True


def test_service_entrypoint_is_present() -> None:
    init_py = (ROOT / "custom_components" / "contract_generated_ui" / "__init__.py").read_text(encoding="utf-8")
    assert "async_setup_entry" in init_py
    assert "async_unload_entry" in init_py
