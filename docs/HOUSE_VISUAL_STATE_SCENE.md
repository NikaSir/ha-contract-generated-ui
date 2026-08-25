# House Visual State Scene v1

Contract Generated UI `0.30.0` replaces the compact `Дом сейчас` tile cluster with a full-screen visual state scene on the House v11 release-candidate route.

## Purpose

The first screen answers one question: **what is happening with the house right now?**

The scene visualizes only high-value household states:

- safety;
- open contacts;
- motion;
- lighting;
- climate activity;
- cameras;
- weather/time context;
- windows as an aggregate category;
- physical sectional-gate state;
- physical entrance-door state;
- incoming electrical quality;
- drinking-water pressure;
- internet availability;
- heating activity.

Detailed telemetry remains below the hero scene or in integration-owned panels.

## Layering contract

The scene follows the same asset discipline accepted for Stark SolarPower:

1. **Decorative asset** — `frontend/assets/house-hero-dusk-v1.svg` contains no Home Assistant entity ids, state text or baked readings.
2. **Live frontend layer** — `frontend/nikas-house-hero.js` reads the entity ids supplied by the generated House manifest output and renders all values/status text dynamically.
3. **Semantic source layer** — `house_home_v1` passes only roles already resolved from verified private `SemanticInventory`.
4. **Navigation layer** — the hero receives manifest-owned routes; no deep subsystem path is invented in the frontend component.

The asset is served locally from:

`/contract_generated_ui/frontend/assets/house-hero-dusk-v1.svg?build=0300b001`

No Base64 or external CDN is used.

## Truthfulness rules

- `unknown` and `unavailable` never become green/normal.
- Electrical quality uses the same thresholds as the accepted House/Infrastructure field logic:
  - emergency: `<198 V` or `>242 V`;
  - deviation: `<205 V` or `>235 V`;
  - attention: `<210 V` or `>230 V`;
  - otherwise normal.
- Sectional-gate and entrance-door outlines use only their physical access sensors.
- The window outline is an aggregate visual cue: it means one or more bound window contacts are open; it is not an invented mapping of a specific physical window onto the decorative façade.
- If the renderer cannot classify dedicated window entity ids, the opening set is used as a conservative aggregate instead of fabricating a location.

## Mobile composition

On iPhone portrait the scene occupies approximately the full usable first screen between the Home Assistant header and the global `Дом / Действия / Инфра` tab bar.

The scene contains:

- five compact top status cells;
- weather and local time overlays;
- camera health pill;
- category/access callouts over the house artwork;
- four utility cards at the bottom, collapsing to a 2×2 grid on narrow screens.

After the visual scene, the existing protected House sequence continues:

1. `Активные события`;
2. `Ресурсы`;
3. `Отопление и ГВС`;
4. `Автомобили`;
5. `Ключевые точки доступа`.

## Field-test gate

`0.30.0` is a live visual field-test step, not a production `/dashboard-house` cut-over. Acceptance requires:

- the custom element and local asset load without frontend-resource errors;
- the scene fits one iPhone portrait screen without colliding with the global bottom bar;
- the status colors match the existing House/Infrastructure semantics;
- `unknown` / `unavailable` are visible as unreliable states;
- window/gate/door callouts do not imply unsupported physical-location knowledge;
- all scene navigation targets open their existing canonical panels/views;
- lower House sections remain unchanged and scroll correctly below the hero.
