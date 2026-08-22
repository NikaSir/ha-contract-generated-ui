# ADR-001: Integration-owned specialized dashboards

**Status:** Accepted  
**Date:** 2026-08-22

## Context

Home Assistant NikaS has two distinct UI responsibilities:

1. a house-wide overview and navigation layer (`Дом`, `Инфраструктура`, `Действия` and other cross-domain surfaces);
2. deep, device- or domain-specific interfaces for complex integrations such as irrigation, robot vacuum, router/failover and UPS telemetry.

A central dashboard generator can reliably compose verified high-level state and navigation, but it should not become the owner of every domain-specific interaction model. The integration that defines the entities, actions and semantics has the best knowledge of how its detailed UI should behave.

## Decision

### 1. Specialized dashboard ownership

A custom integration **owns its specialized dashboard when the device/domain requires a deep interface**.

The integration owner is responsible for the dashboard's:

- information hierarchy;
- entity/action mapping;
- control semantics and safety;
- status and diagnostic interpretation;
- mobile/desktop layout;
- versioning and compatibility with the integration;
- detailed UX that may approximate the vendor application where useful.

Examples:

- `ha-ho-sc-8w` owns the detailed irrigation dashboard;
- `ha-s8-omni` owns the detailed S8 OMNI dashboard;
- `ha-keenetic-hero-4g` owns the detailed router/WAN/LTE dashboard;
- the Stark SolarPower integration owns detailed UPS dashboards.

### 2. Role of Contract Generated UI

`ha-contract-generated-ui` remains the **house-wide overview, composition and navigation layer**.

It may display verified summary states from specialized integrations, but it should prefer a deep link to the integration-owned dashboard instead of duplicating the complete device application.

Its responsibilities are:

- cross-domain dashboards and views;
- concise operational summaries;
- active events and reliability indicators;
- consistent house-wide navigation;
- links/cards/buttons that open specialized dashboards;
- semantic validation of the navigation target when that target is declared as a contract dependency.

### 3. No duplicated ownership

Detailed controls should have **one canonical UI owner**.

A central dashboard may expose selected quick actions when explicitly justified, but it must not silently fork or independently reimplement the integration's full interaction model.

### 4. Specialized dashboard contract

An integration-owned dashboard should expose stable metadata that can be consumed by the central UI. The exact schema may evolve, but the minimum contract is:

- stable panel/dashboard id;
- title;
- route/path;
- icon;
- owner/integration id;
- optional sidebar visibility;
- optional preferred entry view;
- stable canonical parent route for Header Back;
- compatibility/version metadata where required.

Conceptual example:

```yaml
panel:
  id: irrigation
  title: Полив
  path: /dashboard-irrigation
  parent_route: /dashboard-actions
  icon: mdi:sprinkler
  owner: ha-ho-sc-8w
  expose_in_generated_ui: true
  navigation:
    header_back: explicit_parent_route
    primary_navigation: fixed_bottom_bar
```

This metadata describes navigation. It does not give `ha-contract-generated-ui` ownership of the specialized panel contents.

### 4.1. Unified application shell

Every integration-owned specialized dashboard follows the normative [Home Assistant NikaS specialized-panel UI standard](SPECIALIZED_PANEL_UI_STANDARD.md).

The shell contract is:

- Header Back uses `mdi:arrow-left` and an **explicit Home Assistant navigation** to the declared parent route;
- browser history is not an application-navigation contract;
- Header is reserved for leaving the panel and global panel actions;
- primary internal sections live in an iOS-safe **fixed bottom navigation bar**;
- top primary tabs are not used;
- factual Home Assistant entities retain long press → native more-info;
- Header and bottom navigation never execute entity/device actions on hold or double tap.

Canonical parent routes are:

- HO-SC-8W irrigation → `/dashboard-actions`;
- S8 OMNI vacuum → `/dashboard-actions`;
- Keenetic Hero 4G+ → `/dashboard-infrastructure/overview`;
- Stark SolarPower UPS → `/dashboard-infrastructure/overview`.

### 5. Runtime and release boundary

Specialized dashboard code/configuration is released with its owning integration whenever practical. The integration and its dashboard therefore evolve together and can be tested in the same repository/release pipeline.

`ha-contract-generated-ui` should consume only the stable navigation/summary contract required for cross-domain composition.

## Consequences

### Positive

- domain knowledge remains with the component that owns the entities and actions;
- detailed dashboards can evolve without bloating the central generator;
- central panels remain compact and operational;
- device-specific UI can closely match the natural workflow of the device or vendor application;
- release/version compatibility is easier to reason about;
- failures and `unknown`/`unavailable` semantics remain owned by the integration that understands them;
- every specialized dashboard has predictable Back semantics and a common one-handed mobile navigation model.

### Costs

- integrations with rich domains must maintain dashboard code/configuration in addition to entities;
- a common navigation metadata contract is required;
- visual consistency must be maintained through shared project rules rather than a single renderer owning every screen;
- canonical parent routes must be treated as stable application-navigation API.

## Initial implementation order

1. `ha-ho-sc-8w` — irrigation dashboard;
2. `ha-s8-omni` — robot and station dashboard;
3. `ha-keenetic-hero-4g` — WAN/LTE/failover dashboard;
4. Stark SolarPower — UPS overview and diagnostics dashboard;
5. stable deep links from house-wide generated dashboards to these integration-owned panels.

## Project rule

> Complex device/domain UI belongs to the integration that owns the domain. Contract Generated UI owns house-wide overview, composition and navigation. Every specialized dashboard uses the NikaS application shell: explicit Header Back + fixed bottom section navigation.
