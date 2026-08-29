# NikaS Proven Integration & Panel Patterns

**Status:** LIVING REFERENCE  
**Baseline:** NikaS Specialized Panel UI Standard v1.9  
**Purpose:** concise catalogue of solutions that have proven correct across NikaS Home Assistant work and should be reused when a new integration or panel is written from scratch.

This document intentionally excludes temporary workarounds, superseded implementations and visually acceptable but architecturally weak solutions.

---

## 1. Correct overall architecture

Use this dependency direction:

```text
DEVICE / VENDOR / HA ENTITIES
          ↓
INTEGRATION DATA ACQUISITION
          ↓
NORMALIZED DOMAIN STATE
          ↓
PANEL CONTRACT / ENTITY MAPPING
          ↓
PERSISTENT UI SHELL
          ↓
TARGETED STATE PATCHES
```

The panel must not reverse this direction by guessing backend facts from labels, entity-name conventions or visual state.

---

## 2. Correct backend pattern

### 2.1 One normalized source of live truth

For polled or API-backed devices, use one integration-owned coordinator/domain state object. Individual entities and the panel consume that normalized state instead of independently polling.

Store separately:

- last attempt;
- last successful sample;
- current normalized values;
- availability/source state;
- error metadata safe for diagnostics.

### 2.2 Registry-aware binding

Prefer entity/device registry discovery for related entities. If a fixed entity ID is necessary, declare it as part of the contract and test it explicitly.

### 2.3 Fail closed

If an input is absent, malformed, `unknown` or `unavailable`, return an explicit unavailable/unknown domain result. Never substitute zero or “normal”.

### 2.4 Derived values

Every derived value has documented factual inputs. Calculation is performed in one reusable domain function, not independently in multiple cards.

### 2.5 Write operations

Correct write lifecycle:

```text
EDIT → VALIDATE → APPLY/START/STOP → CONFIRM → BUSY → HA CALL → FACTUAL RESULT
```

Use a registered integration service or discovered HA entity capability. Disable duplicate submissions. Never claim success from button click alone.

---

## 3. Correct frontend shell

The only accepted high-level topology is:

```text
Header                   native scale / persistent
Peer selector (optional) native scale / persistent
Work viewport             sole scroll + zoom owner
Bottom Tab Bar            native scale / persistent
```

### Proven properties

- shell mounted once;
- height-locked phone layout;
- safe area consumed once;
- only the work viewport scrolls;
- no outer HA page scrolling/chaining;
- exactly one zoom viewport;
- fixed chrome never enters transformed content;
- short and long tabs do not move Header/Bottom Bar.

---

## 4. Correct Header pattern

Use v1.9 geometry and semantics:

- left: HA system menu only;
- center: two-line clickable title plaque;
- title line: current specialized-panel name;
- second line: `UI vX.Y.Z`;
- center plaque returns to the factual NikaS source base panel;
- right: maximum one panel-global action, typically Refresh.

Never use:

- separate Back arrow;
- `Назад` text;
- browser `history.back()`;
- integration drawer in the permanent left rail.

---

## 5. Correct navigation pattern

Base panel records the source route immediately before navigation. Specialized panel captures and validates that source once and preserves it across telemetry updates and tab changes.

Navigation is explicit through HA location state (`history.pushState` + `location-changed`), not through browser history semantics.

Only allowed NikaS base route families are accepted. Invalid routes fail closed to the configured safe fallback.

---

## 6. Correct rendering pattern

### Structural mount

Create once:

- Header;
- optional selector;
- viewport/canvas;
- Bottom Tab Bar;
- persistent background/scene layer;
- tab root containers.

### Live update

For each HA update:

1. normalize factual state;
2. schedule at most one animation-frame reconciliation;
3. compare old/new values;
4. patch only changed text/classes/ARIA/CSS variables;
5. do not recreate shell or images;
6. do not trigger unrelated async work.

### Tab switching

Lazy-build a work view once; cache it; reattach/reveal the same subtree on return.

---

## 7. Correct scroll and zoom pattern

### At 100%

- native vertical scroll;
- no transform pan;
- no horizontal scroll;
- transform normalized to origin;
- clicks/hold begin without artificial gesture delay.

### Pinch

- two fingers;
- preserve focal midpoint;
- range 75–200%;
- snap 97–103% to exactly 100%;
- reset with two-finger double tap;
- suppress post-pinch synthetic click;
- cancel pending more-info when a second finger joins.

### Above 100%

- one-finger transform pan allowed;
- each axis enabled only if scaled content exceeds viewport;
- translations clamped to factual content bounds;
- no empty canvas exposure.

---

## 8. Correct typography pattern

Meaningful phone UI text: **12–25 px**.

- captions/navigation/secondary: 12–14 px;
- ordinary labels/status: ~14–16 px;
- prominent values: up to 25 px;
- Header follows its fixed v1.9 pair.

If content does not fit, redesign the card. Do not shrink operational text below 12 px.

---

## 9. Correct connection/freshness indicator

Introduce only by explicit request.

Line 1 — transport:

- `Локально`;
- `Облако`;
- `Резерв`;
- `Нет связи`;
- `Нет данных`.

Line 2 — freshness:

- `Данные актуальны`;
- `Данные устарели`;
- `Нет данных`.

Patch this as a stable DOM subtree. No flashing, pulsing or remounting.

---

## 10. Correct operational page pattern

The first page should answer immediately:

- what device/system is this;
- what state is it in;
- what path/source is active if operationally important;
- what primary measurements matter now;
- is action required.

Avoid raw technical detail, duplicate telemetry and configuration internals on the first page.

Use a physical/state scene only where it increases comprehension.

---

## 11. Correct diagnostics pattern

A dedicated Diagnostics tab should expose, where useful:

- every enabled state-bearing entity actually bound to the target device(s);
- source entity ID;
- raw state;
- raw attributes;
- last changed / last updated;
- device/model identifiers;
- integration/UI version;
- polling/source/freshness metadata;
- safe recent error state.

Diagnostics must reflect reality, not a curated “healthy” view.

---

## 12. Correct statistics/history architecture

History is isolated from live rendering.

### Proven request lifecycle

For each period:

```text
period key
  ↓
load object (cached)
  ↓
small bounded graph requests
  ↓
max concurrency = 2
  ↓
progressive per-graph render
  ↓
terminal state per graph
```

Validated periods may include 24 h / 7 d / 30 d / 12 m according to product requirements.

### Proven rules

- Recorder is accessed through authenticated HA APIs;
- do not rely on Lovelace helper availability inside `panel_custom`;
- cache both in-flight and completed periods;
- switching away does not cancel/restart useful work unnecessarily;
- switching back reuses the load;
- live telemetry never restarts history;
- Header Refresh invalidates only the active period;
- terminal timeout: **60 s per graph** in the proven LIDER pattern;
- history requests limited to **2 concurrent graph requests** in that pattern;
- each graph ends as data / no data / Recorder unavailable;
- render completed graphs progressively;
- limit rendered SVG points rather than corrupting period semantics.

---

## 13. Correct performance pattern

### Startup

Display persistent shell and deterministic loading content immediately. Avoid a blank white frame.

### State updates

- max one animation-frame reconciliation;
- no redundant DOM writes;
- no unchanged image `src` rewrites;
- no full active-tab regeneration;
- no history call from telemetry updates.

### Assets

- local only;
- size close to display need;
- WebP for large scene/background imagery where appropriate;
- persistent mounted image nodes.

### Repeated interaction test

At minimum verify ten tab switches and repeated telemetry cycles without white frames, flicker, duplicated listeners or geometry movement.

---

## 14. Correct source-code structure

A clean specialized panel frontend should make these responsibilities visibly separate:

```text
constants/version
navigation
state normalization
shell mount
view construction
live patchers
formatters
zoom/gesture controller
history loader/cache
command handlers
```

Avoid one giant class method that mixes data discovery, HTML generation, navigation, Recorder calls and device commands.

For the integration backend, follow HA platform conventions and keep vendor/API logic, coordinator/domain normalization, entity platforms, services and panel registration separated.

---

## 15. Correct production packaging

- one autonomous production JS entrypoint;
- no runtime imports/dynamic imports/CDN dependencies;
- build inputs may be modular, production output deterministic;
- CI regenerates/checks bundle parity;
- UI version shown in Header matches contract, panel manifest, production cache key and component registration;
- changed runtime behavior increments UI version/cache key;
- no duplicate active shell/zoom/navigation engines in the shipped bundle.

---

## 16. Correct CI pattern

A repository should automatically reject known regressions.

Include checks for:

- Python/JSON/YAML validity;
- HACS and Hassfest as applicable;
- contract/schema validity;
- deterministic bundle parity;
- JS syntax;
- version coherence;
- one viewport/shell;
- no routine full `shadowRoot.innerHTML` rendering;
- stable DOM behavior;
- navigation contract;
- typography limits;
- no runtime imports;
- statistics single-flight/cache/concurrency behavior;
- command duplicate-submit protection where writes exist.

A learned defect should preferably result in a new automated guard.

---

## 17. Correct release/merge pattern

Use a focused branch and PR. Merge only after all required checks are green. Do not create tags or GitHub Releases unless explicitly requested.

After merge, acceptance on the target phone is still required for behavior that cannot be proven statically: inertial scroll, safe areas, pinch/click isolation, iOS WebView flicker, history responsiveness and touch controls.

---

## 18. Correct real-device acceptance checklist

### Shell

- Header cannot be shifted upward;
- Bottom Bar cannot be shifted;
- short page does not collapse shell;
- long page remains scrollable only in work viewport.

### Rendering

- no white frame at startup after shell appears;
- no flicker from telemetry;
- no background/image flash;
- no redraw on simple value change.

### Navigation

- HA menu works;
- center plaque returns to the actual source base panel;
- all Bottom Bar tabs work repeatedly.

### Zoom

- pinch is smooth and bounded;
- 100% is native scroll;
- two-finger double tap resets;
- pinch does not trigger card action/history/more-info.

### Data

- unavailable/unknown are explicit;
- no false green state;
- transport/freshness factual when present.

### Statistics

- 24h → 7d → 24h → 7d does not duplicate loads;
- graph results appear progressively;
- no indefinite loading;
- live telemetry remains responsive during Recorder work.

### Commands

- disabled when unavailable;
- confirmation where required;
- busy state prevents duplicate submission;
- failure is visible;
- success comes from factual state/call completion, not optimistic animation.

---

## 19. Project-specific proven lessons to carry forward

### LIDER

- fixed shell and stable DOM solved Header/Bottom Bar movement and flicker;
- Recorder should use direct authenticated HA history rather than Lovelace helpers;
- per-graph requests + concurrency 2 + cached periods solved period-switch loading failures;
- physical statistics grouping is better than arbitrary entity grouping;
- `До стабилизаторов / После стабилизаторов / Неотключаемая линия` is factual; generation/export must not be invented.

### Stark SolarPower

- early shell/background rendering materially improves perceived startup;
- persistent optimized WebP assets avoid visible delayed scene construction;
- fixed chrome + work-only zoom/scroll is the visual baseline.

### Keenetic

- network diagrams should show only real active paths; remove grey decorative branches and duplicated telemetry;
- active-channel operational data belongs with the active channel rather than being repeated across the scene;
- reserve capability and active reserve are distinct facts.

### StarLine

- explicit visual states can communicate security/door/ignition better than one generic scene;
- fixed Header/Bottom Bar and meaningful text size remain mandatory even for highly visual pages;
- do not introduce the optional connection indicator unless requested.

### HO-SC-8W irrigation

- command semantics must match device reality;
- per-zone duration + queue is a separate workflow from controller power state;
- settings writes require Apply + confirmation rather than changing equipment immediately on every input event;
- seasonal correction is a reusable example of safe write UX;
- program state and manual queue should be modeled separately.

### S8 OMNI

- do not mix automatic station settings with immediate run/stop controls;
- state imagery should cover materially different operating states;
- retain explicit “unfinished” reminder UI only when it is intentional product information, not accidental developer text.

### Base panels / generated UI

- navigation links among base and specialized panels are part of the architecture, not incidental click handlers;
- equipment lists and room views should be generated/filterable from factual registry metadata/labels rather than manually curated copies;
- operational view and Infrastructure diagnostics should remain distinct.

---

## 20. Rule for future work

When creating a new integration or panel, start from this file and the normative v1.9 standard rather than copying an old repository wholesale.

Copy **patterns**, contracts, guards and tests — not historical implementation baggage.

If a new solution proves better:

1. confirm it on CI and target device;
2. update the normative rule if required;
3. update this proven-pattern file;
4. add a regression guard;
5. only then propagate it to other integrations.