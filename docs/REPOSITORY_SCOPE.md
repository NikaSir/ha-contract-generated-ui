# Repository scope: main House only

## Decision

`NikaSir/ha-contract-generated-ui` owns only the new main **Дом** overview. It must not implement or register Rooms, Actions, Infrastructure or any detailed control panel.

The existing configured YAML dashboards remain the working baseline in Home Assistant. The split does not rename, overwrite, unload or delete them.

## Ownership matrix

| Route | Status | Rule |
|---|---|---|
| `/dashboard-house` | Existing YAML | Preserve unchanged |
| `/dashboard-house-v11/home` | New main House | Owned here |
| `/dashboard-rooms/rooms` | Existing YAML | External link until a separate Rooms repository is accepted |
| `/dashboard-actions/home` | Existing YAML | External link until a separate Actions repository is accepted |
| `/dashboard-infrastructure/overview` | Existing YAML | External link until a separate Infrastructure repository is accepted |
| Device-specific routes | Separate integrations | Always externally owned |

## Preservation

The exact multi-panel code state before the split is commit `c525b30991ce7a52b2b3aeba876d65fc7ba97685` on `archive/multipanel-0.37.8`.

This repository may clean only its own packaged contracts, manifests, frontend bundles and fallback registrations. It must never clean private inventory, snapshots, generated history or Home Assistant YAML dashboard files.

## New detailed-panel workflow

1. Create a dedicated repository when work on a detailed panel starts.
2. Give it a unique preview route that does not collide with the existing YAML route.
3. Keep its contracts, manifest, frontend, assets and tests inside that repository.
4. Test the preview on the target phone while the YAML dashboard remains available.
5. Change the House navigation URL only after the new panel is accepted.
6. Retain the YAML panel as a rollback path until its retirement is explicitly approved.

## Cross-repository boundary

- Navigation by explicit URL is allowed.
- Copying an approved UI pattern at development time is allowed.
- Importing JavaScript, Python, assets or manifests from another panel repository at runtime is forbidden.
- One repository must never unload or replace a route owned by another repository or by Lovelace YAML.
