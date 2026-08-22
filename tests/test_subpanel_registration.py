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


def test_generated_subpanels_are_registered_but_hidden_from_sidebar(tmp_path: Path) -> None:
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
    assert dashboards["dashboard-main"]["show_in_sidebar"] is True
    assert dashboards["dashboard-child"]["show_in_sidebar"] is False
