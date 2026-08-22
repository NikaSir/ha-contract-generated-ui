from __future__ import annotations

import copy
import hashlib
from pathlib import Path
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


def app_shell_engine_sha256(base_engine_sha256: str) -> str:
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(
        f"{base_engine_sha256}:{layer_sha}".encode("utf-8")
    ).hexdigest()


def manifest_app_shell_config(
    manifest: Mapping[str, Any],
) -> tuple[str, dict[str, str]] | None:
    app_shell = manifest.get("spec", {}).get("app_shell")
    if app_shell is None:
        return None
    if not isinstance(app_shell, Mapping):
        raise ValueError("spec.app_shell must be an object")

    active = app_shell.get("active")
    if active not in APP_SHELL_ACTIVE:
        raise ValueError(f"unsupported app shell active surface {active!r}")

    raw_routes = app_shell.get("routes", {})
    if not isinstance(raw_routes, Mapping):
        raise ValueError("spec.app_shell.routes must be an object")

    routes: dict[str, str] = {}
    for surface, path in raw_routes.items():
        if surface not in APP_SHELL_ACTIVE:
            raise ValueError(f"unsupported app shell route surface {surface!r}")
        if not isinstance(path, str) or not path.startswith("/"):
            raise ValueError(
                f"app shell route {surface!r} must be an absolute Home Assistant path"
            )
        routes[surface] = path

    return active, routes


def manifest_app_shell_active(manifest: Mapping[str, Any]) -> str | None:
    config = manifest_app_shell_config(manifest)
    return config[0] if config is not None else None


def _navigation_items(routes: Mapping[str, str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for base_item in APP_SHELL_ITEMS:
        item = dict(base_item)
        override = routes.get(item["id"])
        if override is not None:
            item["path"] = override
        items.append(item)
    return items


def append_app_shell(
    dashboard: Mapping[str, Any],
    *,
    active: str,
    routes: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if active not in APP_SHELL_ACTIVE:
        raise ValueError(f"unsupported app shell active surface {active!r}")

    normalized_routes = dict(routes or {})
    for surface, path in normalized_routes.items():
        if surface not in APP_SHELL_ACTIVE:
            raise ValueError(f"unsupported app shell route surface {surface!r}")
        if not isinstance(path, str) or not path.startswith("/"):
            raise ValueError(
                f"app shell route {surface!r} must be an absolute Home Assistant path"
            )

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
                        "type": "markdown",
                        "content": "<br><br><br>",
                        "text_only": True,
                        "grid_options": {"columns": "full"},
                    }
                ],
            }
        )
    return transformed


__all__ = [
    "APP_SHELL_ACTIVE",
    "APP_SHELL_ITEMS",
    "app_shell_engine_sha256",
    "append_app_shell",
    "manifest_app_shell_active",
    "manifest_app_shell_config",
]
