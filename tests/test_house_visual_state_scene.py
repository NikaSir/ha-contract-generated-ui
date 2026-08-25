from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend"


def test_house_visual_scene_is_local_layered_and_fail_closed() -> None:
    bundle = (FRONTEND / "nikas-house-hero.js").read_text(encoding="utf-8")
    asset = (FRONTEND / "assets" / "house-hero-dusk-v1.svg").read_text(encoding="utf-8")

    assert 'const ELEMENT_NAME = "nikas-house-hero"' in bundle
    assert "/contract_generated_ui/frontend/assets/house-hero-dusk-v1.svg" in bundle
    assert "base64" not in bundle.lower()
    assert "https://" not in bundle
    assert '"unknown"' in bundle
    assert '"unavailable"' in bundle
    assert "min < 198 || max > 242" in bundle
    assert "min < 205 || max > 235" in bundle
    assert "min < 210 || max > 230" in bundle
    assert "Нет данных" in bundle
    assert "Авария" in bundle
    assert "Отклонение" in bundle
    assert "Внимание" in bundle

    # The decorative asset must not contain baked Home Assistant facts or UI text.
    assert "<text" not in asset.lower()
    assert "sensor." not in asset
    assert "binary_sensor." not in asset
    assert "229.7" not in asset
    assert "50.0" not in asset


def test_house_visual_scene_keeps_data_and_art_separate() -> None:
    renderer = (ROOT / "generator" / "render_house.py").read_text(encoding="utf-8")
    assert '"type": "custom:nikas-house-hero"' in renderer
    assert '"power": [entities["power_a"], entities["power_b"], entities["power_c"]]' in renderer
    assert '"water": entities["water_drinking"]' in renderer
    assert '"internet": entities["internet"]' in renderer
    assert '"access": {' in renderer
    assert "HOUSE_HERO_ASSET_URL" in renderer


def test_house_visual_scene_fits_real_mobile_viewport_without_cover_zoom() -> None:
    bundle = (FRONTEND / "nikas-house-hero.js").read_text(encoding="utf-8")

    # First screen must end above the fixed global tab bar on iPhone-class viewports.
    assert "height:clamp(620px,calc(100svh - 184px),680px)" in bundle
    assert "min-height:0" in bundle

    # The landscape house art is deliberately scaled to show most of the facade,
    # rather than using `cover` and cropping the house into a close-up.
    assert "background-size:125% auto" in bundle
    assert "background-position:center 48%" in bundle

    # Five top statuses remain legible by stacking icon/text vertically on mobile.
    assert "flex-direction:column" in bundle
    assert "justify-content:center" in bundle

    # Zone coordinates are tied to the mobile 125%-wide art transform.
    assert ".window-zone { left:16%; top:45.5%; width:18%; height:8.2%; }" in bundle
    assert ".gate-zone { left:10%; top:54%; width:29%; height:12%; }" in bundle
    assert ".door-zone { right:13.5%; top:55.5%; width:11.5%; height:10.8%; }" in bundle
