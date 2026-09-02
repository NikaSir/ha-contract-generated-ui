# Changelog

## Unreleased — 0.38.2

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
