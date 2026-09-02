# Changelog

## Unreleased

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
