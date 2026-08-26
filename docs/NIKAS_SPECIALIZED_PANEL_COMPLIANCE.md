# Specialized Panel Compliance Audit — 2026-08-26

Canonical requirements are in `NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` v1.5.

| Surface | Header | 100% scroll/pan | Enlarged bounds | Bottom Tab Bar | Brand | Result |
|---|---|---|---|---|---|---|
| House (`nikas-house-overview`) | GAP: rails are transparent; title/version sizes differ from UPS | GAP: transform pan owns one-finger vertical movement at 100% | PARTIAL: content bounds are clamped, but the 100% invariant is missing | GAP: icon is 25px and tab height is 60px | PASS: packaged `brand/icon.png` | Runtime follow-up required |
| Infrastructure (`nikas-infrastructure-overview`) | GAP: transparent rails and one-line title | GAP: transform pan remains enabled at 100% | PARTIAL: bounds exist, but axes are not governed by the new 100% rule | GAP: icon is 25px and tab height is 60px | PASS: same packaged integration brand | Runtime follow-up required |

- v1.5 is the sole normative shell/zoom/Header/navigation/brand source.
- Older standards are explicitly superseded where they conflict.
- The former transform-pan-at-100% rule is non-conforming.
- Runtime gaps are recorded rather than silently represented as compliant.

