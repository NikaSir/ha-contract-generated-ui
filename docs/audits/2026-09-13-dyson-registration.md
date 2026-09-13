# Dyson specialized panel registration — 2026-09-13

Registered [NikaSir/ha-nikas-dyson](https://github.com/NikaSir/ha-nikas-dyson) in the central factual inventory at production `b14fc882d6c21ee92099461a85e74f8972d58cca`: integration **0.1.5**, UI **1.0.2**. This extends the registry from 17 to 18 repositories; the historical September 7 baseline is unchanged.

[Product PR #1](https://github.com/NikaSir/ha-nikas-dyson/pull/1) and [MIT PR #2](https://github.com/NikaSir/ha-nikas-dyson/pull/2) were squash merged. [Post-merge push run](https://github.com/NikaSir/ha-nikas-dyson/actions/runs/34744161836) passed repository-checks, HACS, Hassfest and validate. HACS retains the explicit `topics` exception for a custom repository. MIT, repository description and the NikaS brand asset are present.

[Active Protect main ruleset 23096960](https://github.com/NikaSir/ha-nikas-dyson/rules/23096960) requires a pull request and strict `validate` from GitHub Actions (integration 15368), blocks deletion and force pushes, and has no bypass actors. This is a point-in-time observation, not continuous enforcement verification by the offline inspector.

| Finding | Original issue | Reconciliation |
| --- | --- | --- |
| A34 | Failed snapshot left cached status apparently live | Stale status and cleared live power/activity; failure/recovery browser regression |
| A35 | Importing v101 patch was not autonomous | One deterministic production bundle and delivery checks |
| A36 | Source selection and explicit calibration unavailable | Options flow and 22 behavioral option tests |
| A37 | Specialized shell/refresh/lifecycle and central profile absent | Canonical shell, lifecycle/refresh/zoom regressions and this registration |
| A38 | No behavioral CI/HACS or main protection | Aggregate validate, tests, HACS/Hassfest, MIT/metadata and active ruleset |
| A39 | README version diverged from production | Integration 0.1.5 / UI 1.0.2 and binding/version regression coverage |

All six findings are `fixed_pending_verification`. Every acceptance evidence entry remains `pending`; device acceptance has no evidence paths. Product tests (25 Python and 7 browser scenarios) use mocked Home Assistant boundaries/responses. No installed Home Assistant, physical appliance calibration or iPhone acceptance is claimed.

Central reconciliation followed RED → GREEN: the registry and new profile test failed on the previous central main because Dyson was absent, then passed after registration. The full suite passed with 208 tests and 61 subtests. Profile schema validation passed.

The [offline inspection report](2026-09-13-dyson-registration.json) was generated from a clean Dyson production checkout using central authority revision `46e4d37d3bbdc9dbb4f5fd01627fa7c0ed564e92`. It confirms the source identity, artifact paths, all four version/registration bindings and normative document hashes. Its overall result is **not_verified**, not a compliance pass: it does not execute builds, prove runtime registration, validate shell behavior or substitute for live/device acceptance.
