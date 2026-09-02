# Repository scope: registry and shared assets

## Decision

`NikaSir/ha-contract-generated-ui` is a retained service integration. It captures and
downloads scrubbed Home Assistant registry snapshots, validates preserved source data
and serves retained shared assets. It owns no runtime dashboard.

The accepted main House panel is owned by `NikaSir/ha-nikas-house`. Rooms, Access and
all device/domain panels remain owned by their dedicated repositories.

## Route ownership

| Route | Owner | Contract Generated UI rule |
|---|---|---|
| `/dashboard-house` | Existing YAML | Preserve unchanged |
| `/dashboard-house-v11/home` | Existing owner | Do not register or remove |
| `/dashboard-house-v12/home` | Historical Contract Generated UI route | Retired; do not register |
| `/dashboard-house-v13/home` | `ha-nikas-house` | External owner; do not modify |
| Other NikaS routes | Their dedicated integrations or YAML | External owners; do not modify |

## Preservation

The exact pre-split multi-panel state is commit
`c525b30991ce7a52b2b3aeba876d65fc7ba97685` on
`archive/multipanel-0.37.8`. The final Contract Generated UI House state is commit
`f5bff81` on the default branch history.

The integration must never clean private inventory, snapshots, generated history,
user-supplied assets or Home Assistant YAML dashboard files. Historical House source
may remain in Git for traceability but is not imported or registered at runtime.

## Runtime boundary

- Allowed: registry capture, authenticated snapshot download, source validation and
  serving the retained assets directory.
- Forbidden: panel registration, Lovelace generation from an entity button, global
  frontend injection, route replacement or unloading a route owned by another project.
