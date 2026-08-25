# Stark SolarPower panel lessons for the NikaS UI standards

**Status:** architecture evidence / normative input  
**Reference implementation:** `NikaSir/ha-stark-solarpower`  
**Primary field target:** Home Assistant Companion App on iPhone Pro Max, portrait

This document records lessons proven during practical Stark SolarPower panel development and mobile acceptance. Stark is reference evidence, not a runtime dependency for other panels.

## 1. Integration-owned application boundary works

The integration owns its entities, device discovery, domain UI, frontend assets and production frontend artifact. Shared NikaS standards define shell behavior and release invariants without moving domain code into `ha-contract-generated-ui`.

## 2. Safe area must have exactly one owner

Field testing exposed duplicate top-safe-area padding. Adopted rule: notch/Dynamic Island and Home Indicator insets are consumed exactly once. No view/card adds independent phone-model offsets.

## 3. Permanent left Header control belongs to Home Assistant

The permanent left rail is the Home Assistant system menu `☰` and uses the standard `hass-toggle-menu` event. It is not Back, browser history, integration drawer or device action. Parent/drill-down navigation belongs inside work content when needed.

Header title remains geometrically centered and native scale below the effective top safe area.

## 4. Persistent peer-device context is a first-class shell layer

Stark has two peer UPS devices. The accepted selector sits directly below Header and remains native scale.

Proven rules:

- fixed peer order;
- selection never reorders devices;
- selected peer survives Bottom Tab changes;
- compact health may be visible for non-selected peers;
- detailed content belongs only to selected peer;
- new peers reuse the same template where discovery permits.

## 5. Exactly one zoom viewport

A practical rerender defect showed that repeated wrapping can create nested zoom viewports, duplicate handlers/controls, blank space and progressive content shrinkage.

Adopted rule:

- exactly one zoom viewport per panel instance;
- shell installation/reconciliation is idempotent;
- an existing canonical viewport is reused, never blindly wrapped again;
- optimized/partial HA updates must not mutate shell topology accidentally.

This is a release-blocking lifecycle invariant.

## 6. Final mobile zoom interaction is gesture-only

Practical mobile acceptance showed that permanent `− / % / +` controls consume useful space and can participate in rerender/lifecycle problems. The final standard therefore removes the permanent zoom toolbar.

Accepted interaction:

- two-finger focal-point pinch is the primary zoom gesture;
- enlarged content pans/scrolls;
- pinch ending in **97–103%** snaps to exactly **100%**;
- **two-finger double tap** resets scale and work-area scroll to **100%**;
- reset briefly shows native-scale `Масштаб 100%` confirmation;
- zoom preference persists locally per panel/client and may include selected peer-device identity.

Header, Device Selector and Bottom Tab Bar remain native scale.

## 7. Responsive layout is resolved before zoom

Accepted sequence:

```text
actual viewport
→ mobile/tablet/desktop composition
→ selected-device/domain content
→ user zoom
```

Zoom never drives responsive breakpoint selection.

## 8. Local visual assets are effective when live data stays separate

Stark uses local integration assets: transparent device artwork plus optimized context backgrounds. Live measurements, power paths and state overlays remain separate runtime HTML/SVG/UI layers.

Adopted rules:

- no remote CDN dependency for panel-critical artwork;
- no Base64 images inside production JS;
- context art contains no live HA values/status text;
- dynamic layers remain semantic/interactive;
- asset URLs use release/UI-version cache busting.

## 9. Normal measurements are visually neutral

Green/amber/red are reserved for confirmed semantic health/warning/fault. Normal numeric telemetry is neutral. `unknown`, `unavailable`, stale/source loss never appear healthy.

## 10. Backend owns trust thresholds and factual meaning

If integration exposes validated semantic state, frontend consumes it rather than reimplementing thresholds. Unsupported runtime, watts, alarms or reserve estimates are not invented.

## 11. Native Home Assistant surfaces reduce duplication

Factual entities should reuse native more-info/history when it provides the required detail. Custom UI focuses on domain overview/context.

## 12. Global actions need feedback and integration ownership

Shell-level actions use stable Home Assistant APIs/entities of the owning integration, not vendor APIs from frontend. Async actions should show busy/result feedback and suppress duplicate activation while busy.

## 13. Unrelated HA updates should not rebuild the panel unnecessarily

Relevant-state fingerprints/selective rendering are useful, but optimization must preserve shell topology, selected peer, active Bottom Tab, zoom state and interaction bindings.

## 14. Production frontend needs deterministic delivery

Accepted delivery principles:

- one deterministic production entry module;
- historical/versioned source modules are not runtime dependency chain;
- version-based cache busting;
- CI validates syntax, manifest/registration parity, deterministic output and packaged assets.

## 15. Real-device acceptance is part of design

Desktop render is insufficient. Mobile acceptance must check safe areas, HA menu, centered Header, selector fit, first useful viewport, Bottom Tab clearance, pinch/pan, 97–103% snap, two-finger reset, `Масштаб 100%` feedback, repeated HA updates, peer switching, stale/unavailable states, more-info and global-action feedback.

## 16. Standards promoted from these lessons

The Stark experience is promoted into:

- `SPECIALIZED_PANEL_SHELL_STANDARD.md` v1.3;
- `SPECIALIZED_PANEL_ZOOM_STANDARD.md` v1.3;
- `INTEGRATION_DASHBOARD_UI_STANDARD.md` v1.4;
- `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md`.

The standards are canonical. Stark SolarPower remains the field reference implementation and may itself require follow-up migration when a newer canonical rule supersedes historical behavior.