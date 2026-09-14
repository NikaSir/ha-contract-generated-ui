# Hikvision sensor entity IDs — 2026-09-14

The [dependency audit](2026-09-14-dependabot-maintenance.md) identified a remaining Home Assistant 2027.2 compatibility warning. This follow-up resolves the source-code cause in [Hikvision PR #11](https://github.com/NikaSir/ha-hikvision-next/pull/11), accepted as [`8fc9b51d360c16112350fc12e4195d7ef2bf29df`](https://github.com/NikaSir/ha-hikvision-next/commit/8fc9b51d360c16112350fc12e4195d7ef2bf29df), integration version 1.1.9.

## Cause and correction

AlarmServerSensor and StorageSensor used a raw, case-sensitive device serial number (including slash characters) in their suggested entity IDs. Home Assistant currently repairs these IDs but [reports that support ends in 2027.2](https://github.com/home-assistant/core/blob/2026.9.2/homeassistant/helpers/entity_platform.py).

Both classes now apply Home Assistant's `slugify` to the suggested entity ID before registration. Their `unique_id` strings are unchanged. Existing registry identity, user names and user-disabled state are retained. Other platforms were inspected: their suggested IDs already use normalized serial/event identities.

## Validation

[PR CI 1](https://github.com/NikaSir/ha-hikvision-next/actions/runs/34852770169), [PR CI 2](https://github.com/NikaSir/ha-hikvision-next/actions/runs/34852770260): all required checks succeeded on reviewed head `45d73dcb871434aaee3844db24765b0bb8af75fe` before protected squash merge. Both Python 3.12 and 3.14 matrix legs, Hassfest, HACS and the fail-closed validate gate passed.

The new regression file checks sensor IDs before the platform can normalize them, using both NVR and slash-containing camera serials. It also pre-seeds legacy registry entries before integration setup, then verifies the registry entry IDs, original unique IDs, custom entity IDs, user names and USER-disabled storage state through two setup/unload cycles. Existing sensor-value tests continue to assert the default entity IDs. No test expectation was weakened to accept invalid IDs.

The canonical profile is advanced to the accepted Hikvision revision, adds the regression evidence, and keeps all runtime/device acceptance statuses pending. The canonical self-profile points to its accepted parent, `92a38ee1cda61de0d0dc3564d5d6b2fbe0a333d0`, rather than attempting a circular self-reference.

## Acceptance boundary

No tag or GitHub Release was created. HACS installation and acceptance on the owner's camera/NVR remain pending. Tests ran in hosted GitHub Actions because local workspace execution was unavailable.

General settings in 17 repositories remain the separate Administration-access task recorded in the preceding audit. Research drafts S8 #102 and HO-SC-8W #22 are unchanged.
