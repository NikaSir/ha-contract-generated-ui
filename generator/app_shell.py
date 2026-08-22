from __future__ import annotations

import copy
from typing import Any, Mapping

APP_SHELL_ACTIVE = frozenset({"home", "actions", "infrastructure"})
APP_SHELL_ITEMS = (
    {
        "id": "home",
        "label": "Дом",
        "title": "Дом",
        "icon": "mdi:home-outline",
        "path": "/dashboard-house",
    },
    {
        "id": "actions",
        "label": "Действия",
        "title": "Действия",
        "icon": "mdi:lightning-bolt-outline",
        "path": "/dashboard-actions",
    },
    {
        "id": "infrastructure",
        "label": "Инфра",
        "title": "Инфраструктура",
        "icon": "mdi:server-network",
        "path": "/dashboard-infrastructure/overview",
    },
)


def manifest_app_shell_active(manifest: Mapping[str, Any]) -> str | None:
    app_shell = manifest.get("spec", {}).get("app_shell")
    if app_shell is None:
        return None
    if not isinstance(app_shell, Mapping):
        raise ValueError("spec.app_shell must be an object")
    active = app_shell.get("active")
    if active not in APP_SHELL_ACTIVE:
        raise ValueError(f"unsupported app shell active surface {active!r}")
    return active


def append_app_shell(
    dashboard: Mapping[str, Any],
    *,
    active: str,
) -> dict[str, Any]:
    if active not in APP_SHELL_ACTIVE:
        raise ValueError(f"unsupported app shell active surface {active!r}")

    transformed = copy.deepcopy(dashboard)
    views = transformed.get("views")
    if not isinstance(views, list) or not views:
        raise ValueError("NikaS app shell requires dashboard views")

    for view in views:
        if not isinstance(view, dict) or view.get("type") != "sections":
            raise ValueError("NikaS app shell requires Sections views")
        sections = view.get("sections")
        if not isinstance(sections, list):
            raise ValueError("NikaS app shell requires view sections")
        sections.append(
            {
                "type": "grid",
                "cards": [
                    {
                        "type": "custom:nikas-app-shell",
                        "active": active,
                        "items": [dict(item) for item in APP_SHELL_ITEMS],
                        "grid_options": {"columns": "full"},
                    }
                ],
            }
        )
    return transformed


__all__ = [
    "APP_SHELL_ACTIVE",
    "APP_SHELL_ITEMS",
    "append_app_shell",
    "manifest_app_shell_active",
]
