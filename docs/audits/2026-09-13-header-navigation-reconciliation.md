# Header navigation production reconciliation

Navigation Contract 1.3 is merged. Main-panel titles return to `/home/overview`; internal pages return to their immediate parent. Ambient query/storage/referrer/history cannot select that parent.

| Repository | Merged PR | Production revision | UI |
|---|---|---|---|
| ha-contract-generated-ui | [#171](https://github.com/NikaSir/ha-contract-generated-ui/pull/171) | `3a503d86d4d317bf15a6d0bc22fdad13c1800f7b` | contract 1.3 |
| ha-nikas-climate | [#20](https://github.com/NikaSir/ha-nikas-climate/pull/20) | `824b95fd129a953c6d6de8f7a12efd83911c2961` | 1.4.28 |
| ha-nikas-rooms | [#8](https://github.com/NikaSir/ha-nikas-rooms/pull/8) | `aa0d5e211bb38cd95b52263e8391e55f99327090` | 11.0.16 |
| ha-nikas-house | [#12](https://github.com/NikaSir/ha-nikas-house/pull/12) | `97f7d137f54c891a6acea69d84aa2da9de2ae453` | 1.0.3 |
| ha-vless-gateway | [#24](https://github.com/NikaSir/ha-vless-gateway/pull/24) | `5aa7c3b1090cf322c3321ee7446388a25915b229` | 0.1.2 |
| ha-starline-telemetry | [#60](https://github.com/NikaSir/ha-starline-telemetry/pull/60) | `1b7e819833d210f95b5f1bb40f29c3d20693344f` | 0.6.10 |
| ha-zont | [#34](https://github.com/NikaSir/ha-zont/pull/34) | `508f4f3db76bc60be42fb644eba23b5737cfd62d` | 0.9.7 |
| ha-water-accounting | [#7](https://github.com/NikaSir/ha-water-accounting/pull/7) | `bece25db3f73f2a4b2b9a116c69a20baf9f20b05` | 0.1.6 |
| ha-stark-solarpower | [#77](https://github.com/NikaSir/ha-stark-solarpower/pull/77) | `92ad94231556862e0f491ab6a880c9a1c8765d7e` | 0.9.7 |
| ha-nikas-dyson | [#3](https://github.com/NikaSir/ha-nikas-dyson/pull/3) | `6585c81f230ec471219e65c57394fb7b683b8504` | 1.0.3 |
| ha-nikas-access | [#14](https://github.com/NikaSir/ha-nikas-access/pull/14) | `a3406417212e3f4de90d68d577174d53f81c9f8e` | 0.1.10 |
| ha-lider-voltage-control | [#46](https://github.com/NikaSir/ha-lider-voltage-control/pull/46) | `1d5bb0dbe233f3d62b0049236768609850c923f6` | 0.8.8 |
| ha-s8-omni | [#134](https://github.com/NikaSir/ha-s8-omni/pull/134) | `53b609d23183b86f5d016da80fcbdf6beb4c396b` | 1.0.8 |
| ha-ho-sc-8w | [#182](https://github.com/NikaSir/ha-ho-sc-8w/pull/182) | `8e4e1bf755105a3bef88ca6bfa04175bc5c5d4c6` | 1.1.1 |
| ha-keenetic-hero-4g | [#96](https://github.com/NikaSir/ha-keenetic-hero-4g/pull/96) | `a7549e4dc1429a84849defbdf69d936cc8dc5195` | 1.0.10 |

Keenetic includes concurrent overview/plaque changes (#97/#98), S8 includes docked-station command guards (#135), and HO includes automatic HA theme support (#183). Those changes were preserved; navigation versions advanced to 1.0.10, 1.0.8 and 1.1.1 respectively.

Reconciliation RED: the dependency-free profile regression failed for all 14 product profiles against central main `3a503d86d4d317bf15a6d0bc22fdad13c1800f7b`. GREEN: exact production revisions and all artifact bindings match. Stark version matching now uses the navigation patch adjacent to `SAFE_RETURN_ROUTE`, because the old `SOURCE_ROUTE_KEY` marker was removed.

Every product records NAV-1 as `fixed_pending_verification`. Existing findings are retained. All acceptance evidence stays pending and device evidence paths stay empty. GitHub CI and local browser fixtures do not certify the running Home Assistant, iPhone or device behavior. No live installation was performed.

The central self-profile pins the merged authority revision above; it does not attempt to self-pin this reconciliation commit.
