# NikaS Integration Panel Template v1.0 — reference implementation

This directory is a **copy/adapt reference**, not a runtime dependency.

A specialized integration must copy the relevant structure into its own repository and produce one autonomous production bundle. Do not import files from `ha-contract-generated-ui` at runtime.

## Files

- `panel-shell-reference.js` — working reference for the common application shell and shared primitives;
- `panel-contract.example.json` — machine-readable panel metadata example.

## Adoption sequence

1. Copy `panel-shell-reference.js` into the integration frontend source tree.
2. Rename the custom element and constants for the integration.
3. Set the canonical `parentPath`.
4. Define 3–5 primary tabs.
5. Enable Device Selector only for multiple peer physical devices.
6. Replace `_renderHero()` and `_renderViewContent()` with domain content.
7. Keep Header, safe-area geometry, Bottom Tab Bar, state tones and navigation mechanics unchanged unless the global standard is revised.
8. Bind factual entity blocks to native HA more-info on hold where technically practical.
9. Use only integration-owned/real HA entities and validated integration actions.
10. Build one autonomous production JS bundle and register it through `module_url` with query-string UI-version cache busting.
11. Add CI that rejects runtime imports of previous frontend versions and verifies the committed bundle.
12. Validate on iPhone Pro Max portrait, cold cache, HA restart and remote/Nabu Casa access before acceptance.

## Required integration-specific values

```js
const APP = {
  title: "Example Panel",
  subtitle: "Device model · UI v1.0.0",
  parentPath: "/dashboard-actions",
  tabs: [
    ["overview", "mdi:view-dashboard-outline", "Обзор"],
    ["control", "mdi:tune", "Управление"],
    ["diagnostics", "mdi:stethoscope", "Диагностика"],
  ],
};
```

## Multi-device rule

If the application owns peer devices, preserve:

```text
Header
Device Selector
Selected device content
Bottom Tab Bar
```

Device order is fixed. Selection persists across tabs. The selected device is never reordered to the first slot.

## Non-goals

The template does not provide:

- direct device API calls;
- raw Tuya/RCI/SNMP writes;
- fake Home Assistant entities;
- a shared CDN/module dependency;
- domain-specific business logic.

Those boundaries remain owned by each integration.
