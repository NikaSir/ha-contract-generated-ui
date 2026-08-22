# NikaS frontend resources

Home Assistant 2026 can construct Lovelace before a late `custom:` element is registered. NikaS central dashboards therefore keep their primary content native Lovelace. Frontend JavaScript is used only where an application shell materially improves navigation.

## Global navigation — Contract Generated UI 0.20.0

The 0.20.0 line keeps the frontend cache generation globally monotonic at **b004** after the b001–b003 field-test sequence.

Contract Generated UI automatically loads the global navigation enhancement through Home Assistant `frontend.add_extra_js_url()`:

```text
/contract_generated_ui/frontend/nikas-ui.js?build=b004
```

It renders the common `Дом · Действия · Инфра` Bottom Tab Bar and Lovelace-embedded tab groups described by the formal navigation contract. If this progressive enhancement loads late, native Lovelace content remains usable.

No manual `lovelace.resources` entry is required.

## Shared generated application panels

Generated application subpanels such as ZONT and StarLine no longer require a generated Lovelace host dashboard when their logical parent surface is external to Contract Generated UI.

They are **автоматически** registered as Home Assistant custom panels by Contract Generated UI using one shared web component and one self-contained frontend bundle:

```text
/contract_generated_ui/frontend/nikas-generated-subpanel.js?build=b004
```

The bundle contains no ZONT-, StarLine- or subsystem-specific route constants. Panel configuration is derived from:

```text
PanelManifest + NavigationContract
```

The shared host receives only presentation/navigation metadata:

- panel title and subtitle;
- logical parent path for Back;
- 2–5 tab IDs, labels and icons;
- field-test placeholder text until real domain contracts are connected.

Home Assistant entity IDs and private semantic inventory are not exposed through panel registration metadata.

### Visual contract

Generated custom panels intentionally use the same application language as external NikaS specialized panels:

- Back button in the upper-left;
- geometrically centered title/subtitle;
- common action rail in the upper-right;
- Hero status section;
- rounded application cards;
- fixed edge-attached Bottom Tab Bar;
- safe-area handling on iPhone;
- the same state and spacing hierarchy.

Architectural invariant:

> One CGUI-owned shared custom-panel host; external-panel-like appearance.

## Routing and Back

A generated custom panel has one Home Assistant panel route, for example:

```text
/dashboard-zont
/dashboard-starline
```

Its logical parent remains declarative in `navigation/main.yaml`:

```text
ZONT     → /dashboard-house/heating
StarLine → /dashboard-house/vehicles
```

The shared Header uses this parent path directly. It does not depend on browser history.

Tab switching inside the shared custom panel is owned by the common panel host. The tab list itself remains manifest-driven.

## Lovelace registration

Generated application subpanels are **not** exported under `lovelace.dashboards:` and therefore require no manual edit of `configuration.yaml`.

`lovelace_configuration_snippet.yaml` contains only CGUI-owned Lovelace dashboards that genuinely require YAML-dashboard registration.

During field validation generated ZONT and StarLine panels are intentionally visible in the Home Assistant sidebar so their mobile shell can be tested directly. Parent launch-card integration can be enabled when the relevant parent dashboard is itself CGUI-owned or exposes a supported declarative extension point.

## Embedded mode

The renderer still supports embedded generated subviews when a real CGUI host manifest exists for the target dashboard. In that case native `subview: true` and explicit `back_path` remain the reliability fallback and the shared navigation contract remains authoritative.

The renderer must not require an embedded host manifest merely because a logical parent path exists outside CGUI.

## Navigation registry

Contract Generated UI compiles navigation data to:

```text
/config/contract_generated_ui/generated/navigation.json
```

and serves it at:

```text
/contract_generated_ui/navigation.json
```

Standalone custom-panel groups are removed from the **served global-overlay registry** so `nikas-ui.js` cannot draw a second Header or Bottom Tab Bar over the dedicated custom-panel host. Embedded Lovelace tab groups such as the existing electricity subpanel remain in the registry.

## Legacy frontend modules

`nikas-app-shell.js` and `nikas-infrastructure-summary.js` remain migration fallbacks for older generated dashboards. New generated application subpanels do not depend on them.

After a Contract Generated UI update, fully restart Home Assistant. Regenerate dashboards when deterministic YAML/trace artifacts need to be refreshed or reviewed.
