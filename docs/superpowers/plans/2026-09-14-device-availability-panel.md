# Device Availability Technical Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an integration-owned NikaS technical panel that presents live Entity Availability group health at `/dashboard-device-availability`.

**Architecture:** A small Python lifecycle module registers one collision-safe Home Assistant custom panel and its static JavaScript module. The JavaScript owns group discovery, normalization and aggregation from public Home Assistant states; a Web Component renders the fixed NikaS shell and applies state changes through point updates.

**Tech Stack:** Home Assistant custom integration APIs, Python 3.12, JavaScript Web Components, Node test harness, pytest.

**Spec:** `docs/superpowers/specs/2026-09-14-device-availability-panel-design.md`

## Global Constraints

- Entity Availability 0.5.3 is an optional runtime dependency.
- Route: `/dashboard-device-availability`; parent and safe return: `/home/overview`.
- The integration owns only this technical route and removes only the route it registered.
- Fixed header/footer, safe-area insets, one work viewport and work-area-only zoom follow NikaS UI Standard v2.2.
- Telemetry updates patch existing DOM nodes and never rebuild the panel shell.
- Group monitoring configuration remains in Entity Availability.

---

### Task 1: Revise repository ownership and route registry

**Files:**
- Modify: `docs/REPOSITORY_SCOPE.md`
- Modify: `README.md`
- Modify: `navigation/main.yaml`
- Modify: `custom_components/contract_generated_ui/bundled_sources/navigation/main.yaml`
- Modify: `tests/test_repository_scope.py`
- Modify: `tests/test_navigation_registry.py`

**Interfaces:**
- Consumes: canonical `specialized_routes` navigation mapping.
- Produces: `device_availability` route with path `/dashboard-device-availability` and `/home/overview` parent/return routes.

- [ ] **Step 1: Write failing tests** that assert the repository owns exactly one technical panel and both navigation copies expose the new specialized route.
- [ ] **Step 2: Run** `pytest -q tests/test_repository_scope.py tests/test_navigation_registry.py` and verify failure from the old no-panel assertions and missing route.
- [ ] **Step 3: Update scope, README and both navigation copies** with the narrow ownership exception and new route.
- [ ] **Step 4: Run the same tests** and verify they pass.
- [ ] **Step 5: Commit** with `feat: declare device availability panel ownership`.

### Task 2: Add panel lifecycle and static asset registration

**Files:**
- Create: `custom_components/contract_generated_ui/device_availability_panel.py`
- Modify: `custom_components/contract_generated_ui/const.py`
- Modify: `custom_components/contract_generated_ui/__init__.py`
- Create: `tests/test_device_availability_panel.py`
- Modify: `tests/test_repository_scope.py`

**Interfaces:**
- Produces: `async_register_device_availability_panel(hass) -> bool` and `async_unregister_device_availability_panel(hass) -> None`.
- Stores owned route under `hass.data[DOMAIN][DEVICE_AVAILABILITY_PANEL_PATH]`.
- Serves module URL `/contract_generated_ui/frontend/device-availability-panel.js?build=b001`.

- [ ] **Step 1: Write failing lifecycle tests** using lightweight fake Home Assistant/frontend objects. Assert registration occurs before coordinator refresh, collisions are preserved, missing source integration does not remove the route, and unload removes only the recorded route.
- [ ] **Step 2: Run** `pytest -q tests/test_device_availability_panel.py` and verify import/behavior failures.
- [ ] **Step 3: Implement constants and lifecycle module** using `panel_custom.async_register_panel`, `frontend.async_panel_exists` and `frontend.async_remove_panel`.
- [ ] **Step 4: Integrate setup and unload** in `__init__.py`; register the static directory once with `StaticPathConfig`.
- [ ] **Step 5: Run focused tests** and verify they pass.
- [ ] **Step 6: Commit** with `feat: register device availability technical panel`.

### Task 3: Build and verify Entity Availability data normalization

**Files:**
- Create: `custom_components/contract_generated_ui/frontend/device-availability-model.js`
- Create: `tests/device_availability_model_harness.mjs`
- Create: `tests/test_device_availability_frontend.py`

**Interfaces:**
- Produces: `discoverAvailabilityGroups(states)`, `buildAvailabilitySnapshot(states)`, `filterAvailabilityItems(snapshot, query, group, condition)`.
- Returns snapshot shape `{status, totals, groups, items, diagnostics, updateEntityIds}`.

- [ ] **Step 1: Write failing Node-backed pytest cases** with literal 0.5.3-style group summary, offline, stale, battery, signal and recovery fixtures.
- [ ] **Step 2: Run** `pytest -q tests/test_device_availability_frontend.py` and verify missing-module failure.
- [ ] **Step 3: Implement discovery and normalization** with tolerant companion-sensor lookup and explicit `no_integration`, `empty`, `healthy`, `problem`, and `no_data` states.
- [ ] **Step 4: Implement problem-first sorting and search/filter functions** without reading private `.storage` data.
- [ ] **Step 5: Run focused tests** and verify aggregate counts, optional-data fallback and representative entity IDs.
- [ ] **Step 6: Commit** with `feat: normalize Entity Availability state data`.

### Task 4: Implement the NikaS frontend panel

**Files:**
- Create: `custom_components/contract_generated_ui/frontend/device-availability-panel.js`
- Create: `tests/device_availability_panel_harness.mjs`
- Modify: `tests/test_device_availability_frontend.py`

**Interfaces:**
- Consumes: Task 3 snapshot functions and Home Assistant `hass.states` / `hass.callService`.
- Produces: custom element `nikas-device-availability-panel` with Summary, Devices and Diagnostics tabs.

- [ ] **Step 1: Write failing behavior tests** for stable shell identity, targeted state patching, built-in overview navigation, more-info event payload and refresh entity list.
- [ ] **Step 2: Run focused tests** and verify failures because the panel module is absent.
- [ ] **Step 3: Implement one-time shell render** with fixed header/footer and three tab containers; adapt the canonical shell interaction/zoom code into the autonomous bundle.
- [ ] **Step 4: Implement Summary, Devices and Diagnostics views** with light/dark theme tokens, responsive cards/table, search and filters.
- [ ] **Step 5: Implement point updates** by recomputing the pure snapshot and updating retained nodes/rows without replacing the shell.
- [ ] **Step 6: Implement refresh feedback**: block duplicates, call `homeassistant.update_entity`, hold busy for at least 900 ms and show success/error result without changing geometry.
- [ ] **Step 7: Run focused tests** and verify all frontend behaviors pass.
- [ ] **Step 8: Commit** with `feat: add device availability panel interface`.

### Task 5: Release metadata and full verification

**Files:**
- Modify: `custom_components/contract_generated_ui/manifest.json`
- Modify: `CHANGELOG.md`
- Modify: `tests/test_repository_scope.py`
- Modify: `.nikas-ui-standard.json` only if the repository's pinned scope metadata requires reconciliation.

**Interfaces:**
- Produces: installable development release with the technical panel packaged.

- [ ] **Step 1: Update version assertions first** to the chosen next patch/minor version and run them to verify failure.
- [ ] **Step 2: Update manifest and changelog** with Entity Availability compatibility, route and fallback behavior.
- [ ] **Step 3: Run** `python -m pytest -q` and resolve only failures caused by the feature or revised repository boundary.
- [ ] **Step 4: Run** `python -m generator validate .` and `git diff --check`.
- [ ] **Step 5: Run the Node harnesses directly** to confirm production modules parse and behavioral cases pass.
- [ ] **Step 6: Commit** with `chore: prepare device availability panel release`.
