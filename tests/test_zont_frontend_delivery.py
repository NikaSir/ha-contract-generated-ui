"""Regression coverage for the production ZONT panel bundle."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "contract_generated_ui"
FRONTEND = INTEGRATION / "frontend"


def test_registered_zont_bundle_is_approved_and_autonomous() -> None:
    bundle = (FRONTEND / "nikas-generated-zont.js").read_text(encoding="utf-8")
    constants = (INTEGRATION / "const.py").read_text(encoding="utf-8")

    assert 'GENERATED_ZONT_BUILD = "b006"' in constants
    assert 'const UI_VERSION = "0.8.17"' in bundle
    assert 'const ASSET_ROOT = "/contract_generated_ui/frontend/assets"' in bundle
    assert 'ElementClass.prototype.__zontV0812 = true' in bundle
    assert "import(" not in bundle


def test_zont_equipment_assets_ship_with_registration_owner() -> None:
    assets = FRONTEND / "assets"
    assert (assets / "zont-boiler-casing-v0812.webp").is_file()
    assert (assets / "zont-dhw-shell-v0812.webp").is_file()
