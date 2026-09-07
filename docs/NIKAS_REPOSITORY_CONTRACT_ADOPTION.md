# Repository contract: first adoption package

This package adds [Repository Contract v1.0](NIKAS_REPOSITORY_CONTRACT.md), its
schema and inspector, and a central inventory of 17 revision-pinned repositories.
The existing UI standard remains v2.2. Product versions and runtime code are not
changed by this package.

## Contents

| File | Responsibility |
|---|---|
| `schemas/nikas_repository_contract.schema.json` | Factual profile format |
| `scripts/nikas_repository_contract.py` | Profile validation and strict inspection |
| `deployments/repository-contracts/*.json` | Source revision, active delivery, observed standard and open evidence for each repository |
| `scripts/checkout_nikas_contract_snapshots.py` | Public Git snapshots at the exact profile revisions |
| `.github/workflows/repository-checks.yml` (`nikas-contract-toolkit` job) | Inspector regression tests and profile-schema checks |
| `.github/workflows/nikas-fleet-inspection.yml` | Manually invoked strict inspection with retained JSON/Markdown results |

The [initial strict baseline](audits/2026-09-07-repository-contract-baseline.md)
records the exact inspected revisions and retains the full machine-readable report.

The toolkit CI result is **not** a product-compliance result. The fleet workflow
does not use `continue-on-error`; failing or unverified applicable requirements
leave it failed while its report is uploaded. The first package does not alter
consumer workflows, branch protection, device commands or approved interfaces.

## Run locally

Install the repository's existing development dependencies:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python scripts/nikas_repository_contract.py schema \
  --registry deployments/repository-contracts
```

Validate one profile against its matching checkout:

```bash
python scripts/nikas_repository_contract.py validate \
  --profile deployments/repository-contracts/ha-ho-sc-8w.json \
  --root ../ha-ho-sc-8w \
  --json-output /tmp/nikas-one.json \
  --markdown-output /tmp/nikas-one.md
```

For a reproducible fleet inspection, use an empty destination on a clean build
runner. Snapshot acquisition respects the runner's Git configuration; it does
not install or run the fetched projects' dependencies, tests or integrations.

```bash
python scripts/checkout_nikas_contract_snapshots.py \
  --registry deployments/repository-contracts \
  --destination /tmp/nikas-snapshots
python scripts/nikas_repository_contract.py fleet \
  --registry deployments/repository-contracts \
  --repos-root /tmp/nikas-snapshots \
  --json-output /tmp/nikas-fleet.json \
  --markdown-output /tmp/nikas-fleet.md
```

The destination is not overwritten if a checkout already exists. Each profile
uses a full Git commit SHA; `main` is the publication policy, not a floating
inspection revision. Updating to newer consumer commits is a reviewed inventory
change after checking the actual entrypoints and evidence again.

Exit codes:

- `0`: all checks in the requested scope passed or were factually inapplicable;
- `1`: strict inspection found a failure or an unverified applicable requirement;
- `2`: malformed profile/input or setup error.

In particular, exit 0 from `schema` means only that profiles conform to the
profile format. Read the report scope and per-requirement results.

## Evidence discipline

These initial profiles preserve observed standards, including old 1.9/2.1
declarations, and open audit IDs. The required baseline is recorded separately.
A `pending` entry is not an exception or acceptance. Existing test/workflow
paths are inventory only; they do not prove those tests cover the active product.

Literal bindings identify statically observable values. They do not execute
Home Assistant or prove the complete registration control flow. Missing or
unsupported bindings and ambiguous registration remain unverified. Behavioural
and physical acceptance require separate evidence tied to the exact revision
and relevant runtime artifacts.

The retained House files inside `ha-contract-generated-ui` are not active panel
artifacts: its current setup registers the registry service and static assets.
The standalone House repository is the panel owner. The HO profile includes
the newly merged Zone 7 verification revision, UI 0.7.06; its additional syntax
checks do not establish autonomy or complete coverage of its historical imports.

## Subsequent consumer migration

The [first CI migration](NIKAS_CI_GATE.md) establishes one aggregate `validate`
context in the canonical repository, House and StarLine while preserving the
existing checks. It is one adoption step; product compliance remains separate.

1. Review this canonical package and the matching defaults/mirror PR.
2. Use each strict report to choose a focused consumer PR, starting with actual
   delivery/validation mismatch and command/data-quality defects.
3. Add a local factual profile and uniquely named CI check, preserving existing
   mandatory gates. Extend real scenario coverage and close open findings.
4. After applicable gaps are closed, make strict compliance required and verify
   the GitHub setting by readback. A checked-in settings declaration is not proof
   that GitHub enforces it.
5. Record the required browser/HA/iPhone acceptance before declaring the product
   migration complete.

Manual fleet inspection remains an audit tool; it is not a substitute for a
required consumer check. Do not automatically merge old PRs, delete publication
objects or change product capabilities as a side effect of adoption.
