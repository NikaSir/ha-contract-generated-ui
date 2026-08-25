from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend"


def test_house_visual_scene_is_local_layered_and_fail_closed() -> None:
    bundle = (FRONTEND / "nikas-house-hero.js").read_text(encoding="utf-8")
    asset = (FRONTEND / "assets" / "house-hero-day-v1.svg").read_text(encoding="utf-8")

    assert 'const ELEMENT_NAME = "nikas-house-hero"' in bundle
    assert "/contract_generated_ui/frontend/assets/house-hero-day-v1.svg" in bundle
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
    assert "house-hero-day-v1.svg?build=0310b001" in renderer


def test_house_visual_scene_is_daytime_light_and_mobile_first() -> None:
    bundle = (FRONTEND / "nikas-house-hero.js").read_text(encoding="utf-8")
    asset = (FRONTEND / "assets" / "house-hero-day-v1.svg").read_text(encoding="utf-8")

    # The first screen still ends above the fixed global tab bar.
    assert "height:clamp(620px,calc(100svh - 184px),680px)" in bundle
    assert "min-height:0" in bundle

    # The new portrait asset is intentionally designed for mobile and can use cover.
    assert 'viewBox="0 0 900 1180"' in asset
    assert "background-size:cover" in bundle
    assert "background-position:center 51%" in bundle

    # The light theme is deliberate; dark mode is a later independent pass.
    assert "background:rgba(255,255,255,.86)" in bundle
    assert "--ink:#15202b" in bundle
    assert "--muted:#4f5d69" in bundle

    # Five top statuses remain legible by stacking icon/text vertically on mobile.
    assert "flex-direction:column" in bundle
    assert "justify-content:center" in bundle

    # Zones are recalibrated for the portrait day facade.
    assert ".window-zone{left:17%;top:46%;width:25%;height:12%}" in bundle
    assert ".gate-zone{left:10%;top:61%;width:34%;height:17%}" in bundle
    assert ".door-zone{right:14%;top:62%;width:14%;height:17%}" in bundle
