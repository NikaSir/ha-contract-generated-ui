# Beta release adoption

## Approved decision — 2026-09-14

The owner approved the following delivery sequence for five integrations:

1. Publish a candidate version with a `-beta.N` suffix for user testing.
2. Let the user install the beta through HACS with beta versions enabled.
3. Publish the corresponding stable version only after the user's acceptance.
4. Keep the previous stable Release available for rollback.

The scope is `ha-ho-sc-8w`, `ha-s8-omni`, `ha-nikas-climate`,
`ha-lider-voltage-control` and `ha-keenetic-hero-4g`.
This decision does not switch other integrations to a release-driven channel.

## Implementation and evidence

This record preserves the approved direction; it does not claim that the five
publication pipelines have already been migrated. Repository maintenance,
successful CI or a merge to `main` is not user acceptance of a beta candidate.

At the audit snapshot on 2026-09-14:

| Repository | Observed channel | Remaining transition work |
|---|---|---|
| `ha-ho-sc-8w` | Stable `1.1.1`; automation publishes stable versions and skips prereleases | Enable beta publication and verify HACS delivery while preserving the previous stable |
| `ha-s8-omni` | Stable `v1.0.8`; no release workflow | Implement the beta/stable publication process and verify HACS delivery |
| `ha-nikas-climate` | Documented `main` channel; no GitHub Releases | Implement and verify the release-driven beta/stable channel |
| `ha-lider-voltage-control` | Documented `main` channel; no GitHub Releases | Implement and verify the release-driven beta/stable channel |
| `ha-keenetic-hero-4g` | Documented `main` channel; release-tag workflow explicitly disabled | Replace the old main-only policy when the approved channel is implemented and verified |

Each implementation must preserve existing integration/UI version lineage and
the project's tag-prefix convention, use a reviewed source commit, distinguish
GitHub prereleases from stable Releases, and keep stable promotion subject to
user acceptance. No existing Release or tag is deleted or repointed as part of
this transition.

Factual repository profiles continue to describe implemented behavior at their
pinned revisions. They must not be changed to claim working beta automation
merely because this decision has been approved. Acceptance remains subject to
the [HACS Publication Contract](NIKAS_HACS_PUBLICATION_CONTRACT.md).
