# Dependabot maintenance — 2026-09-14

This record covers the 27 dependency PRs generated after the [preceding fleet maintenance](2026-09-14-fleet-maintenance.md). The owner authorized continuing the remediation. All 27 are resolved: 26 merged through protected squash PRs, and the coverage-only Hikvision PR #8 closed because its compatible update is included in #9.

## Reviewed changes and validation

- 24 GitHub Actions updates change action major-version references only. Workflow permissions, triggers, inputs and required gates are preserved. Hosted PR checks passed on the reviewed heads before merge.
- The v7 action READMEs were reviewed for runner requirements and behavior changes. The updated checkout workflows do not use `pull_request_target` or `workflow_run` with untrusted fork checkouts. Existing explicit Python/Node runtime selections remain in place.
- Climate #25 exercised `actions/upload-artifact@v7` in the successful UI geometry workflow, including artifact upload. This is execution evidence, not only workflow syntax inspection.
- Overlapping updates were rebased or merged with their accepted base, reviewed again and checked again before squash merge. No force push or ruleset bypass was used.
- Local execution was unavailable because the workspace failed to initialize. Validation was performed by the repositories' hosted GitHub Actions; no local test run is claimed.

## Hikvision compatibility corrections

The original test-helper update required Python 3.14 and could not install on the existing Python 3.12 runner. The original coverage update also conflicted with the legacy Home Assistant helper's coverage pin. [PR #9](https://github.com/NikaSir/ha-hikvision-next/pull/9) keeps Python 3.12 and adds a required Python 3.14 matrix leg, with environment-specific helper and coverage requirements. The observed environments resolve to Home Assistant 2025.1.4 and 2026.9.2 respectively. The current camera import dependency PyTurboJPEG 1.8.3 and its system library are installed in the modern leg.

The current HA test environment forbids external DNS. A spoofed-notification regression previously depended on a live lookup of a fixture hostname. It now provides deterministic DNS at the socket boundary while preserving the real source matching and all assertions: HTTP 403, unchanged sensor state and no event emission. Production notification code is unchanged.

[PR #10](https://github.com/NikaSir/ha-hikvision-next/pull/10) pairs `xmltodict==1.0.4` in test requirements and the runtime manifest, and advances the integration version from 1.1.7 to 1.1.8. The dependency-only proposal previously tested a different parser from the one Home Assistant would install. A new test compares installed distributions with every applicable manifest requirement. Its [red test run](https://github.com/NikaSir/ha-hikvision-next/actions/runs/34849878243/job/103994820508) demonstrated the original mismatch: CI installed 1.0.4 while the manifest required 0.13.0. The paired change passes the full matrix, including existing parsing, notification, switch and exact outgoing XML payload regressions: [Python 3.12](https://github.com/NikaSir/ha-hikvision-next/actions/runs/34850887238/job/103998244195) reports 110 passed and 1 pre-existing skip; [Python 3.14](https://github.com/NikaSir/ha-hikvision-next/actions/runs/34850887238/job/103998244175) reports 111 passed.

The XML parser changelog was reviewed against actual parse/unparse use; the integration does not enable the changed `process_namespaces=True` mode. No tags or GitHub Releases were created. HACS installation and real-camera/NVR acceptance of 1.1.8 remain pending.

Primary references: [test-helper Python requirement](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/blob/169b9d563d8a3e4739668fd427b596bfefbc0dfb/setup.py), [HA camera requirements](https://github.com/home-assistant/core/blob/2026.9.2/homeassistant/components/camera/manifest.json), [Ubuntu JPEG package](https://packages.ubuntu.com/source/noble/libjpeg-turbo), [xmltodict changelog](https://github.com/martinblech/xmltodict/blob/v1.0.4/CHANGELOG.md).

## PR dispositions

| PR | Original update | Result |
|---|---|---|
| [.github#14](https://github.com/NikaSir/.github/pull/14) | chore(deps): bump actions/setup-python from 5 to 7 | Merged (squash) |
| [.github#15](https://github.com/NikaSir/.github/pull/15) | chore(deps): bump actions/checkout from 4 to 7 | Merged (squash) |
| [ha-hikvision-next#6](https://github.com/NikaSir/ha-hikvision-next/pull/6) | Bump actions/checkout from 3 to 7 | Merged (squash) |
| [ha-hikvision-next#7](https://github.com/NikaSir/ha-hikvision-next/pull/7) | Bump actions/setup-python from 5 to 7 | Merged (squash) |
| [ha-hikvision-next#8](https://github.com/NikaSir/ha-hikvision-next/pull/8) | Update pytest-cov requirement from >=4.1.0 to >=7.1.0 | Closed; incorporated into #9 |
| [ha-hikvision-next#9](https://github.com/NikaSir/ha-hikvision-next/pull/9) | Update pytest-homeassistant-custom-component requirement from >=0.13.179 to >=0.13.364 | Merged (squash) |
| [ha-hikvision-next#10](https://github.com/NikaSir/ha-hikvision-next/pull/10) | Bump xmltodict from 0.13.0 to 1.0.4 | Merged (squash) |
| [ha-lider-voltage-control#50](https://github.com/NikaSir/ha-lider-voltage-control/pull/50) | Bump actions/setup-node from 4 to 7 | Merged (squash) |
| [ha-lider-voltage-control#51](https://github.com/NikaSir/ha-lider-voltage-control/pull/51) | Bump actions/setup-python from 5 to 7 | Merged (squash) |
| [ha-lider-voltage-control#52](https://github.com/NikaSir/ha-lider-voltage-control/pull/52) | Bump actions/checkout from 4 to 7 | Merged (squash) |
| [ha-nikas-access#16](https://github.com/NikaSir/ha-nikas-access/pull/16) | build(deps): bump actions/setup-node from 4 to 7 | Merged (squash) |
| [ha-nikas-access#17](https://github.com/NikaSir/ha-nikas-access/pull/17) | build(deps): bump actions/checkout from 4 to 7 | Merged (squash) |
| [ha-nikas-access#18](https://github.com/NikaSir/ha-nikas-access/pull/18) | build(deps): bump actions/setup-python from 5 to 7 | Merged (squash) |
| [ha-nikas-climate#23](https://github.com/NikaSir/ha-nikas-climate/pull/23) | Bump actions/checkout from 4 to 7 | Merged (squash) |
| [ha-nikas-climate#24](https://github.com/NikaSir/ha-nikas-climate/pull/24) | Bump actions/setup-node from 4 to 7 | Merged (squash) |
| [ha-nikas-climate#25](https://github.com/NikaSir/ha-nikas-climate/pull/25) | Bump actions/upload-artifact from 4 to 7 | Merged (squash) |
| [ha-nikas-climate#26](https://github.com/NikaSir/ha-nikas-climate/pull/26) | Bump actions/setup-python from 5 to 7 | Merged (squash) |
| [ha-nikas-rooms#10](https://github.com/NikaSir/ha-nikas-rooms/pull/10) | Bump actions/checkout from 4 to 7 | Merged (squash) |
| [ha-nikas-rooms#11](https://github.com/NikaSir/ha-nikas-rooms/pull/11) | Bump actions/setup-python from 5 to 7 | Merged (squash) |
| [ha-nikas-rooms#12](https://github.com/NikaSir/ha-nikas-rooms/pull/12) | Bump actions/setup-node from 4 to 7 | Merged (squash) |
| [ha-starline-telemetry#62](https://github.com/NikaSir/ha-starline-telemetry/pull/62) | chore(deps): bump actions/setup-python from 5 to 7 | Merged (squash) |
| [ha-starline-telemetry#63](https://github.com/NikaSir/ha-starline-telemetry/pull/63) | chore(deps): bump actions/checkout from 4 to 7 | Merged (squash) |
| [ha-water-accounting#9](https://github.com/NikaSir/ha-water-accounting/pull/9) | Bump actions/checkout from 4 to 7 | Merged (squash) |
| [ha-water-accounting#10](https://github.com/NikaSir/ha-water-accounting/pull/10) | Bump actions/setup-python from 5 to 7 | Merged (squash) |
| [ha-water-accounting#11](https://github.com/NikaSir/ha-water-accounting/pull/11) | Bump actions/setup-node from 4 to 7 | Merged (squash) |
| [ha-zont#36](https://github.com/NikaSir/ha-zont/pull/36) | Bump actions/setup-node from 6 to 7 | Merged (squash) |
| [ha-zont#37](https://github.com/NikaSir/ha-zont/pull/37) | Bump actions/checkout from 6 to 7 | Merged (squash) |

## Verified consumer main revisions

All listed main heads were read back after merge and their latest check results were successful. Central consumer profiles and their existing reconciliation fixtures are advanced to these exact revisions. UI artifact paths, versions and bindings are preserved. The canonical repository's self-profile points to accepted parent `759d13f714380972e3b3219dff7cfa3a49f14a2a`; a profile cannot pin its own future containing commit.

| Repository | Accepted main | Validation |
|---|---|---|
| .github | [`974b606a524cfbfc4eddd4df649821d112e7c425`](https://github.com/NikaSir/.github/commit/974b606a524cfbfc4eddd4df649821d112e7c425) | [CI 1](https://github.com/NikaSir/.github/actions/runs/34849431281): success |
| ha-hikvision-next | [`16f058095019bfbca571dc5e7e13fd1d7ded41d6`](https://github.com/NikaSir/ha-hikvision-next/commit/16f058095019bfbca571dc5e7e13fd1d7ded41d6) | [CI 1](https://github.com/NikaSir/ha-hikvision-next/actions/runs/34851207346), [CI 2](https://github.com/NikaSir/ha-hikvision-next/actions/runs/34851207251): success |
| ha-lider-voltage-control | [`03dcc945f22f2d8506d1db857706748198566e88`](https://github.com/NikaSir/ha-lider-voltage-control/commit/03dcc945f22f2d8506d1db857706748198566e88) | [CI 1](https://github.com/NikaSir/ha-lider-voltage-control/actions/runs/34848925014), [CI 2](https://github.com/NikaSir/ha-lider-voltage-control/actions/runs/34848925016): success |
| ha-nikas-access | [`29ad98ac191d210f36c75ed2fde24844637efaf4`](https://github.com/NikaSir/ha-nikas-access/commit/29ad98ac191d210f36c75ed2fde24844637efaf4) | [CI 1](https://github.com/NikaSir/ha-nikas-access/actions/runs/34849416255): success |
| ha-nikas-climate | [`1c98b256df93a6793708a9462eef392ff1cdf858`](https://github.com/NikaSir/ha-nikas-climate/commit/1c98b256df93a6793708a9462eef392ff1cdf858) | [CI 1](https://github.com/NikaSir/ha-nikas-climate/actions/runs/34848970970): success |
| ha-nikas-rooms | [`ed3f7e50b2c9756fddd9f2a79dc14f82f09e8fdc`](https://github.com/NikaSir/ha-nikas-rooms/commit/ed3f7e50b2c9756fddd9f2a79dc14f82f09e8fdc) | [CI 1](https://github.com/NikaSir/ha-nikas-rooms/actions/runs/34849551054): success |
| ha-starline-telemetry | [`ecbe026ba7e785265c3d2a746e97d529998443d8`](https://github.com/NikaSir/ha-starline-telemetry/commit/ecbe026ba7e785265c3d2a746e97d529998443d8) | [CI 1](https://github.com/NikaSir/ha-starline-telemetry/actions/runs/34849421421): success |
| ha-water-accounting | [`889c22f44ce56559eede919099340c48ead1c386`](https://github.com/NikaSir/ha-water-accounting/commit/889c22f44ce56559eede919099340c48ead1c386) | [CI 1](https://github.com/NikaSir/ha-water-accounting/actions/runs/34849018177), [CI 2](https://github.com/NikaSir/ha-water-accounting/actions/runs/34849018233): success |
| ha-zont | [`9ca0f4eb6b4a9c8ab7e128ed75560e48c38e19e3`](https://github.com/NikaSir/ha-zont/commit/9ca0f4eb6b4a9c8ab7e128ed75560e48c38e19e3) | [CI 1](https://github.com/NikaSir/ha-zont/actions/runs/34849426365): success |

This follow-up changes registry evidence and audit documentation, not the normative contract text, so the previously reconciled `.github` standard mirror does not need another content refresh. Runtime/device acceptance evidence remains pending.

## Remaining boundaries and work

- General settings readback still shows 17 repositories with `allow_merge_commit=true`, `allow_rebase_merge=true` and `delete_branch_on_merge=false`. Dyson alone has squash-only and automatic branch deletion. The connection does not provide Administration writes; the previously supplied owner-run `NikaS_apply_general_settings_2026-09-14.sh` remains the concrete remediation. No settings change is claimed here.
- Affected General settings repositories: `ha-contract-generated-ui`, `ha-hikvision-next`, `ha-ho-sc-8w`, `ha-keenetic-hero-4g`, `ha-lider-voltage-control`, `ha-nikas-access`, `ha-nikas-climate`, `ha-nikas-house`, `ha-nikas-rooms`, `ha-s8-omni`, `ha-stark-solarpower`, `ha-starline-telemetry`, `ha-vless-gateway`, `ha-water-accounting`, `ha-zont`, `.github`, `vless-gateway`.
- The reviewed main rulesets remain active with required checks, resolved review conversations, linear history and squash merging. Existing strictness settings were preserved.
- Research drafts [S8 #102](https://github.com/NikaSir/ha-s8-omni/pull/102) and [HO-SC-8W #22](https://github.com/NikaSir/ha-ho-sc-8w/pull/22) were not merged or edited. Their physical acceptance prerequisites remain.
- The new Hikvision HA 2026.9 test environment logs a separate deprecation warning: existing sensor entity IDs are normalized by HA today but must be corrected before HA 2027.2. This pre-existing runtime compatibility work is not treated as resolved by dependency CI.
- CI success does not establish installation on the owner's Home Assistant or acceptance on devices. No hardware operations were performed.
