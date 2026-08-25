# Integration dashboard header standard — superseded

**Status:** Superseded  
**Superseded by:** `docs/INTEGRATION_DASHBOARD_UI_STANDARD.md` v1.3 and `docs/SPECIALIZED_PANEL_SHELL_STANDARD.md` v1.2

The former header-only standard is no longer normative by itself.

The current specialized-panel standards cover the complete application shell and incorporate field lessons from Stark SolarPower:

- the permanent **Home Assistant main-system menu** control is always on the left; it is not panel Back and not an integration-specific drawer;
- the application title is geometrically centered on the mobile viewport;
- no decorative integration/device icon shifts the Header title;
- optional short subtitle carries model/context/version;
- at most one global action such as Refresh occupies the right rail and should expose async feedback;
- top safe area is consumed **exactly once**, avoiding both Dynamic-Island overlap and duplicate blank bands;
- a persistent peer-device selector, when present, sits below Header and stays at native scale;
- exactly one zoomable work viewport contains domain content;
- focal-point pinch is mandatory on touch clients; on-screen zoom controls are optional shell presentation;
- primary navigation is a full-width fixed Bottom Tab Bar with bottom-safe-area clearance;
- `unknown`, `unavailable`, stale/source-loss states are never treated as healthy;
- integration-owned frontend delivery uses a stable versioned production entry and local packaged assets.

See:

- `docs/SPECIALIZED_PANEL_SHELL_STANDARD.md`;
- `docs/SPECIALIZED_PANEL_ZOOM_STANDARD.md`;
- `docs/INTEGRATION_DASHBOARD_UI_STANDARD.md`;
- `docs/SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md`;
- `docs/STARK_SOLARPOWER_PANEL_LESSONS.md`.
