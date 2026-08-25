# Stark SolarPower panel lessons for the NikaS UI standards

**Status:** architecture evidence / normative input  
**Reference implementation:** `NikaSir/ha-stark-solarpower`  
**Observed panel line:** UI `0.3.x` → `0.5.6`  
**Primary field target:** Home Assistant Companion App on iPhone Pro Max, portrait

This document records lessons proven by Stark SolarPower and promoted into shared specialized-panel standards. Stark remains a reference implementation, not a runtime dependency of other panels.

## 1. Integration-owned application boundary works

Stark owns one stable custom panel route, Home Assistant entity/device discovery, domain presentation, frontend assets and one production frontend artifact. JavaScript consumes Home Assistant state/registries and does not call the vendor API directly.

Adopted rule: integration owns domain UI/package; shared standards own shell/release invariants.

## 2. Safe area must have exactly one owner

Field review exposed duplicate top-safe-area padding. Correct behavior consumes the effective inset exactly once.

Adopted rule:

- Dynamic Island/notch and Home Indicator insets are consumed once;
- panel registration and CSS must agree on ownership;
- no view/card adds a second independent safe-area offset;
- blank duplicate top bands are shell defects.

## 3. The left Header rail is native Home Assistant menu

Stark UI 0.5.6 verified the final project rule: the permanent left Header control dispatches the Home Assistant menu event:

```js
new CustomEvent("hass-toggle-menu", {
  bubbles: true,
  composed: true,
})
```

Adopted rule:

- permanent left rail is HA main-system menu only;
- no browser Back, hard-coded parent Back, integration drawer or device action in that rail;
- parent navigation, if needed, appears inside work content;
- title stays geometrically centered between native-scale rails.

## 4. Persistent peer-device context is a first-class shell layer

Stark uses a persistent fixed-order selector:

`UPS Интернет | UPS Котёл`

Proven rules:

- selection never reorders peers;
- selected UPS survives primary-tab changes;
- non-selected peer may expose compact health;
- primary content belongs only to selected UPS;
- second full UPS block is not duplicated;
- selector stays native scale and outside zoom viewport;
- another discovered peer can reuse the same template.

## 5. Exactly one zoom viewport

UI 0.5.4 exposed a lifecycle defect: repeated post-render wrapping could create nested zoom wrappers, duplicate controls, blank space and progressive shrinkage. UI 0.5.5 fixed this by normalizing old wrappers and rebuilding exactly one viewport.

Adopted rule:

- exactly one work viewport per panel instance;
- shell reconciliation is idempotent;
- repeated HA state updates must not add wrappers/handlers/feedback elements;
- steady-state architecture keeps shell topology stable.

## 6. Permanent zoom buttons are not part of the standard

UI 0.5.5 removed `− / % / +` after the field defect and recovered useful mobile space.

UI 0.5.6 confirmed the replacement interaction model:

- two-finger focal-point pinch;
- pan/scroll when enlarged;
- no permanent screen zoom controls;
- local per-UPS persistence.

Adopted rule: gesture-only is the standard mobile shell, not merely an allowed variant.

## 7. Two-finger double tap is the reset gesture

Stark UI 0.5.6 implements two quick two-finger taps as the canonical reset.

Reset result:

```text
scale = 100%
scrollLeft = 0
scrollTop = 0
```

The recognizer distinguishes tap from pinch using duration/movement tolerance so normal zoom does not trigger reset.

Adopted rule: two-finger double tap resets scale and viewport origin without executing domain actions.

## 8. Near-100% pinch snaps to exact 100%

UI 0.5.6 snaps completed pinch values in the range:

```text
97% .. 103%
```

to exactly 100%.

This removes annoying near-default states such as 99%/101% and gives the user a stable canonical layout.

Adopted rule: 97–103% is the standard snap band.

## 9. Reset needs lightweight confirmation

After explicit reset or snap, Stark briefly shows:

```text
Масштаб 100%
```

The feedback is transient, non-interactive, does not reserve permanent layout space and uses polite accessibility status semantics.

Adopted rule: gesture reset must be discoverable through short confirmation without restoring a permanent toolbar.

## 10. Zoom preference includes peer-device context

Stark stores scale separately per selected UPS/client.

Adopted scope:

- single-device: panel + client;
- multi-peer-device: panel + peer-device + client;
- switching peer restores peer-specific scale;
- Bottom Tab changes preserve scale for same peer;
- zoom preference is local UI data, never HA entity state.

## 11. Responsive layout is resolved before zoom

Adopted order:

`actual viewport → responsive composition → selected peer/domain content → user zoom`.

Zoom never chooses mobile/desktop breakpoints.

## 12. Local visual assets are effective when data remains separate

Stark uses transparent UPS PNG plus optimized local WebP network/boiler context plates, delivered through integration static routes with version cache busting.

The background contains no live values. UPS artwork, SVG power paths, labels, status nodes and measurements remain separate runtime layers.

Adopted rule:

- no critical CDN dependency;
- no Base64 image payload when normal local file is suitable;
- live state is not baked into pixels;
- contextual art may change with selected peer;
- assets ship/validate with integration release.

## 13. Normal measurements are visually neutral

Stark field review reserved green/amber/red for semantic state instead of coloring ordinary numeric values.

Adopted rule: factual telemetry is neutral; semantic colors express confirmed health/warning/fault/unreliable meaning.

## 14. Backend owns trust thresholds and factual meaning

Stark frontend consumes backend `data_stale` rather than duplicating the stale threshold.

Adopted rule:

- frontend consumes validated semantic entities when available;
- backend threshold logic is not silently reimplemented;
- unsupported runtime/watts/alarms/reserve estimates are not invented;
- missing data is shown as missing data.

## 15. Native Home Assistant surfaces reduce duplication

Long press/history links open native Home Assistant more-info/history where that provides required factual detail.

Adopted rule: custom frontend focuses on domain overview/context instead of rebuilding generic HA detail/history without material benefit.

## 16. Global actions need feedback and domain ownership

Stark Refresh uses the integration's existing `refresh_now` entity and later added busy/success/error feedback with duplicate-tap suppression.

Adopted rule: shell-level actions use stable HA integration APIs/entities, not direct vendor calls, and expose safe async feedback.

## 17. Unrelated Home Assistant updates should not rebuild shell topology

Stark uses a relevant-state fingerprint to skip unnecessary full Shadow DOM rebuilds.

Adopted rule:

- unrelated entity churn should not rebuild complete panel when practical;
- any optimization preserves exactly one viewport and gesture/reset handlers;
- performance optimization and shell idempotency are tested together.

## 18. Production frontend needs deterministic delivery

Stark replaced runtime historical-module chaining with one self-contained production bundle. CI rebuilds deterministically, syntax-checks, rejects runtime imports and verifies registration/manifest parity.

Adopted rule:

- one stable production entry;
- historical modules are build-time history;
- version cache busting;
- local asset existence guard;
- manifest/registration parity;
- lifecycle smoke/regression checks where practical.

## 19. Field acceptance is part of design

Stark needed real iPhone passes to correct typography, selector height, hero proportions, double safe-area, first-viewport density, nested zoom lifecycle, menu semantics and reset UX.

A mobile-first panel is not UI-complete from desktop render alone.

Field acceptance includes:

- safe areas;
- native HA menu event;
- Header geometry;
- selector fit;
- first useful viewport;
- Bottom Tab clearance;
- focal-point pinch/pan;
- two-finger double-tap reset;
- 97–103% snap;
- `Масштаб 100%` confirmation;
- repeated HA update lifecycle;
- unreliable states;
- peer switching;
- more-info/global-action behavior.

## 20. Standards changed from these lessons

Stark UI 0.5.6 is promoted into:

- `SPECIALIZED_PANEL_SHELL_STANDARD.md` v1.3;
- `SPECIALIZED_PANEL_ZOOM_STANDARD.md` v1.3;
- `INTEGRATION_DASHBOARD_UI_STANDARD.md` v1.4;
- `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md` v1.1.

The standards are canonical. Stark is the proven reference implementation for this revision.
