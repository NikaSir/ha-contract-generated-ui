# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Contract Generated UI `0.37.4` updates Rooms to UI `10.8.23`: it consumes the registry snapshots already carried by the Home Assistant frontend before falling back to WebSocket list calls, and turns a missing `hass` handoff into a bounded, retryable error instead of an endless loading screen.

- Contract Generated UI `0.37.3` updates Rooms to UI `10.8.22` and assigns it a new custom-element identity. This prevents an iOS Home Assistant WebView from retaining the previously registered Rooms class after an integration upgrade while preserving the bounded registry loading, error state and retry path from `0.37.2`.

- Contract Generated UI `0.36.10` integrates the existing `/dashboard-rooms` Lovelace dashboard into the current NikaS shell without copying or changing room entity logic. Rooms now receive the fixed Header, active four-item Bottom Tab Bar, room-aware centered titles and explicit return to `/dashboard-rooms/rooms`; the obsolete duplicate `Помещения · v10.8.18` overview heading is suppressed.

- Contract Generated UI `0.36.9` updates House UI to `0.37.8`: the fixed Bottom Tab Bar gains a fourth `Помещения` item using `mdi:floor-plan` and opens the existing rooms panel at `/dashboard-rooms/rooms`. The route is part of the canonical navigation registry and preserves return handoff when rooms launch a specialized panel.

- Contract Generated UI `0.36.8` updates House UI to `0.37.7`: the `Дом сейчас` top row is fixed as `Окна / Двери / Свет / Движение / Климат`; weather and protection occupy the next row, date/time and cameras the row below. `Электросеть`, `Отопление` and `Интернет` now open their owning LIDER, ZONT and Keenetic panels directly. Main-menu labels use the approved NikaS panel names.
- Contract Generated UI `0.36.7` updates House UI to `0.37.6`: the lower resource row now renders four compact text-only state plaques (`Электросеть`, `Вода`, `Интернет`, `Отопление`). Icons, status words and numeric secondary lines are removed; the existing fail-closed state logic controls only the highlighted text colour, while each plaque retains its route and a 48 px minimum mobile touch target.
- Contract Generated UI `0.36.6` updates House UI to `0.37.5`: the Climate summary no longer treats absent configured entities as unavailable, while explicit `unknown`/`unavailable` states remain orange and active heating/cooling remains yellow. The compact lower resource cards retain 12 px minimum copy, remove redundant secondary text and determine `Вода` exclusively from the verified irrigation-mainline pressure sensor: positive pressure is `Есть`, zero is `Нет воды`, and missing/unavailable telemetry is `Нет данных`.
- Contract Generated UI `0.36.4` updates House and Actions UI to `0.37.3`: the visible House status label is now `Защита`, and the legacy `Действия` dashboard receives the common fixed Header with Home Assistant menu and refresh controls. Existing status logic, Actions cards, layout and the absence of a House connection/freshness indicator remain unchanged.
- Contract Generated UI `0.36.3` fixes the field-test regressions in base UI `0.37.2`: the standalone `Дом сейчас` scene now fills its single work canvas instead of collapsing to zero height, unavailable UPS telemetry can no longer claim that data is current, and the legacy `Действия` dashboard restores its global Bottom Tab Bar after stale or removed chrome hosts. Header and navigation remain outside the transform canvas; `Дом сейчас` still has no connection/freshness indicator.
- Contract Generated UI `0.36.2` adopts specialized-panel standard v1.6: fixed `23/14px` (`21/13px` narrow) Header plaques, height-locked phone chrome, meaningful `12–25px` typography, native vertical scroll at 100%, and stable point-patched House/Infrastructure content. Generic generated panels now preserve one shell and one canvas while lazily caching tab/device views. The copy/adapt template includes the matching gesture controller and persists transforms by either supported peer-device selector key. The optional two-level transport/freshness indicator remains disabled for `Дом сейчас`; routine telemetry, clock updates and scroll no longer replace the background, viewport or navigation DOM.
- Contract Generated UI `0.36.1` aligns the House Header with the accepted Stark SolarPower shell: `Дом сейчас` is the centered primary title, `Состояние · UI v0.36.1` is the secondary line, and the native-scale 44 pt menu/refresh rails remain outside the transform canvas and below the iOS safe area.
- Contract Generated UI `0.36.0` promotes `Инфраструктура · v11.0` to an integration-owned specialized panel at `/dashboard-infrastructure/overview`, populated from verified semantics with the incoming three-phase grid, UPS Internet, UPS Boiler and Keenetic Hero 4G+. The native Header/Bottom Tab Bar remain outside one persisted transform canvas. Incoming voltage before the LIDER PS7500W-30 stabilizers is now evaluated by its passport ranges (nominal 150–265 V, working 125–275 V); downstream voltage is reserved for verified sensors and evaluated separately against the project ГОСТ range 198–242 V.
- House scene object outlines now use SVG source-image coordinates with the same `xMidYMid slice` crop as the photoreal background, preventing window/gate/entrance drift across viewports. Camera availability moves into the clock card, while the existing climate active-count plus availability-color semantics remain unchanged.
- Contract Generated UI `0.35.1` completes the ZONT handoff: this repository no longer packages or registers `/dashboard-zont`, its ZONT bundle, assets or manifest; stale runtime `zont.yaml` files are retired automatically and shared shell/zoom discovery no longer targets the ZONT element. The dedicated `ha-zont` integration is the sole panel owner.
- Contract Generated UI `0.35.0` promotes `Дом · v11.0` to an integration-owned specialized panel on the existing `/dashboard-house-v11/home` route. It uses a permanent Home Assistant `☰` menu action, native Header and Bottom Tab Bar, one persisted `translate3d(x,y,0) scale(s)` canvas, gesture-only pinch/pan/reset, 97–103% snap-to-100 and post-gesture interaction guards; the House runtime no longer depends on Lovelace constructing a late `custom:` card after refresh.
- Contract Generated UI `0.34.2` serves the approved autonomous ZONT UI `0.8.17` directly from the panel registration owner, including its local boiler artwork, eliminating the startup-order race that could show UI `0.8.0` or leave the ZONT route blank after a Home Assistant restart.

- Contract Generated UI `0.34.1` fits the House hero to the measured top edge of the fixed global Tab Bar so the second utility row cannot be hidden underneath navigation, and makes the main UI bundle statically import the House custom element to prevent cold-refresh configuration races.
- Contract Generated UI `0.34.0` replaces the truncated House hero with a complete maximum-photorealistic daytime v3 background, preserves the accepted live status composition and lets the mobile scene occupy the full work area between the native Home Assistant Header and the fixed bottom navigation.
- Contract Generated UI `0.29.3` closes the final complete-set field-polish discrepancies: Infrastructure now evaluates incoming-grid quality with the same 198/205/210/230/235/242 V thresholds used by House, the Actions swing-gate placeholder is shortened to `Нет датчика`, and the House heating summary uses mobile-safe `Основной` / `Резервный` labels while preserving the existing fail-closed state semantics.
- Contract Generated UI `0.29.1` keeps the complete-set global `Дом` tab on `/dashboard-house-v11/home` during field acceptance; navigation contract `1.1.1` changes only that global route while preserving existing subpanel parent routes and the dormant generated-irrigation candidate.
- Contract Generated UI `0.29.0` promotes `Действия` from renderer-only staging to the complete v11 central release-candidate set with public `actions.home` contract and generated `/dashboard-actions/home` manifest.
- The complete Actions renderer keeps gate control read-only (physical sectional sensor plus explicit swing-gate no-sensor placeholder), adds only allowlisted confirmed `vacuum.start` / `vacuum.return_to_base` quick commands, and delegates deep S8 OMNI and irrigation workflows to `/dashboard-s8-omni` and `/dashboard-irrigation`.
- The complete `Дом / Действия / Инфра` RC preserves existing subpanel parent semantics while the global shell is switched to the temporary House preview route for field testing.
- Bundled public sources now include Actions contract/manifest; regression coverage locks source-package parity, rejects retired ROXIMO controls and unsafe vacuum services, and preserves StarLine public-source retirement.
- Clarified the normative specialized-panel UI standard to **v1.1**: primary navigation must use a full-width, edge-attached fixed bottom Tab Bar on iPhone; floating/pill navigation bars with external side/bottom gaps are explicitly non-conforming.
- Standardized active-tab treatment inside the shared bottom bar, mobile safe-area handling, 44 pt-class touch targets, and content bottom clearance so the final card scrolls fully above navigation.
- Initial Architecture-as-Code repository bootstrap.
- Formal directories for contracts, inventory, manifests, schemas, generator and tests.
- Repository validation workflow and Dependabot configuration.
- MIT license.
- Contract Core v1 schemas for `UIContract`, `SemanticInventory` and `PanelManifest`.
- Executable `ha-contract-ui validate` / `python -m generator validate` validation path.
- Architectural guard that rejects concrete Home Assistant binding keys from contracts and manifests.
- Verified-only semantic inventory bindings and explicit unreliable-state safety invariants.
- Regression test suite for contract-core validation.
- Python dependency tracking in Dependabot.
- Home Assistant custom integration shell under `custom_components/contract_generated_ui`.
- Single-entry UI config flow and diagnostic contract-source status sensor.
- Runtime validation of `/config/contract_generated_ui` using packaged Contract Core v1 schemas.
- English and Russian translations for setup, sensor states and registry snapshot capture.
- HACS repository metadata and official Home Assistant Hassfest workflow.
- Regression guard ensuring packaged schemas stay aligned with repository schemas.
- Scrubbed Home Assistant entity-registry capture with deterministic content IDs.
- Atomic `current.json` / `previous.json` snapshot rotation only on factual registry change.
- Explicit verified-inventory builder from snapshot entities and semantic bindings.
- Semantic diff for registry snapshots and semantic inventory, including rebinding detection.
- Disabled-entity guard for verified inventory construction.
- Semantic namespace grammar that cannot be confused with Home Assistant `domain.object_id` entity IDs.
- Deterministic Lovelace Renderer v1 using core Heading, Grid and Tile cards.
- Explicit safe Tile card/icon tap, hold and double-tap action generation.
- Fail-closed service actions and restricted v1 toggle-domain allowlist.
- Deterministic `RenderTrace v1` metadata with source versions, resolved bindings and dashboard SHA-256.
- Reviewable RenderTrace semantics for views, modules, roles, domains and primary actions.
- Deterministic renderer-engine SHA-256 fingerprint in every RenderTrace.
- `RenderDiff v1` classification for manifest, source, view, module, binding, action and renderer changes.
- Critical detection of unexplained canonical dashboard drift.
- Fail-closed `ha-contract-ui gate render` release gate.
- Exact `RenderApproval v1` hash matching with automatic stale-approval rejection.
- Renderer safety, namespace-boundary, reproducibility and release-gate regression tests.
- First production infrastructure contracts for electrical grid, Stark SolarPower UPS and Keenetic WAN failover telemetry.
- Public/private runtime policy that keeps real Home Assistant `SemanticInventory` bindings outside the public repository.
- Home Assistant runtime renderer and **Generate dashboards / Сгенерировать панели** button (`0.2.0`).
- Deterministic candidate generation under `/config/contract_generated_ui/generated/` with generated-file and SHA attributes.
- Official Home Assistant YAML-dashboard registration snippet export (`0.3.0`) without automatic configuration or `.storage` mutation.
- Runtime regression tests for deterministic generation, verified-only bindings, registration snippet shape and dashboard slug safety.
- Renderer v2 Sections layout (`0.4.0`) as a deterministic layer over validated tiles_v1 semantics.
- Module-to-section composition with `max_columns: 4`, explicit non-dense placement and stable section spans.
- Explicit Tile card Sections sizing (`grid_options: columns: 6, rows: 1`) to improve label readability.
- CLI and Home Assistant runtime parity for Sections v2 generation.
- Infrastructure panel manifest `0.2.0` / title `Инфраструктура · v0.2` for the new layout baseline.
- Operational Renderer v3 (`0.5.0`) with explicit `status`, `telemetry` and `diagnostic` role groups in UI contracts.
- Two-column dense Sections composition for subsystem cards on desktop.
- Larger status tiles, denser telemetry tiles and compact core Entities cards for diagnostic roles.
- Short operational labels for power, UPS and Keenetic telemetry without changing verified bindings.
- Bundled public contracts/manifests inside the custom integration and atomic synchronization into `/config/contract_generated_ui` during generation.
- Managed-source synchronization explicitly excludes `inventory/`, `snapshots/` and `generated/` so private Home Assistant bindings and runtime history remain local.
- Infrastructure panel manifest `0.3.0` / title `Инфраструктура · v0.3`.
- Regression tests for operational role-group coverage, deterministic v3 rendering and private-source sync protection.
- Manifest-level operational group filters (`0.6.0`) so each view explicitly selects `status`, `telemetry` and/or `diagnostic` roles.
- Separate `Диагностика` view for UPS and Keenetic technical sensors while the main infrastructure overview keeps only operational status and telemetry.
- RenderTrace filtering so semantic roles and binding keys match exactly what each generated view displays.
- Infrastructure panel manifest `0.4.0` / title `Инфраструктура · v0.4` with `overview` and `diagnostics` views.
- Generator and Home Assistant runtime regression tests for the diagnostics-view boundary.
- Mobile polish for `0.7.0`: UPS `Возраст данных` and `Время данных` move from overview telemetry to the diagnostics group while `Данные устарели` remains the operational freshness indicator.
- Diagnostic-only views omit the redundant inner `Диагностика` Entities-card title and retain only subsystem headings.
- Infrastructure panel manifest `0.5.0` / title `Инфраструктура · v0.5`.
- Regression tests require clean diagnostic-only cards in both repository and Home Assistant runtime renderers.
- Staged House start-page renderer `house_home_v1` (`0.8.0`) with a mobile-first two-column Sections composition targeting iPhone Pro Max portrait.
- House preview preserves the protected start-page order: `Дом сейчас` → `Активные события` → `Ресурсы` → `Отопление и ГВС` → `Автомобили` → `Ключевые точки доступа`.
- House aggregate cards consume only semantic roles already resolved from verified private inventory; no production House entity IDs are embedded in the renderer.
- Panel manifests can declare `renderer: operational_v1 | house_home_v1` and a stable `spec.navigation` route map; mixed renderer manifests fail closed.
- House preview removes the obsolete `zone.home` dependency instead of guessing a replacement presence zone.
- ADR-001 is applied to the House start page: central resources are concise summaries while detailed irrigation, vacuum, router and UPS UX remains integration-owned.
- CLI rendering now uses the same operational renderer family as the Home Assistant runtime, with byte-locked House layout source parity.
- House preview rollout is documented as dormant/staged: `0.8.0` does not replace the live `/dashboard-house` until a separately activated preview is accepted on iPhone.
- UPS native-panel handoff (`0.9.0`): the central infrastructure UI now keeps only a compact UPS operational summary and delegates detailed UPS UX to Stark SolarPower at `/dashboard-ups`.
- `infrastructure.ups` contract `0.4.0` makes the operating-mode tile a stable **Подробнее** navigation action while preserving hold → more-info and strict `unknown` / `unavailable` semantics.
- Infrastructure panel manifest `0.6.0` removes duplicated UPS technical diagnostics from the central `Диагностика` view and keeps UPS Internet / UPS Boiler as status-only overview modules.
- Bundled runtime contract/manifest sources stay byte-equivalent to repository sources for the UPS handoff.
- Regression tests lock the `/dashboard-ups` navigation target and prevent UPS diagnostic duplication from returning to the central infrastructure panel.
- Staged Actions renderer `actions_home_v1` (`0.10.0`) for a mobile-first quick-operation/navigation surface.
- Actions `navigate` roles render full-width to emphasize transition into the canonical integration-owned panel; safe `toggle` and `more_info` actions remain compact half-width tiles.
- Actions rendering rejects unsupported/service-style action kinds and continues to rely on the base verified-inventory and toggle-domain safety gates.
- Runtime and CLI use a common multi-renderer dispatch layer supporting `operational_v1`, `house_home_v1` and `actions_home_v1` without rewriting the existing operational/House engines.
- Regression tests cover Actions deterministic sizing, unsupported-action rejection, runtime second-render stability and `python -m generator render` parity.
- NikaS App Shell v1 (`0.11.0`) adds a shared fixed, edge-attached bottom Tab Bar for central `Дом`, `Действия` and `Инфраструктура` surfaces without Card Mod or an external frontend dependency.
- The integration now serves its packaged `nikas-app-shell.js` through `async_register_static_paths` and registers it through Home Assistant's supported `frontend.add_extra_js_url()` API, so no manual Lovelace resource entry is required.
- `PanelManifest.spec.app_shell.active` explicitly selects the active central surface and app-shell composition participates in `renderer_engine_sha256` / deterministic RenderTrace output.
- Infrastructure panel `0.7.0` becomes a single operational overview with `app_shell.active: infrastructure`; the central top-level `Диагностика` view is removed as detailed diagnostics move to integration-owned panels.
- Generator/runtime app-shell transformer parity, manifest schema packaging, frontend asset presence and infrastructure single-view ownership boundary are regression-tested.
# 0.36.5

- Base UI `0.37.4` records the active NikaS base route before a specialized panel opens, using the standard v1.7 one-shot handoff key. Specialized title plaques can therefore return explicitly to «Дом сейчас», «Действия» or «Инфраструктура» without browser-history navigation.
# 0.36.6

- House UI `0.37.5` evaluates climate entities in one pass and separates explicit `unknown`/`unavailable` from missing state records. Missing records no longer create a false orange climate warning; active heating/cooling remains yellow, confirmed unavailable stays orange, healthy idle climate is green, and a fully unresolved group is grey with `—`. The lower resource row is compacted without sub-12 px copy, and house-water availability now follows the verified irrigation-mainline pressure sensor instead of the drinking-water range.

# 0.36.7

- House UI `0.37.6` replaces the lower three-line icon cards with four text-only colour-state plaques. Mobile geometry remains a readable 2×2 grid with 16 px labels and 48 px minimum touch targets; routes and factual state evaluation are unchanged.

# 0.36.8

- House UI `0.37.7` separates windows and doors in the five-item top status row, moves protection beside weather, and moves cameras beside the date/time card. Resource navigation delegates directly to the LIDER, ZONT and Keenetic owner panels; main navigation uses the approved panel names.

# 0.36.9

- House UI `0.37.8` adds the `Помещения` global bottom-navigation item and connects it to `/dashboard-rooms/rooms`. The navigation fallback, runtime registry and specialized-panel source-route handoff use the same canonical route.

# 0.36.10

- Rooms UI `10.8.19` adopts the current fixed NikaS shell while preserving all existing room cards, entities and detail routes.
