# Changelog

## Unreleased

## 0.42.0 — 2026-09-20

- Add the `Проблемы` tab between Summary and Devices, grouping each monitored
  device by its highest-priority issue while retaining secondary issue badges.
- Keep non-essential problem rows in a separate neutral section and show a calm
  empty state when no device needs attention.
- Publish device-availability UI `1.0.0-beta005` with a four-item responsive
  bottom navigation and asset build `b005`.

- Reconcile Entity Availability totals by displaying essential and non-essential
  entities separately, including their online, offline and suppressed counts.
- Keep non-essential failures informational, refine the mobile composition card and
  publish device-availability UI `1.0.0-beta002` with integration `0.41.1`.
- Reconcile factual fleet profiles with reviewed main revisions and current
  Keenetic, LIDER, Climate and Stark UI/cache bindings; keep device acceptance pending.
- Support manually published HACS Releases without enabling undeclared release
  automation, and correct the S8 publication profile to its existing channel.
- Clarify the scoped HACS exception in repository policy and record the approved
  five-integration beta-to-stable transition separately from its implementation.

## 0.41.0 — 2026-09-14

- Add the integration-owned `Доступность устройств` technical panel at
  `/dashboard-device-availability`, returning to the built-in `/home/overview`.
- Use public Entity Availability 0.5.3 group-summary attributes for online,
  offline, stale, battery and signal diagnostics without reading private storage.
- Add problem-first group and entity views, search and filters, Home Assistant
  more-info actions and a contract-compliant black refresh action.
- Preserve the panel route when Entity Availability is absent or unavailable and
  remove only the route registered by this integration during unload.

## 0.40.3 — 2026-09-13

- Navigation Contract 1.3 makes titles open the immediate declared parent, with every main panel returning to the native `/home/overview`.
- Retire query, source hand-off, saved-route and referrer authority for title navigation; preserve internal page hierarchy.
- Package the updated route registry and add executable resolver and parent-graph regression checks.
- Consumer runtime rollout and live acceptance remain separately verified; no central dashboard runtime is introduced.

## 0.40.2 — 2026-09-10

- A19: repository contract inspector 1.0.2 uses the validated declaration and
  normative documents from its own pinned canonical checkout instead of stale
  hard-coded UI/navigation hashes. Consumers cannot supply the target baseline.
- Validate the authority baseline in schema/toolkit CI as well as strict
  inspection, retain its provenance in JSON reports, and add regressions for
  canonical updates, stale copies and consumer self-consistency.
- Keep product behaviour unverified until separate acceptance evidence exists;
  this tooling change does not renumber or migrate consumer integrations.
- Pin the HO-SC-8W, House, Stark and Water profiles to their reviewed UI 2.2
  production revisions, entrypoints and UI versions while keeping live
  HA/browser/iPhone acceptance explicitly unverified.
- Support the owner-approved release-driven HACS publication model in factual
  repository profiles without treating a detected release command as a failure
  or as proof of delivery. Unsupported mixed policies still fail closed.

## 0.40.1 — 2026-09-08

- Add the required NikaS Panel Lifecycle Contract v1.0: configured routes are
  application infrastructure and cannot depend on device/cloud reachability.
- Add machine-readable lifecycle requirements, CI guards and a fleet baseline
  covering every current integration-owned panel.
- Close the Stark SolarPower and StarLine Telemetry startup-order gaps through
  owner-repository fixes that register routes before source startup and enforce the order in CI.

## 0.40.0 — 2026-09-08

- Enforce the repository boundary: this project now ships only the shared route
  registry, schemas, snapshot service, validation and offline common tooling.
- Remove the historical House contract, manifest, renderers, frontend bundle,
  asset, build script and panel-specific regression suite. The House runtime
  remains owned exclusively by `NikaSir/ha-nikas-house`.
- Stop synchronizing bundled House sources into Home Assistant. Existing
  user-owned files under `/config/contract_generated_ui/` are preserved.
- Generalize manifest renderer/template schema fields so owner repositories can
  define their own implementations without central panel-specific enums.

## 0.39.2 — 2026-09-08

- Correct the shared Water Accounting registry entry to the owner route
  `/dashboard-water` with safe return to `/dashboard-house-v13/home`.
- Keep the Water implementation in its dedicated repository; this release changes
  only the common route contract and its validation.

- Consolidate CI into uniquely named validation jobs and one `validate` gate
  that requires every job to succeed. Preserve the existing required context
  and keep manual strict fleet inspection separate from tooling validation.

- Add NikaS Repository Contract v1.0, strict inspection tooling and a factual
  registry of the 17 maintained repositories. Keep unsupported or unverified
  requirements visible; toolkit validation does not certify product readiness.
- Document staged adoption without changing integration/UI versions, runtime
  behaviour, existing required checks or the main/HACS publication policy.

- Aligns the engineering knowledge base and compatibility documents with UI v2.2 and makes that parity a CI requirement.
- Resolves the Bottom Tab Bar icon contradiction in favor of the field-tested 26px geometry.

- Promotes the NikaS Specialized Panel UI Standard to v2.2 and standardizes persistent peer-device selector status lamps from the proven Stark SolarPower implementation: green normal, orange warning, red fault/offline and gray unknown, independently of the selected-button surface.
- Requires fail-closed lamp priority, accessible status text and point-only updates that never rebuild selector or shell DOM.
- Keeps Bottom Tab Bar labels clear of the panel-host edge with an explicit
  `26px` icon, `14px` label line box and reserved lower clearance.
- Promotes the canonical NikaS Specialized Panel UI Standard to v2.1 with a
  host-bound shell, numeric Header/work/Bottom Nav geometry and a mandatory
  phone/tablet/desktop acceptance matrix.
- Adds machine-readable shell dimensions and CI guards, including the correct
  3–5 specialized-tab range; Keenetic's five destinations remain conforming.
- Adds a build-time Shell v2 source kit so each panel can ship the same geometry
  inside its own autonomous bundle without a runtime dependency.
- Updates the canonical base routes to House v13 and Rooms v11, and records
  Access and Water Accounting in the specialized route registry.

## 0.39.1

- Prefixes the Home Assistant and HACS display name with `NikaS`.
- Publishes the local brand icon through a versioned HACS update.

## 0.39.0

- Retires automatic registration of the historical `Дом · новая` panel.
- Removes the dashboard-generation entity from the installed integration.
- Removes the obsolete dashboard-generation button from the entity registry on setup.
- Keeps scrubbed registry capture/download, diagnostics, source validation and the
  retained shared photo/assets path.
- Stops loading global House JavaScript and removes the Lovelace runtime dependency.
- Preserves all private inventory, snapshots, generated history and archived sources.
- Replaces the integration brand icon with the approved NikaS graphite/cyan registry icon.

## 0.38.2

- Restores taps on all route cards inside the House visual scene by reconciling
  their idempotent handlers after every stable state render.
- Bumps the House frontend cache key so installed clients load the corrected
  card interaction code immediately after the integration update.

## 0.38.1

- Preserves an existing YAML owner at `/dashboard-house-v11` and registers the
  autonomous House panel in parallel at `/dashboard-house-v12/home` instead of
  silently omitting it.
- Labels the collision-safe sidebar entry `Дом · новая` so it cannot be confused
  with the preserved YAML panel during phone acceptance.
- Keeps unload ownership exact: only the route actually registered by this
  integration is removed.

## 0.38.0

- Preserved the complete multi-panel `0.37.8` baseline at commit `c525b30` on branch `archive/multipanel-0.37.8`.
- Narrowed the production repository to the single new main **Дом** panel at `/dashboard-house-v11/home`.
- Removed Infrastructure, Actions, Rooms and generated-subpanel registration and implementation from the active branch.
- Stopped global frontend injection into existing YAML dashboards; the shared module now exposes navigation only.
- Kept `/dashboard-house`, `/dashboard-rooms`, `/dashboard-actions` and `/dashboard-infrastructure` as externally owned legacy YAML routes.
- Reduced public runtime sources to one House contract, one House manifest and navigation links.
- Established the rule that every future detailed control panel is built and released from its own repository.

Earlier multi-panel history remains available on `archive/multipanel-0.37.8`.
