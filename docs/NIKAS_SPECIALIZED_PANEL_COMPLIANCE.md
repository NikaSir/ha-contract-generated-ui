# Specialized Panel Compliance Audit — 2026-08-26

Canonical requirements are in `NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` v1.5.

| Surface | Header | 100% scroll/pan | Enlarged bounds | Bottom Tab Bar | Brand | Result |
|---|---|---|---|---|---|---|
| House (`nikas-house-overview`) | PASS: UPS geometry, two-line title and matched menu/refresh plaques | PASS: native vertical scroll, `x = y = 0`, no one-finger transform pan | PASS: transform pan starts only above 100% and is axis-clamped on resize | PASS: 52px tabs, 28px `ha-icon`, 12px/700 labels and safe area | PASS: packaged `brand/icon.png` | PASS |
| Infrastructure (`nikas-infrastructure-overview`) | PASS: UPS geometry, two-line title and matched menu/refresh plaques | PASS: native vertical scroll, `x = y = 0`, no one-finger transform pan | PASS: transform pan starts only above 100% and is axis-clamped on resize | PASS: 52px tabs, 28px `ha-icon`, 12px/700 labels and safe area | PASS: same packaged integration brand | PASS |
| Generated standalone host (`nikas-generated-subpanel`) | PASS: permanent HA menu, UPS title/plaques and fixed peer selector | PASS: native vertical scroll with normalized offsets | PASS: gesture-only focal pinch and overflow-axis clamp | PASS: 52px tabs, 28px `ha-icon`, 12px/700 labels and safe area | N/A: host inherits the owning integration identity | PASS |

- v1.5 is the sole normative shell/zoom/Header/navigation/brand source.
- Older standards are explicitly superseded where they conflict.
- The former transform-pan-at-100% rule is non-conforming.
- Registered panel `module_url` values point to autonomous generated bundles in `frontend/dist`; they contain no runtime `import` chain.
- Source modules remain readable in `frontend/`; `scripts/build_frontend_bundles.sh` deterministically rebuilds the release artifacts.


<!-- v1.6-adoption -->
## v1.6 adoption delta — 2026-08-26

This section is normative. Earlier PASS evidence in this file was collected against v1.5 and must not be read as an automatic v1.6 runtime PASS.

- **Indicator policy:** `Дом сейчас` is explicitly **DISABLED** for the common connection/freshness indicator. Infrastructure and generated hosts remain opt-in; no indicator is added without a separate panel requirement.
- **Stable DOM:** House, Infrastructure and generated hosts must preserve Header/viewport/tab-bar node identity and patch live data in place. Polling, age changes and indicator changes may not trigger whole-panel replacement.
- **Fixed chrome:** Header and Bottom Tab Bar must retain fixed screen coordinates on short and long views; Work Viewport is the only scroll owner and must block outer HA scroll chaining.
- **Typography:** new/generated panels use the LIDER 9–25px scale, with 12px as the meaningful-interface minimum.
- **Brand:** packaged integration identity remains mandatory; generated hosts inherit the owning integration identity.
- **Required follow-up:** extend automated checks to stable DOM identity, short-view menu anchoring, typography floors and the explicit no-indicator rule for `Дом сейчас`.
