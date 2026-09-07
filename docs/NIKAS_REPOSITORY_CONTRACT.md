# NikaS Repository Contract v1.0

Status: normative engineering contract for adoption through reviewed pull requests.
Authority: `NikaSir/ha-contract-generated-ui`.
Companion standards: NikaS Specialized Panel UI Standard v2.2, Navigation
Contract v1.2, and Shell v2.1. This document does not replace their requirements
or declare existing implementations compliant.

## 1. Purpose and scope

Every maintained NikaS repository must describe what it actually supplies,
which requirements apply, what has been verified, and how the verified change
reaches Home Assistant. The description and its evidence are versioned with the
source they describe.

A repository may have several roles: standards authority, integration,
panel, service, or explicitly unfinished scaffold. Applicability follows its
active components and capabilities, not its name or a convenient repository
label. Retained historical files are not runtime artifacts unless the active
setup or load graph actually reaches them.

Each integration remains autonomous at runtime. Shared validators, schemas and
build-time source may be reused during development or CI. A running panel must
not depend on another NikaS repository, an older panel installation, or a remote
script to supply its shell, navigation or domain logic.

## 2. One factual description of delivery

The machine-readable profile records:

- repository identity and the exact source revision inspected;
- active integration domains and manifests;
- each actually registered production entrypoint and its registration evidence;
- related integration, UI and cache versions with their separate bindings;
- applicable normative documents and the observed versions/hashes;
- publication channel and real CI workflows/checks;
- behavioural, browser and device acceptance evidence, or its absence.

During this first adoption stage, profiles are maintained centrally under
`deployments/repository-contracts/`. A profile is an inventory of a particular
source revision; it does not overwrite the consumer's existing contract or
silently upgrade its standard version. Consumer-local profiles and required
gates are introduced through subsequent focused migration PRs.

Profile paths must remain inside the inspected repository. A profile must not
execute arbitrary shell commands or load device/integration code to obtain
facts. Unsupported static expressions produce an explicitly unverified result.
Do not guess the target from an old filename, comments, or a declaration that
is not connected to the active registration.

The validator itself has a versioned source and schema. Updating the tool or
normative baseline is a reviewed change; no floating external implementation
may silently change an existing CI requirement.

## 3. Production and versions

Registration, static URL mapping, shipped file and validation target must agree.
CI validates the code Home Assistant actually loads, including reachable local
dependencies. A syntax check of a historical base file is insufficient.

Integration and UI versions are independent. Each must agree with its own
manifest, runtime exposure, registration and cache bindings. A behaviour change
requires the appropriate version/cache update under the existing product policy.
Do not renumber integrations merely to introduce repository tooling.

Specialized production panels retain the existing requirement for one autonomous
bundle. Reachable historical imports are a compliance failure even when a factual
profile accurately records them. Refactoring a chain must preserve approved
behaviour and layout; deleting still-imported files is not a migration.

Builds must be reproducible. CI rebuilds and checks for a diff or uses an
equivalent deterministic check. Static validation of registration is separate
from proof that the browser loads and operates the panel.

## 4. Data quality

Every operational value has a source, value, accepted-sample time and quality.
Implementations must distinguish valid zero/false from missing, unknown,
unavailable, malformed, and preserved stale values.

- Transport, freshness and completeness are independent facts.
- Old cache may be shown with its age/quality; it must not become a fresh green
  reading because another measurement updated.
- A partial aggregate is unknown or explicitly partial, never a complete total
  obtained by replacing missing contributions with zero.
- Bootstrap data cannot indefinitely override newer authoritative state.
- An unchanged HA state may still have fresh telemetry. `last_updated` alone
  does not establish the age of the last accepted device exchange.
- A selected operating mode does not establish physical execution, such as
  compressor operation or active heating.

The two-level connection plaque is used only where requested. This contract
does not add it to StarLine or Home now, invent device selectors for a single
system, or change approved product terminology.

## 5. Commands and confirmation

The backend validates capability, target, current mode and session before a
write. The frontend reflects the same capability and busy state. Product-specific
requirements for explicit Apply and confirmation remain in force.

Missing information cannot authorize a command. Stale queued intentions must
not be reused after the operation/session that created them has ended. Duplicate
submissions are prevented without leaving controls permanently locked.

Successful service dispatch is not proof of physical execution. An unknown or
unavailable readback cannot confirm a requested zero/off state. Timeout and
failure remain observable; the UI must not invent success or automatically retry
a consequential write unless the product contract explicitly provides for it.

Read-only integrations and scaffolds remain read-only. Telemetry refresh is not
a hidden equipment command. Event inputs that can change state require a
documented, enforced source-trust model.

## 6. Lifecycle and stable interface

Each request, timer, animation frame, subscription and lock has a defined owner,
cancellation rule and reconnect path. Detach/attach of the same component must
restore operation. Cancelled work cannot leave a permanent loading flag, frame
identifier or command lock. Late responses cannot replace newer accepted state.

Mount the application shell and stable device controls once. Telemetry changes
patch their content and attributes; they do not recreate the shell, images or
controls. Preserve focus, scroll, selection and valid zoom bounds. Existing
phone/tablet/desktop acceptance requirements remain applicable.

## 7. Evidence and result semantics

Profile/schema validity and product compliance are separate results. A valid
inventory with known defects is not a compliant implementation.

| Result | Meaning |
|---|---|
| `pass` | This specific check has sufficient matching evidence and passed. |
| `fail` | A concrete requirement is contradicted by inspected source or evidence. |
| `not_verified` | Applicable, but evidence is absent, stale, ambiguous or unsupported. |
| `not_applicable` | Excluded by the component's actual capability and a recorded reason. |

Strict compliance fails if any applicable requirement is `fail` or
`not_verified`. A malformed profile is an input error. The checker produces its
report before returning a nonzero status, so failures remain reviewable.

No automatic waivers, expected-failure-to-success conversion, or previous-gap
baseline can turn a missing requirement into `pass`. Open audit findings remain
open until closure evidence is recorded. Merely listing a test or finding a
keyword in source is not behavioural evidence.

Evidence identifies the checked revision, relevant artifact hashes, scenario,
runner/environment and result. Evidence from an older revision cannot silently
certify the current production. Automated source checks, behavioural tests,
browser checks, and acceptance on HA/iPhone are distinct claims.

## 8. Required scenario families

Use small behavioural tests that reproduce a failure or protect a public
contract. Required families depend on the component:

1. Data: missing/null/unknown/unavailable, real zero/off, stale cache, partial
   responses and conflict between an old bootstrap and newer state.
2. Commands: wrong mode/session/capability produces zero writes; duplicate
   submission; unconfirmed readback; successful verified execution.
3. Lifecycle: detach/attach during a request, cooldown and animation frame;
   late response; disconnect and recovery.
4. UI: stable node identity/focus/scroll during telemetry, correct return route,
   cold load and applicable viewport acceptance.
5. Publication: registered artifact equals validated artifact; version/cache
   coherence; reproducible build; required checks really execute.

Protocol and hardware scenarios use verified device-specific mappings. A similar
device profile is not evidence of compatible commands. Synthetic tests must not
dispatch commands to live equipment.

## 9. CI and publication

Preserve existing mandatory checks when adding the contract. Give jobs unique
names across workflows. Do not use a single ambiguous `validate` context for
several independent checks.

An aggregate gate must run even after dependency failure and explicitly require
all mandatory dependencies to have succeeded. Skipped, cancelled and missing
results are not success. `needs` connects jobs within a workflow; cross-workflow
checks require separate required contexts or another verified aggregation.

The common GitHub baseline is a PR to `main`, required applicable checks,
conversation resolution, and protection from force push and deletion. Installing
a document or CI file does not itself configure GitHub branch protection;
settings need separate readback verification. Do not remove an existing required
check to make a migration mergeable.

NikaS publication remains reviewed commits/PRs and `main` through HACS where
applicable. GitHub Releases and automatic release tags are not created. Existing
historical publication objects are not deleted as part of tooling adoption.

## 10. Adoption sequence and completion

1. Review the canonical contract, schema, validator and central profiles.
2. Run strict inspection against exact source revisions. Keep every failure and
   unverified requirement visible; a tooling test pass is not fleet readiness.
3. Introduce consumer-local profiles and CI in focused PRs; preserve earlier
   checks. Close product gaps with their own small tested changes.
4. Promote strict compliance to a required check for each repository once its
   applicable gaps are closed and its job name/trigger has been verified.
5. Complete the applicable HA/iPhone acceptance and record the accepted revision.

This first package implements the common contract and inspection mechanism. It
does not assert that all 17 consumers have migrated, change their equipment
commands or approved layouts, or change their GitHub settings automatically.
Completion is measured separately for tooling, consumer adoption, product
compliance and device acceptance.
