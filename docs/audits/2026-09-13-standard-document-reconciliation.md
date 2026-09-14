# Standard document governance reconciliation — 2026-09-13

Seven repositories contained standard/navigation document drift that existing required CI did not reject. Each product fix synchronizes the documents and linked companions to central authority `000afbcec2ed16e5b9611a7a96d8d845e307e5d9` and enforces independently pinned bytes in required CI. Ruleset contexts and runtime files are preserved.

| Finding | Repository / PR | Production revision | Post-merge CI |
|---|---|---|---|
| A40 | [ha-nikas-rooms #7](https://github.com/NikaSir/ha-nikas-rooms/pull/7) | `03ee44f56459e2356f7680e5498858d0973000c5` | [Validate](https://github.com/NikaSir/ha-nikas-rooms/actions/runs/34766402656) |
| A41 | [ha-keenetic-hero-4g #95](https://github.com/NikaSir/ha-keenetic-hero-4g/pull/95) | `f5c2cb7a74d58559004c5056b51974eb2c5a1c2d` | [Repository checks](https://github.com/NikaSir/ha-keenetic-hero-4g/actions/runs/34766409832), [Frontend bundle](https://github.com/NikaSir/ha-keenetic-hero-4g/actions/runs/34766409819), [Integration validation](https://github.com/NikaSir/ha-keenetic-hero-4g/actions/runs/34766409898) |
| A42 | [ha-s8-omni #133](https://github.com/NikaSir/ha-s8-omni/pull/133) | `32ca842494fc467e71e6bb613e423f2188bfc5f2` | [Repository checks](https://github.com/NikaSir/ha-s8-omni/actions/runs/34766415269) |
| A43 | [ha-starline-telemetry #59](https://github.com/NikaSir/ha-starline-telemetry/pull/59) | `5f4496280d8a23b8761972ddc60ffb08cd056062` | [Repository checks](https://github.com/NikaSir/ha-starline-telemetry/actions/runs/34766422037) |
| A44 | [ha-vless-gateway #23](https://github.com/NikaSir/ha-vless-gateway/pull/23) | `4b78e29157da9f89cc6f3a816fb9f69a9aee757e` | [Repository checks](https://github.com/NikaSir/ha-vless-gateway/actions/runs/34766433761) |
| A45 | [ha-zont #33](https://github.com/NikaSir/ha-zont/pull/33) | `012d1841b7aeee0c6bf40079e61dddabd5840e12` | [Integration validation](https://github.com/NikaSir/ha-zont/actions/runs/34766439288) |
| A46 | [ha-lider-voltage-control #45](https://github.com/NikaSir/ha-lider-voltage-control/pull/45) | `81ac8734ca55c5aaea29cd513b8da7e15ac8d3b9` | [Repository checks](https://github.com/NikaSir/ha-lider-voltage-control/actions/runs/34766445489), [Integration validation](https://github.com/NikaSir/ha-lider-voltage-control/actions/runs/34766445490) |

All listed push workflows succeeded at the exact production revisions. Product tests demonstrated RED on original main and GREEN after synchronization, including document/hash coordinated rollback mutation coverage. The central seven-case reconciliation test separately demonstrated RED before profile updates and GREEN afterward. Central full suite: 215 tests and 61 subtests passed.

S8 production had independently advanced to 1.0.6 through PR #132 before the documentation fix. Its current UI/cache bindings are recorded; this reconciliation does not certify its desktop connection-indicator behavior. Other release versions remain unchanged.

Fresh offline inspection used clean production checkouts. The accompanying JSON retains `not_verified`: document parity and static binding checks pass, but runtime conformance and device acceptance are separate. Findings A40–A46 are `fixed_pending_verification`; all profile acceptance evidence stays `pending`, and device evidence remains empty. Historical audits are preserved.

