# Specialized Panel Frontend Delivery Standard v1.0

**Status:** Required for integration-owned specialized panels with custom frontend  
**Canonical owner:** `NikaSir/ha-contract-generated-ui`  
**Reference evidence:** Stark SolarPower production frontend

## 1. Purpose

A specialized panel can be visually correct and still fail in the field because of stale browser modules, broken runtime import chains, missing assets or non-deterministic packaging.

This standard defines how an integration-owned panel frontend is packaged, registered, cached and release-gated. It does not prescribe the integration's domain UI.

## 2. Ownership boundary

The integration owns:

- its production frontend entry module;
- build-time source modules;
- local panel assets;
- panel registration;
- panel manifest metadata;
- frontend release CI.

`ha-contract-generated-ui` owns the canonical shell/UI/delivery standards and reference contracts. Conformance does not require a runtime dependency on CGUI.

## 3. One stable production entry

Every integration-owned specialized panel MUST expose exactly one production frontend entry module to Home Assistant.

Conforming examples:

```text
frontend/panel.js
```

or a deterministic generated artifact:

```text
frontend/panel-bundle.js
```

Historical/versioned source files may remain in the repository for build history or composable development, but the browser MUST NOT depend on a runtime chain of historical modules.

Production registration must not load:

```text
v020.js → v021.js → v030.js → ...
```

at runtime.

## 4. Deterministic build when a bundle is generated

If the production entry is generated from multiple source files:

- the build is reproducible from a clean checkout;
- the generated artifact is committed or produced by an equally deterministic release step;
- rebuilding without source changes produces no diff;
- build order is explicit;
- unsupported runtime `import` / `export` statements are rejected when the target artifact is intended to be self-contained.

A generated bundle must carry a clear generated-file marker and must not be edited manually.

## 5. Home Assistant registration

The integration registers one stable panel route and one production module URL.

Conceptual registration metadata:

```yaml
panel:
  id: subsystem
  path: /dashboard-subsystem
  owner: integration_domain
  ui_version: 1.2.3
  frontend:
    entry: panel-bundle.js
    cache_busting: query_ui_version
```

Required:

- stable route for the application;
- stable web-component name;
- production module points to the single entry artifact;
- UI version participates in cache busting;
- `panel_custom` / static-path registration is deterministic across restart/reload;
- safe-area ownership is declared consistently with the Specialized Panel Shell Standard.

## 6. Cache busting

A frontend UI release MUST change the production module URL sufficiently to invalidate stale browser/Companion App caches.

Preferred pattern:

```text
/local-panel/panel-bundle.js?v=<ui-version>
```

or an equivalent build identifier.

Local visual assets that change independently SHOULD also use version/build query cache busting.

The version used for cache busting must be derived from release/build metadata, not manually randomised per request.

## 7. Local static assets

Panel-critical assets ship inside the integration package.

Recommended layout:

```text
custom_components/<domain>/
└── frontend/
    ├── panel-bundle.js
    └── assets/
        ├── device.png
        └── context.webp
```

Required:

- no external CDN dependency for panel-critical artwork;
- no Base64 image payload embedded into the production JavaScript bundle when a normal static asset is suitable;
- assets are reachable from a local integration static route;
- HACS/repository packaging includes them;
- filenames or query versions allow predictable cache invalidation;
- image dimensions/quality are optimized before shipping.

## 8. Layered visual assets

Decorative/context art is not state storage.

A background image MUST NOT bake in:

- current Home Assistant measurements;
- active alarms;
- live labels;
- live power-flow state;
- entity availability.

Dynamic device art, SVG paths, status badges, labels and values remain separate runtime layers whenever they encode current state.

Contextual backgrounds may change with selected peer-device context.

## 9. Panel manifest

An integration-owned specialized panel SHOULD ship a machine-readable panel manifest. For NikaS panels this is the preferred contract boundary with CGUI and release tooling.

Recommended fields:

```yaml
api_version: nikas.home-assistant/integration-panel/v1
id: subsystem
path: /dashboard-subsystem
owner: integration_domain
ui_version: 1.2.3
shell:
  standard_version: "1.2"
header:
  left_control: home_assistant_menu
  title_alignment: viewport_center
device_context:
  selector: optional
navigation:
  primary_navigation: full_width_fixed_bottom_tab_bar
zoom:
  pinch: true
  controls: optional
  minimum_percent: 75
  maximum_percent: 200
frontend_delivery:
  mode: self_contained_bundle
  module: panel-bundle.js
  assets: []
  cache_busting: query_ui_version
  runtime_previous_version_imports: false
targets:
  primary: iPhone Pro Max portrait
```

Fields that do not apply may be omitted, but manifest and registration must not contradict each other.

## 10. Manifest / registration parity

CI MUST verify that release metadata agrees across:

- Home Assistant panel registration code;
- panel manifest;
- production entry filename;
- UI version/cache-busting parameter;
- declared static assets.

A mismatch is release-blocking because it can produce a panel that installs successfully but loads stale or missing frontend resources.

## 11. Asset existence guard

Every asset declared by panel metadata must exist in the packaged integration tree.

CI SHOULD fail when:

- a declared asset is missing;
- production entry references an unshipped local asset;
- a build step silently drops an asset;
- a renamed asset leaves a stale URL in frontend code or manifest.

## 12. JavaScript validation

At minimum CI validates:

- production entry with `node --check` or equivalent syntax validation;
- all source JS when practical;
- no prohibited runtime historical imports in a self-contained production bundle;
- deterministic rebuild parity when a bundle is generated.

For Home Assistant integrations, normal HACS/Hassfest validation remains required in addition to frontend checks.

## 13. Runtime dependency policy

The production panel may depend on Home Assistant's supported frontend environment and on resources shipped by its own integration.

It SHOULD avoid adding extra HACS frontend dependencies for capabilities that can be implemented safely with standard Web Components/HTML/CSS/SVG.

A new runtime dependency must have a concrete domain/UI benefit and a release/compatibility plan.

## 14. Safe-area registration interaction

`panel_custom` can participate in safe-area handling. Therefore frontend registration and shell CSS must agree on who consumes the effective inset.

Required:

- safe-area ownership is documented in panel metadata or implementation docs;
- the same inset is not added twice;
- a Companion App field screenshot confirms the result after registration changes.

This is a delivery concern as well as a CSS concern because panel registration options can change the effective viewport presented to the Web Component.

## 15. Versioning

Integration version and Panel UI version may be distinct when useful, but the production frontend release must have an unambiguous UI version/build identity.

When UI files or assets change:

- bump UI/build identity used for cache busting;
- regenerate deterministic bundle if applicable;
- update manifest/registration parity;
- record user-visible frontend changes in changelog/release notes.

## 16. Field release gate

A green build is necessary but not sufficient for a mobile-first panel.

Before treating a frontend release as accepted, verify on the target Home Assistant client:

- new production module actually loaded;
- expected asset version loaded;
- no stale prior UI remains;
- Header/safe areas are correct;
- Bottom Tab Bar is correct;
- peer selector and zoom behavior survive state updates;
- no missing local assets or CORS/network dependency exists.

## 17. Reference Stark SolarPower pattern

Stark SolarPower demonstrates the reference pattern:

- local static route registered by the integration;
- stable `/dashboard-ups` application route;
- one `stark-solarpower-panel-bundle.js` production entry;
- UI-version query-string cache busting;
- historical UI modules retained only as build-time inputs;
- deterministic build script;
- CI syntax/import/parity/rebuild guards;
- local PNG/WebP assets;
- panel manifest describing delivery and assets.

The pattern is evidence, not a mandatory filename/template.

## 18. Acceptance criteria

A custom integration-owned panel frontend is delivery-complete when:

1. Home Assistant loads exactly one stable production entry module;
2. version/build cache busting changes with frontend releases;
3. historical source modules are not runtime dependency chain;
4. deterministic rebuild passes when applicable;
5. production JavaScript syntax validation passes;
6. panel registration and manifest agree;
7. all declared assets exist in the package;
8. critical artwork is local, not CDN/Base64 dependent;
9. live state remains outside decorative pixels;
10. safe-area ownership is not duplicated by registration + CSS;
11. HACS/Hassfest/repository checks pass where applicable;
12. target-device field check confirms the intended frontend and assets loaded.

## Project rule

> One integration-owned specialized panel = one stable production frontend entry, deterministic release identity, local packaged assets, manifest/registration parity and CI-enforced reproducibility. Historical frontend evolution may remain in source control, but it is not a runtime loading architecture.
