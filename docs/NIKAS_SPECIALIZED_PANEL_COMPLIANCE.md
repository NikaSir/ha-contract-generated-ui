# Specialized Panel Compliance Audit — 2026-08-26

Canonical requirements are in `NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` v1.6.

| Surface | Header / fixed chrome | Scroll / zoom | Stable rendering | Indicator | Typography / brand | Result |
|---|---|---|---|---|---|---|
| House (`nikas-house-overview`) | PASS: `23/14`, `21/13` narrow, matched plaques, height-locked shell | PASS: native vertical at 100%, bounded overflow axes above 100% | PASS: scene is mounted once and state/time updates point-patch existing nodes | PASS: explicitly absent by product rule | PASS: meaningful `12–25px`; packaged `brand/icon.png` | PASS pending phone acceptance |
| Infrastructure (`nikas-infrastructure-overview`) | PASS: same fixed Header/Bottom geometry | PASS: native vertical at 100%, bounded overflow axes above 100% | PASS: summary cards preserve DOM and patch state fields | N/A: not requested | PASS: meaningful `12–25px`; same integration brand | PASS pending phone acceptance |
| Generated standalone host (`nikas-generated-subpanel`) | PASS: permanent HA menu, fixed peer selector and Bottom Bar | PASS: one hybrid viewport and one persistent canvas | PASS: shell is mounted once; tab/device view subtrees use lazy cache | PASS: disabled unless the owning product requests it | PASS: meaningful `12–25px`; host inherits owning integration identity | PASS pending phone acceptance |

- v1.6 is the sole normative shell/zoom/Header/navigation/typography/indicator/stable-rendering/brand source.
- Older standards are explicitly superseded where they conflict.
- The former transform-pan-at-100% rule is non-conforming.
- Registered panel `module_url` values point to autonomous generated bundles in `frontend/dist`; they contain no runtime `import` chain.
- Source modules remain readable in `frontend/`; `scripts/build_frontend_bundles.sh` deterministically rebuilds the release artifacts.
