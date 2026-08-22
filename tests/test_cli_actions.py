from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_cli_render_uses_actions_dispatcher(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    for directory in ("contracts", "inventory", "manifests", "out"):
        (repo / directory).mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "schemas", repo / "schemas")

    contract = {
        "api_version": "nikas.home-assistant/ui-contract/v1",
        "kind": "UIContract",
        "metadata": {"id": "actions.cli", "title": "Actions", "version": "1.0"},
        "spec": {
            "roles": {
                "vacuum": {
                    "label": "Пылесос",
                    "description": "Open vacuum dashboard.",
                    "required": True,
                    "allowed_domains": ["vacuum"],
                }
            },
            "states": {
                "normal": {"description": "Normal", "rules": []},
                "event": {"description": "Event", "rules": []},
                "unreliable": {"description": "Unreliable", "rules": []},
            },
            "actions": [
                {
                    "id": "open_vacuum",
                    "kind": "navigate",
                    "description": "Open vacuum dashboard.",
                    "role": "vacuum",
                    "target": "/dashboard-s8-omni",
                }
            ],
            "presentation": {
                "renderer": "tiles_v1",
                "columns": 1,
                "role_order": ["vacuum"],
            },
            "safety": {
                "unknown_is_unreliable": True,
                "unavailable_is_unreliable": True,
                "invent_entity_ids": False,
            },
        },
    }
    inventory = {
        "api_version": "nikas.home-assistant/semantic-inventory/v1",
        "kind": "SemanticInventory",
        "metadata": {
            "generated_at": "2026-08-22T07:00:00Z",
            "source": "home_assistant",
            "scrubbed": True,
            "snapshot_id": "sha256:cli-actions-test",
        },
        "spec": {
            "bindings": {
                "actions.cli.vacuum": {
                    "entity_id": "vacuum.robot",
                    "domain": "vacuum",
                    "verification": "verified",
                }
            }
        },
    }
    manifest = {
        "api_version": "nikas.home-assistant/panel-manifest/v1",
        "kind": "PanelManifest",
        "metadata": {"id": "actions_cli", "title": "Actions", "version": "1.0"},
        "spec": {
            "dashboard_path": "/dashboard-actions-cli",
            "views": [
                {
                    "id": "home",
                    "title": "Actions",
                    "path": "home",
                    "order": 0,
                    "renderer": "actions_home_v1",
                    "modules": [
                        {
                            "contract": "actions.cli",
                            "instance": "quick",
                            "title": "Быстрые действия",
                            "order": 0,
                            "bindings": {"vacuum": "actions.cli.vacuum"},
                        }
                    ],
                }
            ],
        },
    }

    (repo / "contracts" / "actions.yaml").write_text(
        yaml.safe_dump(contract, sort_keys=False), encoding="utf-8"
    )
    (repo / "inventory" / "home.yaml").write_text(
        yaml.safe_dump(inventory, sort_keys=False), encoding="utf-8"
    )
    manifest_path = repo / "manifests" / "actions.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    output = repo / "out" / "actions.yaml"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "generator",
            "render",
            str(manifest_path),
            str(output),
            "--repo-root",
            str(repo),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    dashboard = yaml.safe_load(output.read_text(encoding="utf-8"))
    card = dashboard["views"][0]["sections"][0]["cards"][1]
    assert card["grid_options"] == {"columns": 12, "rows": 1}
    assert card["tap_action"] == {
        "action": "navigate",
        "navigation_path": "/dashboard-s8-omni",
    }
