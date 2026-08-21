# Release policy

## Principles

- Releases are created from `main` only after required CI and Home Assistant validation checks pass.
- Every functional release is traceable to its contracts, verified inventory snapshot(s), panel manifest, renderer-engine fingerprint and generated RenderTrace.
- Generated Lovelace output must be reproducible from the tagged source.
- A green syntax/schema/test run is necessary but not sufficient: the semantic release gate must also allow the candidate.
- Semantic changes are documented in `CHANGELOG.md`.
- No release may contain credentials, private Home Assistant storage, tokens or diagnostic payloads with sensitive data.

## Versioning

The project version format will be fixed before the first functional release. Existing Home Assistant NikaS project version history must not be rewritten merely to satisfy a generic versioning convention.

## Semantic release gate

Every production candidate is compared with the currently approved baseline RenderTrace.

```bash
ha-contract-ui diff render release/baseline.meta.json .generated/candidate.meta.json
ha-contract-ui gate render release/baseline.meta.json .generated/candidate.meta.json
```

The gate is fail-closed:

- no semantic changes → allow;
- semantic changes without approval → block;
- invalid or stale approval → block;
- exact `RenderApproval v1` matching the current baseline SHA, candidate SHA and semantic-diff SHA → allow.

The gate also fingerprints the renderer engine. A renderer implementation change is therefore a reviewable release event. A canonical dashboard SHA change that cannot be explained by render-affecting trace semantics is classified as critical `unclassified_render_drift`.

Approvals are not generated or refreshed automatically. A reviewer creates an approval only after inspecting the semantic diff. Any later candidate, source, renderer or semantic-diff change invalidates the approval.

## Release gate

Before a functional release:

1. repository validation and regression tests are green;
2. Home Assistant Hassfest is green;
3. contract, inventory, manifest and snapshot inputs are valid;
4. deterministic candidate Lovelace YAML and RenderTrace are generated;
5. semantic diff against the approved baseline is reviewed;
6. `ha-contract-ui gate render` returns `ALLOW`;
7. generated panels are tested in Home Assistant;
8. the previous approved YAML and RenderTrace remain available for rollback;
9. the candidate YAML, RenderTrace and any exact review approval are retained as release evidence;
10. `CHANGELOG.md` is updated.

## Rollback

Rollback targets the prior approved generated artifact and its RenderTrace, not a manually edited dashboard. A rollback must preserve the same traceability and validation rules as a forward release.
