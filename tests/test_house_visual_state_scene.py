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
