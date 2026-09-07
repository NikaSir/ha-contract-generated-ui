# NikaS Refresh Action Contract v1.0

**Status:** REQUIRED companion to NikaS Specialized Panel UI Standard v2.2  
**Canonical source:** `NikaSir/ha-contract-generated-ui`  
**Applies to:** every NikaS specialized panel that exposes a refresh action  
**Approved:** 2026-09-07  
**Machine contract:** `.nikas-ui-standard.json` → `refresh_action_feedback`

This companion extends the Header, stable-rendering, data-truth and acceptance rules of [NikaS UI Standard v2.2](NIKAS_SPECIALIZED_PANEL_UI_STANDARD.md). It does not change shell geometry, require a refresh button where none was approved, or certify unchanged panels as compliant.

## Why this rule exists

In HO-SC-8W UI 0.7.08, the upper-right refresh button gave no visible progress feedback. A request could be sent while the user could not distinguish execution, inactivity or failure. The fix is tracked in [HO-SC-8W PR #170](https://github.com/NikaSir/ha-ho-sc-8w/pull/170), UI 0.7.10 / integration 1.0.0-b006.31.

A working service call without observable feedback is a UI defect. An animation without a real refresh request is also a defect.

## Mandatory behavior

### REFRESH-01 — Immediate, truthful feedback

On accepted activation, mark the existing button busy before awaiting asynchronous work. Start the real read-only telemetry refresh through the panel's declared Home Assistant/integration API. The button does not reload Home Assistant, restart an integration, change device settings or invoke unrelated commands.

### REFRESH-02 — Visible duration follows the request

With ordinary motion settings, rotate the refresh glyph continuously at one full turn per 900 ms. Keep the busy presentation for at least 900 ms and until the actual awaited request settles, whichever takes longer. Start the request immediately; the minimum duration delays only removal of feedback. A timer must not re-enable the button while its request is still pending.

### REFRESH-03 — No duplicate requests

Disable repeat activation for the complete busy interval. A handler-level single-flight guard is mandatory in addition to the button's disabled state. Rapid taps, keyboard activation and repeated handler calls must not dispatch a second request or queue a delayed duplicate.

### REFRESH-04 — Completion and failure are observable

On settled success or failure, clear busy/disabled state on every exit path, including exceptions, after the minimum visible interval. Restore the same button so the user can deliberately retry. A rejected request, missing update service or absence of refreshable entities must produce a visible message such as `Не удалось обновить данные`, not silent success. Technical details must not disclose credentials or tokens.

Successful completion of the request does not by itself prove that every device supplied a new sample. Never mark preserved telemetry current, change its timestamp, or turn a status healthy merely because the animation ended. Freshness changes only when factual new data is accepted.

### REFRESH-05 — Preserve the user's context

Patch the mounted UI; do not rebuild the panel or call `location.reload()`. Keep Header, selected tab/peer, work viewport, scroll, zoom and unsubmitted editor draft. New telemetry may update untouched fields according to the product's existing editor contract, but refresh must not submit or silently discard user edits. The button keeps its size and rail so the title does not move.

### REFRESH-06 — Stable busy state during rendering

Ordinary Home Assistant updates and tab changes must not replace the Header button, lose its busy state, restart its animation or re-enable it early. Reconciliation restores the current busy attributes on the mounted control. Unchanged state must not cause unnecessary DOM writes.

### REFRESH-07 — Accessibility and reduced motion

Use a semantic button with an accessible name. While busy expose `aria-busy="true"`, disabled semantics and a name such as `Обновление данных`; restore the idle name on completion. With `prefers-reduced-motion: reduce`, suppress rotation but retain a visibly distinct static busy surface and accessible status. Busy must not be signalled by color alone or by an invisible screen-reader attribute alone.

## Required production regression cases

The owning panel's CI must execute its registered production entrypoint and assert behavior, not only search source text for `busy`, CSS animation or a function name. Test the actual button-to-handler wiring and exact allowed service/API call. The following case identifiers are part of the machine contract:

| Case | Required assertion |
|---|---|
| `activation` | Pointer and keyboard activation start the real permitted request and immediately expose busy state. |
| `fast_success` | A request settling immediately still shows busy for at least 900 ms, then restores idle state. |
| `slow_success` | A request exceeding 900 ms remains busy/disabled until it settles; no timer produces false completion. |
| `duplicate_activation` | Repeat taps, keyboard events and handler calls during busy produce only one request. |
| `failure_cleanup` | Rejection shows an error and restores idle state; a later deliberate retry is possible. |
| `unavailable_targets` | Missing service or no refreshable entities produce visible failure and no false success. |
| `render_stability` | State updates and tab changes preserve the Header control, busy state and active request. |
| `context_preservation` | Refresh preserves tab/peer, scroll, zoom and unsubmitted editor changes, without page reload. |
| `reduced_motion` | Browser-computed reduced-motion styling stops rotation but keeps visible busy feedback and ARIA. |
| `truthful_freshness` | Completion without a new accepted sample does not invent a fresh timestamp or healthy state. |

A static contract check is additional protection, not a substitute for these behavioral tests. Browser checks are required for actual animation, reduced-motion styling and visual geometry; a fake DOM or screenshot alone does not prove them.

## Acceptance and adoption

Include the refresh action in the v2.2 mandatory viewport matrix. Check rapid repeat activation, a slow response and a rejected response on the phone; ensure there is no title shift, viewport reset or lost draft. A still screenshot cannot establish that an icon rotates.

This registry stores the rule, its digest and its regression-case list. Registry CI protects that agreement from deletion or silent weakening; it does not execute every panel's runtime. Each owning repository records implementation, production-test evidence and phone/browser acceptance separately. Missing evidence is `GAP`, not an assumed pass. HO-SC-8W PR #170 is the initial fix, not certification of every case above or of other NikaS panels.
