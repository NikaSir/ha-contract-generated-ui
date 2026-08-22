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
    views = []
    spec: dict = {
        "dashboard_path": path,
        "views": views,
    }
    if subpanel:
        spec["subpanel"] = {
            "template": "standard_v1",
            "navigation": "main",
            "parent": "main.section",
        }
        views.extend(
            [
                {
                    "id": "overview",
                    "title": "Overview",
                    "icon": "mdi:view-dashboard-outline",
                    "path": "overview",
                    "order": 0,
                    "renderer": "subpanel_placeholder_v1",
                    "placeholder": "Overview",
                    "modules": [],
                },
                {
                    "id": "service",
                    "title": "Service",
                    "icon": "mdi:stethoscope",
                    "path": "service",
                    "order": 1,
                    "renderer": "subpanel_placeholder_v1",
                    "placeholder": "Service",
                    "modules": [],
                },
            ]
        )
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


def _navigation() -> dict:
    return {
        "api_version": "nikas.home-assistant/navigation/v1",
        "kind": "NavigationContract",
        "metadata": {"id": "main", "version": "1.0.0"},
        "spec": {
            "routes": {
                "home": {"title": "Home", "path": "/dashboard-main"},
                "main.section": {
                    "title": "Section",
                    "path": "/dashboard-main/section",
                    "parent": "home",
                },
            },
            "global_tabs": [
                {
                    "id": "home",
                    "route": "home",
                    "title": "Home",
                    "icon": "mdi:home-outline",
                }
            ],
            "tab_groups": [],
        },
    }


def test_embedded_subpanel_is_not_registered_separately(tmp_path: Path) -> None:
    source = tmp_path / "contract_generated_ui"
    manifests = source / "manifests"
    navigation = source / "navigation"
    generated = source / "generated"
    manifests.mkdir(parents=True)
    navigation.mkdir(parents=True)

    (navigation / "main.yaml").write_text(
        yaml.safe_dump(_navigation(), sort_keys=False), encoding="utf-8"
    )
    (manifests / "main.yaml").write_text(
        yaml.safe_dump(
            _manifest("main", "/dashboard-main", subpanel=False),
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (manifests / "child.yaml").write_text(
        yaml.safe_dump(
            _manifest("child", "/dashboard-main", subpanel=True),
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
    assert set(dashboards) == {"dashboard-main"}
    assert dashboards["dashboard-main"]["show_in_sidebar"] is True


def test_standalone_subpanel_remains_registered_hidden(tmp_path: Path) -> None:
    source = tmp_path / "contract_generated_ui"
    manifests = source / "manifests"
    navigation = source / "navigation"
    generated = source / "generated"
    manifests.mkdir(parents=True)
    navigation.mkdir(parents=True)

    (navigation / "main.yaml").write_text(
        yaml.safe_dump(_navigation(), sort_keys=False), encoding="utf-8"
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
    assert dashboards["dashboard-child"]["show_in_sidebar"] is False
