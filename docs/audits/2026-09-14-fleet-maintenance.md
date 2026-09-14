# Fleet maintenance — 2026-09-14

This record covers the confirmed repository maintenance backlog from the 2026-09-14 audit. It records repository changes and source snapshots; it does not certify live Home Assistant, mobile clients, or devices.

## Changes merged before this snapshot

- `ha-nikas-dyson`: [PR #5](https://github.com/NikaSir/ha-nikas-dyson/pull/5), [PR #6](https://github.com/NikaSir/ha-nikas-dyson/pull/6), [PR #7](https://github.com/NikaSir/ha-nikas-dyson/pull/7), [PR #8](https://github.com/NikaSir/ha-nikas-dyson/pull/8), [PR #9](https://github.com/NikaSir/ha-nikas-dyson/pull/9), [PR #10](https://github.com/NikaSir/ha-nikas-dyson/pull/10).
- `ha-contract-generated-ui`: [PR #168](https://github.com/NikaSir/ha-contract-generated-ui/pull/168), [PR #173](https://github.com/NikaSir/ha-contract-generated-ui/pull/173).
- `ha-s8-omni`: [PR #136](https://github.com/NikaSir/ha-s8-omni/pull/136).
- `ha-vless-gateway`: [PR #25](https://github.com/NikaSir/ha-vless-gateway/pull/25).
- `ha-lider-voltage-control`: [PR #49](https://github.com/NikaSir/ha-lider-voltage-control/pull/49).
- `ha-starline-telemetry`: [PR #61](https://github.com/NikaSir/ha-starline-telemetry/pull/61).
- `ha-zont`: [PR #35](https://github.com/NikaSir/ha-zont/pull/35).
- `ha-hikvision-next`: [PR #5](https://github.com/NikaSir/ha-hikvision-next/pull/5).
- `ha-nikas-climate`: [PR #22](https://github.com/NikaSir/ha-nikas-climate/pull/22).
- `ha-water-accounting`: [PR #8](https://github.com/NikaSir/ha-water-accounting/pull/8).
- `ha-nikas-access`: [PR #15](https://github.com/NikaSir/ha-nikas-access/pull/15).
- `ha-nikas-rooms`: [PR #9](https://github.com/NikaSir/ha-nikas-rooms/pull/9).
- `.github`: [PR #13](https://github.com/NikaSir/.github/pull/13).

The initial seven dependency PRs (Dyson #5–#10 and toolkit #168) are merged. The four incomplete HA validation configurations now include HACS and Hassfest behind their required gate: Access, Rooms, S8 OMNI, and HA-VLESS. S8 retains its independently required browser regression. Support files were completed in nine repositories, including this fleet's `.github` repository. The shared publication contract and its pinned mirror now recognize the scoped HACS release exception.

S8 manifest key ordering and Rooms package metadata were reconciled without introducing a runtime release. The profile bindings for Keenetic, LIDER, Climate, and Stark were reconciled with their actual registered artifacts in PR #173. CI success is repository evidence only; existing pending acceptance statuses are preserved.

## Source snapshots

Each full SHA below is the reviewed snapshot recorded in the registry. A profile is not a moving pointer to `main`. The toolkit's own profile intentionally points to the accepted parent revision `0cf8e7c19f2db1b0eccbbf30465f167c15858c24`, before this snapshot-only follow-up. The `.github` contract mirror is pinned to that same accepted contract revision; the contract text is unchanged by this follow-up.

| Repository | Source revision |
|---|---|
| `.github` | [`e727728d3bda7d8d137627070ed611c0042684fc`](https://github.com/NikaSir/.github/commit/e727728d3bda7d8d137627070ed611c0042684fc) |
| `ha-contract-generated-ui` | [`0cf8e7c19f2db1b0eccbbf30465f167c15858c24`](https://github.com/NikaSir/ha-contract-generated-ui/commit/0cf8e7c19f2db1b0eccbbf30465f167c15858c24) |
| `ha-hikvision-next` | [`e16247b68202a44c37a01d16dbdcac555348c6d8`](https://github.com/NikaSir/ha-hikvision-next/commit/e16247b68202a44c37a01d16dbdcac555348c6d8) |
| `ha-ho-sc-8w` | [`8e4e1bf755105a3bef88ca6bfa04175bc5c5d4c6`](https://github.com/NikaSir/ha-ho-sc-8w/commit/8e4e1bf755105a3bef88ca6bfa04175bc5c5d4c6) |
| `ha-keenetic-hero-4g` | [`40668e90b71484baba2dd2279aa1281e2be3cd8c`](https://github.com/NikaSir/ha-keenetic-hero-4g/commit/40668e90b71484baba2dd2279aa1281e2be3cd8c) |
| `ha-lider-voltage-control` | [`d7144749882cd008537b633a74b3e3eaeea8c871`](https://github.com/NikaSir/ha-lider-voltage-control/commit/d7144749882cd008537b633a74b3e3eaeea8c871) |
| `ha-nikas-access` | [`faa60f8f11262288a9cafe84271c7ee21354c7f5`](https://github.com/NikaSir/ha-nikas-access/commit/faa60f8f11262288a9cafe84271c7ee21354c7f5) |
| `ha-nikas-climate` | [`34e9bfadcc8fa47bb9298be784d86c280740d1ef`](https://github.com/NikaSir/ha-nikas-climate/commit/34e9bfadcc8fa47bb9298be784d86c280740d1ef) |
| `ha-nikas-dyson` | [`2a246b263ad3fb0398a4ee662e0c1e7a0ffeaae9`](https://github.com/NikaSir/ha-nikas-dyson/commit/2a246b263ad3fb0398a4ee662e0c1e7a0ffeaae9) |
| `ha-nikas-house` | [`97f7d137f54c891a6acea69d84aa2da9de2ae453`](https://github.com/NikaSir/ha-nikas-house/commit/97f7d137f54c891a6acea69d84aa2da9de2ae453) |
| `ha-nikas-rooms` | [`fc668b80790973a57f9f701f2bb1aab6b5c99161`](https://github.com/NikaSir/ha-nikas-rooms/commit/fc668b80790973a57f9f701f2bb1aab6b5c99161) |
| `ha-s8-omni` | [`0780c62f793f95bd941d4b377dfcf2724168342e`](https://github.com/NikaSir/ha-s8-omni/commit/0780c62f793f95bd941d4b377dfcf2724168342e) |
| `ha-stark-solarpower` | [`331a7dcad89cc8e85d9a4c93f200828175c022db`](https://github.com/NikaSir/ha-stark-solarpower/commit/331a7dcad89cc8e85d9a4c93f200828175c022db) |
| `ha-starline-telemetry` | [`6fe4277404447e476f7ed7a95e376de0a8f5e26e`](https://github.com/NikaSir/ha-starline-telemetry/commit/6fe4277404447e476f7ed7a95e376de0a8f5e26e) |
| `ha-vless-gateway` | [`532d45fecd5cd7622be875437da02ff6060252f8`](https://github.com/NikaSir/ha-vless-gateway/commit/532d45fecd5cd7622be875437da02ff6060252f8) |
| `ha-water-accounting` | [`16638bb52262f0780fc7add44aba4a32a05e4bd9`](https://github.com/NikaSir/ha-water-accounting/commit/16638bb52262f0780fc7add44aba4a32a05e4bd9) |
| `ha-zont` | [`c1cf209562850ccb9b42fec7fb2fafb6a7940016`](https://github.com/NikaSir/ha-zont/commit/c1cf209562850ccb9b42fec7fb2fafb6a7940016) |
| `vless-gateway` | [`aa4a0a9f04d084043cabe7b5d0aef3157ca39940`](https://github.com/NikaSir/vless-gateway/commit/aa4a0a9f04d084043cabe7b5d0aef3157ca39940) |

## Remaining administrative and acceptance work

The active Protect main rulesets already require PRs, resolved conversations, linear history, squash-only merges, required checks, and deletion/force-push protection. The current connector cannot mutate repository Administration settings. General settings in 17 repositories still allow merge/rebase and do not automatically delete merged head branches; Dyson is already aligned. These four General settings remain an explicit administrative item. Existing main rulesets already constrain merges to squash.

Enabling Dependabot in the nine newly covered repositories generated a new maintenance queue. Those new proposals, including dependency major upgrades, require their own review and are not included in the original seven-PR batch.

The S8 [research draft #102](https://github.com/NikaSir/ha-s8-omni/pull/102) and irrigation [lab draft #22](https://github.com/NikaSir/ha-ho-sc-8w/pull/22) retain their original heads and draft status. Device and live Home Assistant acceptance remains pending. The approved beta direction for irrigation, S8, Climate, LIDER, and Keenetic remains distinct from implemented delivery, as recorded in [BETA_RELEASE_ADOPTION.md](../BETA_RELEASE_ADOPTION.md); this maintenance batch creates no releases or tags.

Correction to the external initial audit: irrigation's publication profile already declared `github_releases=true` and `automatic_tags=true`; that profile was not changed to enable releases. S8's profile was corrected to reflect its existing manual releases (`true/false`).

## Verification

Each merged maintenance PR received an independent review and passed required CI before protected squash merge. The final snapshot refresh runs the toolkit regression suite, schema validation, and normal required CI. The final external report records post-merge main checks and the administrative handoff. These checks do not turn pending runtime evidence into accepted device behavior.

