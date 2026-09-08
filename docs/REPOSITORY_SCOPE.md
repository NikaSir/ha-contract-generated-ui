# Repository scope: common registry and contracts

## Decision

`NikaSir/ha-contract-generated-ui` is the common NikaS service and knowledge base.
It captures and downloads scrubbed Home Assistant registry snapshots, validates
contract sources, publishes shared schemas and standards, and synchronizes the
canonical route registry. It owns no runtime dashboard.

Panel contracts, manifests, renderers, frontend bundles, artwork and panel-specific
tests belong to their dedicated repositories. The accepted main House panel is owned
by `NikaSir/ha-nikas-house`.

## Route ownership

| Route | Owner | Contract Generated UI rule |
|---|---|---|
| `/dashboard-house` | Existing YAML | Preserve unchanged |
| `/dashboard-house-v11/home` | Existing owner | Do not register or remove |
| `/dashboard-house-v12/home` | Historical Contract Generated UI route | Retired; do not register |
| `/dashboard-house-v13/home` | `ha-nikas-house` | Registry reference only |
| Other NikaS routes | Dedicated integrations or YAML | Registry reference only |

## Preservation

The exact pre-split multi-panel state is commit
`c525b30991ce7a52b2b3aeba876d65fc7ba97685` on
`archive/multipanel-0.37.8`. The final Contract Generated UI House state is commit
`f5bff81` in the default-branch history.

The integration must never clean user-owned inventory, snapshots, generated history,
contracts, manifests, assets or Home Assistant YAML dashboards. Version 0.40 merely
stops packaging and synchronizing the historical House sources; existing runtime
copies are preserved.

## Runtime boundary

- Allowed: registry capture, authenticated snapshot download, generic source
  validation and common navigation-registry synchronization.
- Forbidden: panel registration, Lovelace generation from a Home Assistant entity,
  global frontend injection, panel asset serving, route replacement or unloading a
  route owned by another project.
