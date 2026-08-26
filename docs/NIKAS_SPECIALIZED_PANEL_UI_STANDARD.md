# NikaS Specialized Panel UI Standard v1.5

**Status:** REQUIRED  
**Canonical source:** `NikaSir/ha-contract-generated-ui`  
**Applies to:** every integration-owned specialized Home Assistant panel  
**Primary acceptance viewport:** iPhone Pro Max, portrait  
**Reference visual implementation:** Stark SolarPower / UPS  

This document supersedes every earlier shell, Header, zoom, scrolling and Bottom Tab Bar rule. Historical documents remain useful only where they do not conflict with this standard.

## 1. Ownership and topology

```text
HEADER                                      native scale
DEVICE SELECTOR (peer devices only)         native scale
ONE WORK VIEWPORT                           scroll/zoom owner
BOTTOM TAB BAR                              native scale
```

- Only the work area scales.
- Header, peer selector and Bottom Tab Bar never scale or move with content.
- Exactly one zoom viewport may exist per panel instance; nested wrappers are prohibited.
- Shell reconciliation is idempotent across redraws and Home Assistant state updates.
- The effective iOS safe area is consumed exactly once.

## 2. Header — UPS reference geometry

- Grid: `52px minmax(0,1fr) 52px`; on very narrow screens: `48px minmax(0,1fr) 48px`.
- Minimum height: `62px`; phone target: `60px`, plus the effective top safe area.
- Title remains geometrically centered regardless of side actions.
- Primary title: `21px`, weight `800`, one line.
- Secondary/version line: `12px`, weight approximately `560`, `var(--secondary-text-color)`.
- The permanent left action is only Home Assistant system menu `mdi:menu`; it dispatches bubbling/composed `hass-toggle-menu`.
- At most one panel-global action occupies the right rail. Refresh uses `mdi:refresh`.
- Menu and refresh are visually identical plaques: `44px × 44px`, `16px` radius, `1px` divider border, `var(--card-background-color)` background, subtle `0 7px 20px rgba(23,45,76,.08)` shadow and a `25px` `ha-icon` glyph.
- Menu glyph uses `var(--primary-text-color)`; refresh uses `var(--primary-color)`.
- A transparent refresh rail is non-conforming.
- Back, an integration drawer, a device command or a decorative brand icon is prohibited in the permanent left rail. Parent navigation belongs inside the work area.

## 3. Work viewport at 100%

At exactly `scale = 1`:

- `x = 0` and `y = 0` are invariant;
- one-finger transform panning is disabled;
- normal native vertical scrolling is enabled;
- horizontal scrolling is disabled;
- the top cannot be pulled below origin or translated above its real content boundary;
- clicks, hold-to-more-info and vertical scrolling start without a gesture delay;
- stored transforms are normalized to `{scale:1,x:0,y:0}` before display.

The former rule that one-finger transform panning also provides vertical movement at 100% is retired.

## 4. Zoom and enlarged pan

- Pinch uses two fingers and preserves the focal midpoint.
- Range is `75–200%`.
- Permanent zoom buttons are prohibited.
- Pinch ending within `97–103%` snaps to exactly 100% and origin.
- Two-finger double tap resets to 100%/origin and briefly shows `Масштаб 100%`.
- Scale persists locally per panel/client and per selected peer device where applicable.
- One-finger transform panning is enabled only when `scale > 1`.
- Each axis is enabled only when scaled content exceeds the viewport on that axis.
- Translation is clamped to factual content edges; exposing empty canvas is prohibited.
- Resize, orientation change, content reflow, peer switch and tab change re-run bounds clamping.
- A tab change returns native scroll to the top and removes invalid translation; stored scale may remain.
- A second finger cancels pending more-info; post-gesture synthetic clicks are briefly suppressed, while intentional stationary hold still opens native more-info.

## 5. Bottom Tab Bar — UPS reference geometry

- One fixed, edge-attached, full-width bar; never a floating card or pill.
- It remains outside the work viewport and above the Home Indicator.
- Background: `var(--card-background-color)`; top divider and a subtle upward shadow.
- Insets: approximately `4px` top and `calc(4px + env(safe-area-inset-bottom))` bottom, with safe left/right padding.
- All destinations have equal-width columns; 3–5 primary tabs are supported.
- Tab touch target minimum height: `52px`.
- Tab radius: `13–14px`; compact internal padding and approximately `2px` icon/label gap.
- Icons are MDI through `ha-icon`, never text characters; canonical glyph size is `28px`.
- Labels are one line, approximately `12px`, weight `700`, readable and ellipsized only when necessary.
- Inactive content uses `var(--secondary-text-color)`.
- Active icon/label use `var(--primary-color)` and an approximately 11% primary-color background, without a second shadow.
- Navigating between tabs restores the work area to the page start before interaction resumes.

## 6. Brand and repository identity

- Every integration repository ships a recognizable integration brand asset.
- A packaged `brand/icon.png` is mandatory; it is the minimum HACS brand asset and must not be an empty placeholder.
- `brand/logo.png`, `brand/dark_icon.png` and `brand/dark_logo.png` are required when the mark or wordmark is not legible in both themes.
- Brand files use the integration package layout expected by Home Assistant/HACS and are included in distribution checks.
- README starts with the same recognizable project/integration identity; repository and installed integration must not present unrelated marks.
- Header does not display the brand icon; it is for repository/HACS/HA identity, sidebar/launcher and suitable domain cards.
- Changed raster assets use deterministic cache/version handling where served by the panel.

## 7. Required automated guards

Repository tests or static checks must verify:

1. exactly one work/zoom viewport;
2. no permanent scale controls;
3. `hass-toggle-menu` and `mdi:menu` in the left rail;
4. both Header actions use the standard plaque geometry;
5. Bottom Tab icons use `ha-icon` and canonical size;
6. no horizontal movement and no transform pan at 100%;
7. axis-aware overflow bounds above 100%;
8. clamp after resize/tab/peer changes;
9. brand `icon.png` exists in the shipped integration package;
10. JavaScript syntax, package validation, HACS and Hassfest pass.

## 8. Mandatory phone acceptance

- long diagnostics pages scroll vertically at 100%;
- 100% cannot move horizontally or be pulled away from the top origin;
- enlarged content pans only on necessary axes and never exposes empty field;
- release preserves clamped position without rebound;
- pinch never causes content snap-back;
- card activation does not become accidental pan;
- Header, selector and Bottom Tab Bar remain stationary at every scale;
- both Header buttons are visible matching plaques below Dynamic Island;
- Bottom icons and labels match the Stark SolarPower visual scale;
- integration/repository icon is present and recognizable in installed/distribution surfaces.

