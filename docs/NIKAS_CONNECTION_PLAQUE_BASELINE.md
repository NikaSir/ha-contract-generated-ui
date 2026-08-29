# NikaS Connection Plaque Visual Baseline

**Status:** REQUIRED companion to `NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` v1.9, section 8  
**Canonical source:** `NikaSir/ha-contract-generated-ui`  
**Applies when:** the optional two-level connection/freshness indicator is explicitly requested for a specialized panel

## Canonical visual reference

The approved S8 OMNI connection plaque is the canonical visual baseline for the optional NikaS connection/freshness indicator.

When the indicator is enabled, implementations MUST copy the approved S8 OMNI plaque geometry and placement rather than creating an integration-specific variant.

The following are fixed visual-contract properties:

- overall plaque proportions and rounded shape;
- corner radius;
- internal padding;
- status-lamp size and its position fully inside the plaque;
- spacing between lamp and text block;
- two-line text alignment and vertical rhythm;
- placement in the upper-right area of the work/hero composition when that composition provides the connection-status anchor;
- stable footprint sized so transport/freshness state changes do not move adjacent content.

Implementations MUST NOT independently change these properties merely to match an integration's local artwork or color palette.

Only factual state content and semantic status treatment vary by integration:

- transport: `Локально`, `Облако`, `Резерв`, `Нет связи`, `Нет данных`;
- freshness: `Данные актуальны`, `Данные устарели`, `Нет данных`;
- semantic status colors as defined by section 8 of UI Standard v1.9.

Typography remains `16px/700` for transport and `13px/550–600` for freshness.

## Placement rule

For hero-style overview compositions, the plaque occupies the approved S8 OMNI upper-right status position and must not overlap the device artwork, channel labels, telemetry cards, Header, or another status badge.

If a product layout physically cannot use that anchor, the exception must be explicitly approved and documented in that integration's compliance record. Silent relocation is non-conforming.

## Rendering rule

The plaque is a persistent DOM subtree. Telemetry updates patch only text, classes, ARIA state, and semantic color variables. State changes must not remount the plaque, alter its geometry, or trigger panel/hero redraws.

## Acceptance

A requested connection indicator is conforming only when both conditions are met:

1. transport/freshness semantics satisfy section 8 of `NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md` v1.9;
2. geometry and placement match the approved S8 OMNI visual baseline defined here.

For LIDER, this baseline is mandatory: use the same S8 OMNI connection plaque component and placement logic; only transport, freshness, and semantic colors may change.