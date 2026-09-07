# NikaS CI gate: first consumer migration

The first migration addresses audit finding A21 in the canonical repository,
House and StarLine. Their former HACS, Hassfest and code-check workflows each
reported the same `validate` context. The new workflow gives each check a unique
name and retains a single `validate` job as their aggregate result.

| Repository | Dependencies of `validate` |
|---|---|
| `ha-contract-generated-ui` | `repository-checks`, `hacs`, `hassfest`, `nikas-contract-toolkit` |
| `ha-nikas-house` | `repository-checks`, `hacs`, `hassfest` |
| `ha-starline-telemetry` | `repository-checks`, `hacs`, `hassfest` |

All dependencies live in the same workflow. The aggregate runs with `always()`
and accepts only the exact expected set of results with every result equal to
`success`. Failed, cancelled, skipped, absent and unexpected results are rejected.
The aggregate does not check out the application or run its code.

Existing validation steps, action references and action inputs are preserved.
All earlier triggers are retained: push and pull request, the existing manual
dispatch in canonical/House, and StarLine's Monday 03:00 UTC schedule. Manual
dispatch is also added to StarLine. The union runs code/HACS checks on events
that previously ran only Hassfest.

## Required checks and scope

At the 2026-09-07 inspection, canonical ruleset `21137817` required the
`validate` context from GitHub Actions (`integration_id: 15368`). The migration
keeps that context and gives it one unambiguous producer. GitHub settings do not
need to change for this step.

House and StarLine had no main protection/rulesets at that inspection. Adding
this workflow provides a reliable aggregate check; it does not itself make
the check mandatory. Enabling and reading back protection remains a separate
adoption item. Do not claim that their merges are already blocked by this gate.

The manual strict fleet workflow remains separate. A green `validate` result
means the included automated checks passed. It does not close product findings,
certify UI v2.2 behavior or establish HA/iPhone acceptance. The initial factual
profiles and audit baseline keep their original source revisions; they are not
rewritten to report compliance from CI restructuring alone.

The active House panel and its two extra frontend modules are already covered
by its existing syntax/build checks. StarLine already checks its active
`starline-app.js` bundle and its registration/build bindings. This migration
changes neither those delivered artifacts nor their approved interface.

## Verification and follow-up

`tests/test_ci_gate.py` exercises the actual aggregate shell step with successful
and unsuccessful dependency results, checks that every validation job is a
dependency, and rejects duplicate job contexts across workflows. It can inspect
the same convention in a consumer checkout:

```bash
NIKAS_CI_WORKFLOW_PATH=/path/to/consumer/.github/workflows/repository-checks.yml \
  python -m pytest -q tests/test_ci_gate.py
```

During this migration, the harness rejected 34 negative result combinations for
the canonical gate and 26 for each three-dependency consumer gate, and accepted
the complete-success case in each. Existing repository tests and actual GitHub
Actions runs are still required before merging each PR.

After merging, update or recreate dependency PRs that target removed workflow
files. The existing Dependabot PRs were not merged or closed by this migration.
Continue with consumer protection/local contract adoption and focused fixes for
command validation, stale or missing data, and lifecycle defects. Refresh each
factual profile only after verifying its new source revision and evidence.
