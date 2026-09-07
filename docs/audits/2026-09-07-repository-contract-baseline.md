# Repository contract baseline — 2026-09-07

This is the **pre-adoption baseline** for Repository Contract v1.0, captured
before consumer migration. It describes 17 pinned NikaS repositories, excluding
the `zigbee2mqtt.io` fork. The aggregate strict result is **`fail`**: 14 repositories
are `fail`, 3 are `not_verified`, and none has complete compliance evidence.

`fail` means a detected contract mismatch or a recorded open finding blocks
compliance; it does not mean the product is wholly unusable. `not_verified`
means sufficient evidence is missing; it is not, by itself, a confirmed defect.
Open findings were carried into the profiles from the repository audit. The
inspector does not reproduce their device behavior or certify their repair.
A row without a finding ID can still have unverified requirements. Individual
PASS results below establish only the stated static observations.

## Scope and observed results

- All **17** pinned revisions and Git origin identities matched their checkouts;
  no tracked worktree modifications were reported in those inspected snapshots.
  Manifest identity checks passed for all **15** Home Assistant integrations.
- **15** frontend artifacts were inventoried in **13** repositories. House has
  three independently registered modules: its panel, navigation helper and hero.
  CGUI is a registry/shared-asset service; its retained House frontend is not
  declared active. The inspector conservatively leaves empty-inventory capability
  verification open for CGUI, Hikvision, `.github` and the gateway scaffold.
- **43 static literal bindings passed** against the recorded paths and values.
  All **15 artifact integrity** checks passed. These results do not prove the
  complete Home Assistant registration control flow, effective displayed version,
  cache freshness, syntax validity or deterministic rebuilding.
- Recognized import traversal covered **119 files** and **104 edges** across the
  15 artifact graphs. HO accounts for **76 files / 75 edges**, Climate for
  **26 / 25**, and S8 for **5 / 4**; the other 12 graphs contain one file each.
  No missing targets or unresolved expressions were reported by the recognized
  traversal. The three import-bearing artifacts fail the single-output target;
  the remaining 12 retain `not_verified` autonomy because absence of recognized
  imports does not prove complete runtime autonomy.
- The required standards remain **UI 2.2 / navigation 1.2**. Eight repositories
  passed all four static declaration/document comparisons: CGUI, `.github`,
  Keenetic, LIDER, S8, StarLine, HA VLESS and ZONT. Five still declare UI **1.9**
  (HO, House, Rooms, Stark, Water); Access declares **2.1**. Climate declares
  **2.2**, but its navigation declaration and document paths are incomplete.
  Matching documents do not establish UI behavior compliance.
- Duplicate CI job contexts were detected in CGUI, House and StarLine. The HO
  release workflow conflicts with the required publication policy. Its current
  CI does include v0706 syntax/parity checks, while the main bundle/autonomy
  checks still target the older `irrigation-panel.js`.

The inspection reads source, workflow and profile data. It does not execute
consumer application code, build systems, tests or commands, and it does not
verify live GitHub protection, the user's running Home Assistant, iPhone or
physical devices. Registration reachability, build/syntax coverage, effective
required CI and behavioral/device acceptance remain open in this baseline.

## Pinned repository results

Repository links open the factual profiles. IDs identify recorded open findings;
auto-detected mismatches without an ID remain present in the detailed report.

| Repository / profile | Exact source revision | Strict status | Open finding IDs |
|---|---|---|---|
| [NikaSir/.github](../../deployments/repository-contracts/nikasir-github.json) | `e0b171fea239ca4c4f1b3b9427f84c34784f3a61` | `not_verified` | — |
| [NikaSir/ha-contract-generated-ui](../../deployments/repository-contracts/ha-contract-generated-ui.json) | `956123093a488deda1ea65746f06f03929c61d45` | `fail` | A21 |
| [NikaSir/ha-hikvision-next](../../deployments/repository-contracts/ha-hikvision-next.json) | `12abd40a3b5ad226198eb9cb0dcc5f0bb103a997` | `fail` | A02, A13, A14 |
| [NikaSir/ha-ho-sc-8w](../../deployments/repository-contracts/ha-ho-sc-8w.json) | `9b8cac6dc3a9bf88535dddff2c5de46a10c7c5a4` | `fail` | A01, A06, A07, A22, A19 |
| [NikaSir/ha-keenetic-hero-4g](../../deployments/repository-contracts/ha-keenetic-hero-4g.json) | `d2a35c9aba36a1021834ecb481ecb71e76d23879` | `fail` | A15 |
| [NikaSir/ha-lider-voltage-control](../../deployments/repository-contracts/ha-lider-voltage-control.json) | `504829eff79c2bf83308faaab96ae44247d13b3d` | `fail` | A03 |
| [NikaSir/ha-nikas-access](../../deployments/repository-contracts/ha-nikas-access.json) | `90ae7549af3010487676a03c86f579fcd938bb89` | `fail` | A08, A19 |
| [NikaSir/ha-nikas-climate](../../deployments/repository-contracts/ha-nikas-climate.json) | `1c556be8ba908834a108e20f685222e88118600b` | `fail` | A07, A11, A12, A20-CI |
| [NikaSir/ha-nikas-house](../../deployments/repository-contracts/ha-nikas-house.json) | `65b12f10b61498cecb1b60645e5de17c50557898` | `fail` | A19 |
| [NikaSir/ha-nikas-rooms](../../deployments/repository-contracts/ha-nikas-rooms.json) | `0d5366bf1dbc34e0b449b79c7f06f7d8b520b4d3` | `fail` | A08, A09, A10, A19 |
| [NikaSir/ha-s8-omni](../../deployments/repository-contracts/ha-s8-omni.json) | `eff686b373e92e77f9efa11735143029891ad4fd` | `fail` | A05, REG-S8-IMPORTS |
| [NikaSir/ha-stark-solarpower](../../deployments/repository-contracts/ha-stark-solarpower.json) | `d379323a7092d07f6af1ab0680542609f9a7a69f` | `fail` | A17, A19 |
| [NikaSir/ha-starline-telemetry](../../deployments/repository-contracts/ha-starline-telemetry.json) | `94b36c32e145c7357582bada413c632f46af180e` | `fail` | A04 |
| [NikaSir/ha-vless-gateway](../../deployments/repository-contracts/ha-vless-gateway.json) | `7a96036ddf02a7ca95086785d3dfa504f01ef366` | `not_verified` | — |
| [NikaSir/ha-water-accounting](../../deployments/repository-contracts/ha-water-accounting.json) | `8f73632eedc1eb2bb103fdc1cc22ae9ca39dc208` | `fail` | A18, A19 |
| [NikaSir/ha-zont](../../deployments/repository-contracts/ha-zont.json) | `e8f64b86e35c0f95c19c3bf8d14f4ae8b4fee426` | `fail` | A16 |
| [NikaSir/vless-gateway](../../deployments/repository-contracts/vless-gateway.json) | `75f0e8d55f0b9d2388555adb18f1e663bc241620` | `not_verified` | — |

## Provenance

| Field | Recorded value |
|---|---|
| Checked at (UTC) | `2026-09-07T12:04:50.749644+00:00` |
| Inspector version | `1.0.0` |
| Inspector SHA-256 | `c99a1eb087dffa01a2a9d20f1b6a57681e9217238b25f647b4eb9ac4df6ca37d` |
| Profile schema SHA-256 | `434e700728b62a9bcc8751fe9052d96350955c86a5568c50fbfabb6f0e467691` |
| Source JSON report SHA-256 | `a4981a28785efaad45f55825a7e1a9af916692e25e3983c284c7d2b7ee0f7461` |
| Required UI document SHA-256 | `3b6cc750b08aa0d2a375d1430ea04ac68c90525a527d197b014abd96728d23d1` |
| Required navigation document SHA-256 | `d495eca80345b96976c168029a96146803f3d8195b6f6fc723827b601ffb578e` |

The [full JSON report](2026-09-07-repository-contract-baseline.json) is the final
`baseline.json` generated at the time above. The SHA identifies those exact
report bytes; a rerun has a different timestamp and therefore a different
report hash. Use the recorded inspector, schema and profile revisions to compare
substantive results. The inspector belongs to the adoption package; the CGUI
source SHA in the table is the inspected pre-adoption product snapshot.

## Reproduction

From this canonical repository checkout, use the
[inspector](../../scripts/nikas_repository_contract.py),
[schema](../../schemas/nikas_repository_contract.schema.json) and linked profiles
whose versions/hashes match this baseline. Install the existing development
dependencies, then acquire fresh snapshots in an unused temporary directory:

```bash
python -m pip install -e '.[test]'
python scripts/nikas_repository_contract.py schema \
  --registry deployments/repository-contracts
python scripts/checkout_nikas_contract_snapshots.py \
  --registry deployments/repository-contracts \
  --destination /tmp/nikas-baseline-2026-09-07-snapshots
python scripts/nikas_repository_contract.py fleet \
  --registry deployments/repository-contracts \
  --repos-root /tmp/nikas-baseline-2026-09-07-snapshots \
  --json-output /tmp/nikas-baseline-2026-09-07.json \
  --markdown-output /tmp/nikas-baseline-2026-09-07.md
```

Snapshot acquisition needs Git access to the listed public repositories and
never overwrites an existing checkout. The strict fleet command is expected to
exit **1** for this baseline while writing its reports. Do not turn that exit
into a compliance PASS. Successful schema validation means only that the profile
format is valid. See the [adoption procedure](../NIKAS_REPOSITORY_CONTRACT_ADOPTION.md)
for consumer migration and evidence requirements.
