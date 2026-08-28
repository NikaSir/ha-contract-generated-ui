from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from generator.subpanel_shell import apply_navigation_shell, compile_navigation_registry

ROOT = Path(__file__).parents[1]
CANDIDATE_MANIFEST = ROOT / "staged" / "irrigation" / "panel-manifest.yaml"
CANDIDATE_DASHBOARD = "/dashboard-irrigation-generated"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _sections_dashboard(view_count: int) -> dict:
    return {
        "views": [
            {
                "title": f"Tab {index}",
                "path": f"tab-{index}",
                "type": "sections",
                "max_columns": 1,
                "sections": [
                    {
                        "type": "grid",
                        "cards": [{"type": "markdown", "content": f"content {index}"}],
                    }
                ],
            }
            for index in range(view_count)
        ]
    }


def test_irrigation_candidate_manifest_is_valid_but_not_active() -> None:
    manifest = _load_yaml(CANDIDATE_MANIFEST)
    schema = json.loads(
        (ROOT / "schemas" / "manifest.schema.json").read_text(encoding="utf-8")
    )
    errors = sorted(
        Draft202012Validator(schema).iter_errors(manifest),
        key=lambda error: list(error.absolute_path),
    )
    assert not errors, [error.message for error in errors]

    assert manifest["metadata"]["id"] == "irrigation"
    assert manifest["metadata"]["title"] == "Полив"
    assert manifest["spec"]["dashboard_path"] == CANDIDATE_DASHBOARD
    assert manifest["spec"]["subpanel"] == {
        "template": "standard_v1",
        "navigation": "main",
        "parent": "actions",
    }
    assert [view["title"] for view in manifest["spec"]["views"]] == [
        "Обзор",
        "Ручной",
        "Настройки",
        "Диагностика",
    ]
    assert all(view["renderer"] == "operational_v1" for view in manifest["spec"]["views"])
    assert all(view["modules"] for view in manifest["spec"]["views"])

    assert not (ROOT / "manifests" / "irrigation.yaml").exists()
    assert not (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "bundled_sources"
        / "manifests"
        / "irrigation.yaml"
    ).exists()


def test_irrigation_candidate_shell_has_actions_back_and_four_tabs() -> None:
    manifest = _load_yaml(CANDIDATE_MANIFEST)
    rendered, groups = apply_navigation_shell(
        _sections_dashboard(len(manifest["spec"]["views"])), manifest, ROOT
    )

    assert len(groups) == 1
    group = groups[0]
    assert group["id"] == "irrigation"
    assert group["title"] == "Полив"
    assert group["parent"]["id"] == "actions"
    assert group["parent"]["path"] == "/dashboard-actions/home"
    assert group["embedded"] is False
    assert [tab["path"] for tab in group["tabs"]] == [
        f"{CANDIDATE_DASHBOARD}/overview",
        f"{CANDIDATE_DASHBOARD}/manual",
        f"{CANDIDATE_DASHBOARD}/settings",
        f"{CANDIDATE_DASHBOARD}/diagnostics",
    ]

    for view, expected_path in zip(
        rendered["views"],
        ["overview", "manual", "settings", "diagnostics"],
        strict=True,
    ):
        assert view["path"] == expected_path
        assert view["subview"] is True
        assert view["back_path"] == "/dashboard-actions/home"
        assert view["title"] == "Полив"
        spacer = view["sections"][-1]["cards"][0]
        assert spacer["type"] == "markdown"
        assert spacer["text_only"] is True


def test_irrigation_candidate_route_is_declared_but_registry_stays_dormant() -> None:
    navigation = _load_yaml(ROOT / "navigation" / "main.yaml")
    candidate = navigation["spec"]["routes"]["actions.irrigation_candidate"]
    assert candidate == {
        "title": "Полив · candidate",
        "path": f"{CANDIDATE_DASHBOARD}/overview",
        "parent": "actions",
    }

    registry = compile_navigation_registry(ROOT)
    groups = {group["id"]: group for group in registry["subpanels"]}
    assert "irrigation" not in groups

    serialized = json.dumps(registry, ensure_ascii=False)
    assert "entity_id" not in serialized
    assert "device_id" not in serialized
    assert CANDIDATE_DASHBOARD not in serialized


def test_irrigation_contracts_are_read_only_and_fail_closed() -> None:
    for name in (
        "house_irrigation_controller.yaml",
        "house_irrigation_zone.yaml",
        "house_irrigation_lab.yaml",
    ):
        contract = _load_yaml(ROOT / "contracts" / name)
        safety = contract["spec"]["safety"]
        assert safety["unknown_is_unreliable"] is True
        assert safety["unavailable_is_unreliable"] is True
        assert safety["invent_entity_ids"] is False
        assert all(
            action["kind"] == "more_info" for action in contract["spec"]["actions"]
        )


def test_irrigation_public_runtime_sources_match_bundled_copies() -> None:
    for name in (
        "house_irrigation_controller.yaml",
        "house_irrigation_zone.yaml",
        "house_irrigation_lab.yaml",
    ):
        assert (ROOT / "contracts" / name).read_bytes() == (
            ROOT
            / "custom_components"
            / "contract_generated_ui"
            / "bundled_sources"
            / "contracts"
            / name
        ).read_bytes()

    assert (ROOT / "navigation" / "main.yaml").read_bytes() == (
        ROOT
        / "custom_components"
        / "contract_generated_ui"
        / "bundled_sources"
        / "navigation"
        / "main.yaml"
    ).read_bytes()
