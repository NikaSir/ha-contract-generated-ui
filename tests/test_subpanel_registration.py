from __future__ import annotations

from pathlib import Path

import yaml

from custom_components.contract_generated_ui.runtime_registration import (
    write_lovelace_registration_snippet,
)


def _manifest(
    manifest_id: str,
    path: str,
    *,
    subpanel: bool,
) -> dict:
    spec: dict = {
        "dashboard_path": path,
        "views": [],
    }
    if subpanel:
        spec["subpanel"] = {
            "template": "standard_v1",
            "navigation": "main",
            "parent": "home",
        }
    return {
        "api_version": "nikas.home-assistant/panel-manifest/v1",
        "kind": "PanelManifest",
        "metadata": {
            "id": manifest_id,
            "title": manifest_id.title(),
            "version": "1.0",
        },
        "spec": spec,
    }


def test_generated_application_subpanels_are_not_lovelace_registered(tmp_path: Path) -> None:
    source = tmp_path / "contract_generated_ui"
    manifests = source / "manifests"
    generated = source / "generated"
    manifests.mkdir(parents=True)

    (manifests / "main.yaml").write_text(
        yaml.safe_dump(
            _manifest("main", "/dashboard-main", subpanel=False),
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (manifests / "child.yaml").write_text(
        yaml.safe_dump(
            _manifest("child", "/dashboard-child", subpanel=True),
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    result = write_lovelace_registration_snippet(source, generated)
    document = yaml.safe_load(
        "\n".join(
            line
            for line in result.path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("#")
        )
    )
    dashboards = document["lovelace"]["dashboards"]
    assert result.dashboard_count == 1
    assert "dashboard-main" in dashboards
    assert "dashboard-child" not in dashboards


def test_specialized_panels_are_not_lovelace_registered(tmp_path: Path) -> None:
    source = tmp_path / "contract_generated_ui"
    manifests = source / "manifests"
    generated = source / "generated"
    manifests.mkdir(parents=True)

    main = _manifest("main", "/dashboard-main", subpanel=False)
    specialized = _manifest("house", "/dashboard-house-v11", subpanel=False)
    specialized["spec"]["specialized_panel"] = {"template": "house_overview_v1"}
    (manifests / "main.yaml").write_text(
        yaml.safe_dump(main, sort_keys=False), encoding="utf-8"
    )
    (manifests / "house.yaml").write_text(
        yaml.safe_dump(specialized, sort_keys=False), encoding="utf-8"
    )

    result = write_lovelace_registration_snippet(source, generated)
    document = yaml.safe_load(result.path.read_text(encoding="utf-8"))
    dashboards = document["lovelace"]["dashboards"]
    assert result.dashboard_count == 1
    assert "dashboard-main" in dashboards
    assert "dashboard-house-v11" not in dashboards
