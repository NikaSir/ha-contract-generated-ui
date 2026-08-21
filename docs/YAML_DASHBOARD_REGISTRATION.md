# Register generated dashboards in Home Assistant

Contract Generated UI `0.3.0` exports generated Lovelace YAML but does not edit Home Assistant `.storage` or `configuration.yaml` automatically.

## Generated files

After **Generate dashboards / Сгенерировать панели** succeeds, runtime output is written under:

```text
/config/contract_generated_ui/generated/
```

For each panel manifest the integration writes:

- `<manifest-id>.yaml` — deterministic Lovelace dashboard candidate;
- `<manifest-id>.meta.json` — RenderTrace with source bindings, semantic model and SHA-256.

It also writes:

```text
/config/contract_generated_ui/generated/lovelace_configuration_snippet.yaml
```

The snippet uses Home Assistant's supported YAML dashboard configuration shape.

## Important safety rule

The generated snippet is **merge input**, not an instruction to overwrite `configuration.yaml`.

If `configuration.yaml` already contains a top-level `lovelace:` section, merge the generated `dashboards:` entries into it. Preserve existing resources, resource mode, and other dashboards.

Example generated shape:

```yaml
lovelace:
  dashboards:
    dashboard-infrastructure:
      mode: yaml
      filename: contract_generated_ui/generated/infrastructure.yaml
      title: Infrastructure
      show_in_sidebar: true
      require_admin: false
```

Home Assistant requires additional YAML dashboard URL keys to contain a hyphen. Contract Generated UI validates this rule when exporting the snippet.

## Deployment boundary

Version `0.3.0` deliberately stops before applying the snippet. The integration does not:

- edit `configuration.yaml`;
- write Home Assistant `.storage` Lovelace files;
- register internal Lovelace collections through private Home Assistant APIs;
- replace existing dashboards.

This keeps generation deterministic and reviewable while dashboard registration remains an explicit Home Assistant configuration change.

## Verification sequence

1. Ensure **Source status / Состояние источников** is `valid / Корректно`.
2. Press **Generate dashboards / Сгенерировать панели**.
3. Check button attributes for generated file paths, dashboard SHA-256, and registration snippet path.
4. Review the generated YAML and RenderTrace.
5. Merge the registration entry into `configuration.yaml` only after review.
6. Validate Home Assistant configuration and restart/reload as required.
7. Keep the previous generated candidate/trace available for rollback and semantic diff.
