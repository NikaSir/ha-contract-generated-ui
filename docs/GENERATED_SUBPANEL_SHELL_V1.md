# Generated Subpanel Shell v1

**Status:** generated-subpanel architecture governed by canonical standards  
**Owner:** `ha-contract-generated-ui`  
**Canonical shell:** `SPECIALIZED_PANEL_SHELL_STANDARD.md` v1.3  
**Canonical zoom:** `SPECIALIZED_PANEL_ZOOM_STANDARD.md` v1.3

> Historical note: old revisions described permanent Header Back and optional on-screen zoom controls. Both are superseded. The permanent left Header rail is Home Assistant main-system menu, and the standard mobile zoom interaction is gesture-only.

## Decision

Generated application subpanels use the same formal specialized-panel shell as integration-owned panels. Home Assistant integrations own domain data/commands; CGUI owns generated shell geometry/navigation for generated panels.

```text
Home Assistant integration
  └─ entities / states / services / buttons / events

Contract Generated UI
  └─ contracts / semantic inventory / manifests / navigation
  └─ safe-area policy
  └─ Header / HA main-system menu
  └─ optional peer-device context placement
  └─ exactly one gesture-driven work viewport
  └─ Bottom Tab Bar
  └─ routes / generation / semantic release gate
```

Existing integration-owned panels may implement the same contract locally without runtime-depending on CGUI.

## Navigation data

`navigation/main.yaml` owns logical route IDs, absolute paths, parent relationships and tab groups.

A generated specialized panel declares 2–5 primary views in its manifest. Logical parent route remains metadata for deep links/domain navigation but is not the permanent left Header behavior.

## Header

Canonical generated Header:

```text
☰ | geometrically centered subsystem title | optional global action
```

The left control dispatches the standard Home Assistant menu event:

```js
new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true })
```

Generated panels must not replace it with Back or an integration-specific drawer.

If a logical parent action is required, render it inside the work area.

## Safe area

Effective safe area is consumed exactly once.

Generated shell must avoid Header under Dynamic Island/notch, duplicate top inset, Bottom Bar under Home Indicator and phone-model constants.

## Bottom Tab Bar

Primary navigation is compiled from manifest/navigation data into the shared fixed full-width Bottom Tab Bar.

Generic frontend must not contain subsystem-specific route constants.

The bar stays native scale and final content scrolls above it.

## Exactly one zoomable work viewport

Each generated specialized-panel instance has exactly one work viewport.

Native-scale layers outside it:

- Header / HA menu / right action;
- persistent peer-device selector when present;
- Bottom Tab Bar;
- transient zoom reset feedback.

Shell reconciliation is idempotent across HA rerenders/state updates. It must never create nested wrappers, duplicate gesture handlers or progressive shrinking.

## Gesture-only zoom

On touch clients:

- two-finger focal-point pinch;
- pan/scroll when enlarged;
- no permanent `− / % / +` controls;
- two-finger double tap resets scale + scroll to 100%/origin;
- completed 97–103% pinch snaps to 100%;
- reset/snap briefly shows `Масштаб 100%`;
- scale persists locally per panel and peer device where applicable.

Detailed behavior is normative in Zoom Standard v1.3.

## Peer-device context

When multiple peer physical devices are represented, Device Selector may sit below Header and must remain native-scale, fixed-order, selected-device-only and persistent across Bottom Tab changes.

Subordinate channels are not automatically peer devices.

## Renderer contract

Placeholders must remain deterministic and must not fabricate domain data. Real production renderers use verified semantic bindings.

## Runtime source layout

```text
/config/contract_generated_ui/
├── contracts/
├── manifests/
├── navigation/
├── inventory/        # private
├── snapshots/        # private/history
└── generated/
    ├── *.yaml
    ├── *.meta.json
    ├── navigation.json
    └── lovelace_configuration_snippet.yaml
```

Bundled sync updates public managed sources only; private inventory/snapshots are never overwritten.

## Semantic safety

Shell/navigation changes participate in renderer/release fingerprints where applicable. Parent route, tab structure and shell implementation are not formatting noise.

## Adding another subsystem

1. confirm route/parent in navigation data;
2. add manifest;
3. define 2–5 primary views;
4. add verified domain modules;
5. use canonical shell v1.3 / zoom v1.3;
6. regenerate and pass semantic + target-device UI review.

No subsystem-specific Header/menu/safe-area/zoom/Bottom-Bar implementation is allowed in generic frontend code.

## Acceptance checklist

A generated specialized shell release is accepted when:

- left Header control is HA system menu and uses `hass-toggle-menu`;
- title is geometrically centered;
- safe area consumed exactly once;
- Bottom Tab comes from declarative navigation;
- exactly one work viewport exists;
- repeated HA updates do not nest wrappers/handlers;
- focal-point pinch/pan works;
- no permanent zoom controls appear;
- two-finger double tap resets scale/scroll;
- 97–103% snaps to 100%;
- `Масштаб 100%` confirmation appears briefly;
- no horizontal clipping exists at 100% mobile layout;
- content clears Bottom Tab Bar;
- no fabricated domain data;
- parity/CI/Hassfest/HACS checks pass;
- actual target-device field acceptance is completed.

## Architectural invariant

> Generated subsystems join declaratively. HA menu, safe-area ownership, optional peer context, exactly one gesture-driven work viewport and fixed Bottom Tab Bar are shell responsibilities rather than domain code.
