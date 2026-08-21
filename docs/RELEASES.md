# Release policy

## Principles

- Releases are created from `main` only after required CI checks pass.
- Every functional release must be traceable to its source contracts, inventory assumptions and generator revision.
- Generated Lovelace output must be reproducible from the tagged source.
- Semantic changes are documented in `CHANGELOG.md`.
- No release may contain credentials, private Home Assistant storage, tokens or diagnostic payloads with sensitive data.

## Versioning

The project version format will be fixed before the first functional release. Existing Home Assistant NikaS project version history must not be rewritten merely to satisfy a generic versioning convention.

## Release gate

Before a functional release:

1. repository validation is green;
2. contract/schema validation is green;
3. semantic diff is reviewed;
4. generated panels are tested in Home Assistant;
5. rollback/previous generated artifact remains available;
6. `CHANGELOG.md` is updated.
