# Panel lifecycle fleet baseline — 2026-09-08

Issue: [#48](https://github.com/NikaSir/ha-contract-generated-ui/issues/48)

The audit checks whether an integration-owned route exists independently of the first
physical-device, vendor-cloud or coordinator refresh. Revisions are the audited
default-branch heads; a passing source audit is not hardware acceptance.

| Repository | Audited revision | Registration model | Result |
|---|---|---|---|
| `ha-keenetic-hero-4g` | `1ae8e9d` | Entry runtime and route before non-fatal RCI refresh | PASS |
| `ha-s8-omni` | `0305060` | Route and platforms before non-fatal local refresh | PASS |
| `ha-ho-sc-8w` | `0eb09ac` | Integration-wide panel setup before config-entry transport activation | PASS |
| `ha-stark-solarpower` | `c652e61` | First coordinator refresh before route registration | GAP — owner fix required |
| `ha-starline-telemetry` | `f768c15` | Telemetry mode authenticates, discovers and refreshes before route registration | GAP — owner fix required |
| `ha-nikas-house` | `1a4b6cd` | Route before source-validation refresh | PASS |
| `ha-lider-voltage-control` | `504829e` | Panel-only entry; no device refresh | PASS |
| `ha-nikas-access` | `90ae754` | Panel-only entry; registry-backed content | PASS |
| `ha-nikas-climate` | `d80380d` | Panel-only entry; registry-backed content | PASS |
| `ha-nikas-rooms` | `0d5366b` | Panel-only entry; registry-backed content | PASS |
| `ha-vless-gateway` | `06eb754` | Panel-only entry; no device refresh | PASS |
| `ha-water-accounting` | `40b4be1` | Panel-only entry; registry-backed content | PASS |
| `ha-zont` | `e8f64b8` | Route registered directly during entry setup | PASS |
| `ha-hikvision-next` | `12abd40` | No integration-owned panel | NOT APPLICABLE |

## Acceptance

The two GAP repositories require separate owner PRs with:

- route registration before fallible device/cloud/coordinator I/O;
- explicit startup-order regression coverage;
- no protocol, command or UI behavior change;
- HACS, Hassfest and repository CI success.

Hardware access is not required for these startup-order corrections.
