# Device Availability Problems Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `Проблемы` tab that groups monitored devices by their highest-priority problem while preserving secondary problems and separating non-essential rows.

**Architecture:** Extend each availability item with an ordered `conditions` list and derive problem sections from the existing snapshot. Render the new view inside the existing persistent shell, reusing device rows and Home Assistant more-info behavior without changing route ownership or refresh behavior.

**Tech Stack:** JavaScript ES modules, Home Assistant custom panel Web Components, Python pytest with Node harnesses.

**Spec:** `docs/superpowers/specs/2026-09-14-device-availability-panel-design.md`

## Global Constraints

- Tab order is `Сводка → Проблемы → Устройства → Диагностика`.
- Primary priority is `offline → stale → low_battery → poor_signal → unknown`.
- Each row appears in one primary group; additional conditions appear as badges.
- Non-essential problem rows appear in a neutral block below essential problems.
- Telemetry patches the active work view and never rebuilds the shell.
- UI version uses `MAJOR.MINOR.PATCH-betaNNN` and is shown in full.

## Review Focus

- A device with multiple problems appears once, in its highest-priority group, with every secondary badge.
- A non-essential offline device never appears among essential alerts or raises aggregate status.
- An underlying `unknown` entity not already classified by Entity Availability is visible as `unknown`, while a source-classified offline row remains offline.
- An empty problem set renders the calm empty state instead of empty headings.
- Four bottom tabs remain usable on a narrow phone without horizontal overflow or shell replacement.

---

### Task 1: Problem grouping model

**Files:**
- Modify: `custom_components/contract_generated_ui/frontend/device-availability-model.js`
- Modify: `tests/device_availability_model_harness.mjs`
- Test: `tests/test_device_availability_frontend.py`

**Interfaces:**
- Consumes: `buildAvailabilitySnapshot(states)` and each collapsed availability item.
- Produces: item property `conditions: string[]` and `buildAvailabilityProblemGroups(snapshot)` returning `{essential, nonEssential}` arrays of `{condition, items}`.

- [ ] **Step 1: Write failing tests** for ordered multi-condition rows, essential grouping, non-essential separation, unknown source state, and the empty result.
- [ ] **Step 2: Run** `python -m pytest tests/test_device_availability_frontend.py -k 'problem_groups or multiple_problem or unknown_problem' -v` and confirm failure because the grouping interface is absent.
- [ ] **Step 3: Implement** ordered condition extraction and `buildAvailabilityProblemGroups`; preserve `condition` as the first ordered condition for existing callers.
- [ ] **Step 4: Run** `python -m pytest tests/test_device_availability_frontend.py -v` and confirm all frontend model tests pass.
- [ ] **Step 5: Commit** model and tests with `feat: group availability problems by priority`.

### Task 2: Problems tab and responsive presentation

**Files:**
- Modify: `custom_components/contract_generated_ui/frontend/device-availability-panel.js`
- Modify: `tests/device_availability_panel_harness.mjs`
- Test: `tests/test_device_availability_frontend.py`
- Test: `tests/test_device_availability_header_browser.py`

**Interfaces:**
- Consumes: `buildAvailabilityProblemGroups(snapshot)` and item `conditions` from Task 1.
- Produces: `problems` tab, grouped section markup, secondary badges, calm empty state, four-column bottom navigation.

- [ ] **Step 1: Write failing harness tests** asserting the four-tab order, grouped essential headings, one device row with secondary badges, neutral non-essential heading, empty state, and Problems-tab telemetry without shell writes.
- [ ] **Step 2: Run** `python -m pytest tests/test_device_availability_frontend.py -k 'problems_tab or problem_view' -v` and confirm the view is missing.
- [ ] **Step 3: Implement** the fourth tab, active-view dispatch, grouped flat-list markup, compact badges and responsive four-column navigation.
- [ ] **Step 4: Add/adjust browser assertions** for four equal tab hit targets and no horizontal overflow at 320 px; run them when Playwright is available.
- [ ] **Step 5: Run** `python -m pytest tests/test_device_availability_frontend.py tests/test_device_availability_header_browser.py -v` and confirm pass or the documented Playwright skip only.
- [ ] **Step 6: Commit** UI and tests with `feat: add availability problems tab`.

### Task 3: Release metadata and repository verification

**Files:**
- Modify: `custom_components/contract_generated_ui/frontend/device-availability-panel.js`
- Modify: `custom_components/contract_generated_ui/const.py`
- Modify: `custom_components/contract_generated_ui/manifest.json`
- Modify: `tests/test_device_availability_beta004_source.py`
- Modify: `tests/test_device_availability_frontend.py`
- Modify: `tests/test_device_availability_panel.py`
- Modify: `tests/test_repository_scope.py`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: completed Problems tab.
- Produces: UI `1.0.0-beta005`, asset build `b005`, integration `0.42.0`, and matching regression/release metadata.

- [ ] **Step 1: Update release tests first** to expect UI `1.0.0-beta005`, build `b005`, and integration `0.42.0`.
- [ ] **Step 2: Run** `python -m pytest tests/test_device_availability_beta004_source.py tests/test_device_availability_panel.py tests/test_repository_scope.py tests/test_device_availability_frontend.py -v` and confirm version failures.
- [ ] **Step 3: Update** runtime version/build/manifest values and add the Problems-tab release entry to `CHANGELOG.md`.
- [ ] **Step 4: Run** the same focused command and confirm pass.
- [ ] **Step 5: Run** `python -m pytest` plus `python scripts/check_nikas_ui_standard.py` and JavaScript syntax checks for both frontend modules.
- [ ] **Step 6: Commit** with `chore: release device availability beta005`.
