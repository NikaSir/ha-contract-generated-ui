from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "custom_components" / "contract_generated_ui"
EXPECTED_PUBLIC_SOURCE_FILES = 11


def _module():
    package_name = "contract_generated_ui_sync_test"
    package_spec = importlib.util.spec_from_file_location(
        package_name,
        PACKAGE_PATH / "__init__.py",
        submodule_search_locations=[str(PACKAGE_PATH)],
    )
    assert package_spec is not None and package_spec.loader is not None
    package = importlib.util.module_from_spec(package_spec)
    sys.modules[package_name] = package
    package_spec.loader.exec_module(package)

    spec = importlib.util.spec_from_file_location(
        f"{package_name}.runtime_source_sync",
        PACKAGE_PATH / "runtime_source_sync.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_bundled_sync_updates_only_public_source_directories(tmp_path: Path) -> None:
    module = _module()
    root = tmp_path / "contract_generated_ui"
    (root / "inventory").mkdir(parents=True)
    (root / "snapshots").mkdir(parents=True)
    (root / "generated").mkdir(parents=True)
    inventory = root / "inventory" / "home.yaml"
    snapshot = root / "snapshots" / "current.json"
    generated = root / "generated" / "infrastructure.yaml"
    inventory.write_text("PRIVATE-INVENTORY\n", encoding="utf-8")
    snapshot.write_text("PRIVATE-SNAPSHOT\n", encoding="utf-8")
    generated.write_text("GENERATED-CANDIDATE\n", encoding="utf-8")

    result = module.sync_bundled_public_sources(root)
    assert result.checked_files == EXPECTED_PUBLIC_SOURCE_FILES
    assert result.changed_files == EXPECTED_PUBLIC_SOURCE_FILES

    assert inventory.read_text(encoding="utf-8") == "PRIVATE-INVENTORY\n"
    assert snapshot.read_text(encoding="utf-8") == "PRIVATE-SNAPSHOT\n"
    assert generated.read_text(encoding="utf-8") == "GENERATED-CANDIDATE\n"

    for name in (
        "infrastructure_power_grid.yaml",
        "infrastructure_ups.yaml",
        "infrastructure_keenetic.yaml",
        "house_irrigation_controller.yaml",
        "house_irrigation_zone.yaml",
        "house_irrigation_lab.yaml",
    ):
        assert (root / "contracts" / name).exists()

    for name in (
        "infrastructure.yaml",
        "zont.yaml",
        "starline.yaml",
        "irrigation.yaml",
    ):
        assert (root / "manifests" / name).exists()

    assert (root / "navigation" / "main.yaml").exists()

    second = module.sync_bundled_public_sources(root)
    assert second.checked_files == EXPECTED_PUBLIC_SOURCE_FILES
    assert second.changed_files == 0
