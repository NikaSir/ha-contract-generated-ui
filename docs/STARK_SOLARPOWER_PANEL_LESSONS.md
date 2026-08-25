# Stark SolarPower panel lessons for the NikaS UI standards

**Status:** architecture evidence / normative input  
**Reference implementation:** `NikaSir/ha-stark-solarpower`  
**Observed panel line:** UI `0.3.x` → `0.5.5`  
**Primary field target:** Home Assistant Companion App on iPhone Pro Max, portrait

This document records lessons proven by the Stark SolarPower panel and explains which of them are promoted into the shared specialized-panel standards. It does not make Stark SolarPower a runtime dependency of other panels.

## 1. Integration-owned application boundary works

Stark SolarPower owns one stable custom panel route, its Home Assistant entity/device discovery, domain presentation, frontend assets and production frontend artifact. The panel consumes Home Assistant entities and registries; it does not call the SolarPower vendor API from JavaScript.

Adopted rule:

- an integration-owned panel keeps ownership of its domain UI and package;
- the shared NikaS standards define shell behavior and release invariants;
- conformity must not require moving domain code into `ha-contract-generated-ui`.

## 2. Safe area must have exactly one owner

The iPhone field pass exposed duplicate top safe-area padding. Later Stark UI versions corrected this by making the application boundary responsible for consuming the top inset exactly once.

Adopted rule:

- notch/Dynamic Island and Home Indicator insets are consumed exactly once;
- if Home Assistant/panel registration already supplies a safe-area value, the panel shell uses that effective value rather than adding a second copy;
- no domain view adds independent top/bottom safe-area padding.

A blank band caused by doubled `safe-area-inset-top` is a shell defect.

## 3. The permanent left Header control is Home Assistant navigation

Stark iterations demonstrated that domain Back, integration drawers and Home Assistant navigation are different concerns. The project-level decision is now stricter than the historical Stark builds:

- the permanent left rail belongs to Home Assistant and opens the main-system menu;
- an integration-specific drawer must not impersonate the Home Assistant menu;
- parent/drill-down navigation may exist elsewhere, but not by replacing the permanent system-menu rail.

The Header title remains geometrically centered between symmetric left/right rails. A decorative product icon does not occupy the Header title line.

## 4. Persistent peer-device context is a first-class shell layer

Stark SolarPower has two peer UPS devices. Field iterations converged on a persistent selector directly below the Header:

`UPS Интернет | UPS Котёл`

Proven rules:

- fixed device order;
- selection never reorders devices;
- selected device survives section changes;
- compact health may be visible for non-selected peers;
- detailed primary content belongs only to the selected device;
- a second full device block is not appended below;
- a newly discovered peer can reuse the same UI template.

Adopted rule: a persistent peer-device selector remains at native scale and is outside the zoomable domain viewport.

## 5. Exactly one zoom viewport

Stark UI 0.5.4 added work-area zoom. Optimized Home Assistant state updates then exposed a lifecycle defect: repeated shell installation could create nested zoom wrappers, duplicate controls, blank space and progressive content shrinkage. UI 0.5.5 fixed the field defect by normalizing old wrappers and rebuilding exactly one clean viewport.

Adopted rule:

- there is exactly one zoom viewport per specialized panel instance;
- shell installation is idempotent;
- rerendering must never wrap an already wrapped work area;
- controls, when enabled, also exist exactly once;
- optimized/partial Home Assistant updates must not mutate shell topology accidentally.

A shell implementation that relies on repeated blind DOM post-processing is not production-complete.

## 6. Pinch is the essential mobile zoom interaction; controls are policy

Stark UI 0.5.5 was field-accepted with gesture-only zoom after removing the on-screen `− / % / +` toolbar that participated in the 0.5.4 defect.

Adopted rule:

- two-finger focal-point pinch is mandatory on touch devices;
- pan/scroll and persistence are mandatory;
- on-screen zoom controls are a shell presentation policy, not a domain requirement;
- when controls are enabled they use the shared `− / percentage / +` behavior and remain outside the zoom viewport;
- gesture-only mobile presentation is conforming when explicitly declared and field-accepted.

This keeps accessibility available without forcing permanent controls onto every compact mobile composition.

## 7. Zoom preference may include peer-device context

Stark stores scale per panel client and selected UPS. This proved useful because two peer devices can have different visual density.

Adopted persistence scope:

- single-device panel: `panel + client`;
- multi-peer-device panel: `panel + peer-device + client` is allowed and preferred when layouts differ materially;
- switching peer device restores that peer's scale;
- zoom is local UI preference, never Home Assistant entity state.

## 8. Responsive layout is resolved before zoom

Stark keeps the accepted iPhone layout and then scales the work content. Zoom does not cause the layout to flip between mobile and desktop breakpoints.

Adopted rule:

`actual viewport → responsive composition → selected-device content → user zoom`.

## 9. Local visual assets are effective when data remains separate

Stark uses:

- a transparent PNG for the physical UPS;
- optimized WebP context plates for the network room and boiler room;
- local integration static routes;
- query-string cache busting tied to UI version.

The background contains no live values. UPS artwork, power paths, status nodes, labels and measurements remain separate HTML/SVG/runtime layers.

Adopted rule:

- no remote CDN dependency for panel-critical artwork;
- no Base64 image payload inside the production JavaScript bundle;
- decorative/context art must never bake current Home Assistant state into pixels;
- dynamic layers stay semantic and interactive;
- device/context-specific backgrounds may be selected declaratively from the current peer-device context.

## 10. Normal measurements are visually neutral

Stark field review moved green/amber/red away from ordinary measurements and reserved those colors for confirmed semantic state.

Adopted rule:

- normal numeric telemetry uses neutral typography;
- semantic colors communicate health, warning, fault or unreliable state;
- `unknown`, `unavailable`, stale/source-loss states are never styled as healthy.

## 11. Backend owns trust thresholds and factual meaning

Stark corrected explanatory UI so the backend `data_stale` entity owns the stale threshold. The frontend reports the state and age rather than duplicating the threshold logic.

Adopted rule:

- if the integration exposes a validated semantic state, frontend code consumes it;
- the UI must not silently reimplement backend thresholds that can drift;
- derived runtime, watts, alarms or reserve estimates are not invented when no proven entity/algorithm exists;
- lack of data is shown as lack of data.

## 12. Native Home Assistant surfaces reduce duplication

Stark uses long press / history links to open native Home Assistant more-info/history rather than implementing a second history subsystem.

Adopted rule:

- factual entities should use native more-info/history when that provides the required detail;
- custom frontend should focus on domain overview and context, not duplicate Home Assistant facilities without a clear benefit.

## 13. Global actions need feedback and domain ownership

Stark Refresh uses the integration's existing `refresh_now` button entity. A later UI iteration added busy/success/error feedback and prevented duplicate taps while refresh was in flight.

Adopted rule:

- shell-level actions call only stable Home Assistant APIs/entities of the owning integration;
- frontend code does not bypass the integration to call vendor APIs;
- async global actions should expose progress/result feedback and suppress duplicate activation while busy.

## 14. Unrelated Home Assistant updates should not rebuild the panel

Stark added a render fingerprint so unrelated Home Assistant entity churn does not rebuild the whole Shadow DOM.

Adopted rule:

- integration-owned panels should avoid full rerender on unrelated HA updates;
- optimization must preserve shell topology;
- render optimization and shell idempotency are tested together.

## 15. Production frontend needs deterministic delivery

Stark replaced a runtime chain of historical UI modules with one self-contained production bundle. Historical files remain build-time sources only. CI rebuilds the bundle deterministically, checks JavaScript syntax, rejects runtime imports and verifies registration/manifest consistency.

Adopted rule:

- one deterministic production entry module per integration-owned panel;
- historical/versioned source modules must not become runtime dependencies;
- entry URL uses version-based cache busting;
- CI verifies entry syntax, manifest/registration parity and deterministic output;
- asset files declared by the panel manifest must exist in the shipped integration package.

## 16. Field acceptance is part of the design process

Stark needed several real iPhone passes to correct typography, selector height, hero proportions, safe-area duplication, first-viewport density and zoom lifecycle defects.

Adopted rule:

A mobile-first panel is not UI-complete from a desktop render alone. Release acceptance includes actual target-device screenshots/interaction checks for:

- safe areas;
- Header geometry;
- selector fit;
- first useful viewport;
- Bottom Tab Bar clearance;
- pinch/pan behavior;
- `unknown` / stale / source-loss states;
- peer-device switching;
- long press / more-info;
- global-action feedback.

## 17. Standards changed from these lessons

The Stark experience is promoted into:

- `SPECIALIZED_PANEL_SHELL_STANDARD.md`;
- `SPECIALIZED_PANEL_ZOOM_STANDARD.md`;
- `INTEGRATION_DASHBOARD_UI_STANDARD.md`;
- `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md`.

The standards are canonical. Stark SolarPower remains a reference implementation and may itself require follow-up migration when a newer canonical shell rule supersedes a historical Stark implementation.
