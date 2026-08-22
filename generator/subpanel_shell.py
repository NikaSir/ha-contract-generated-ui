from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

from .render import RenderError

NAVIGATION_API_VERSION = "nikas.home-assistant/navigation/v1"
NAVIGATION_KIND = "NavigationContract"
NAVIGATION_REGISTRY_API_VERSION = "nikas.home-assistant/navigation-registry/v1"
NAVIGATION_REGISTRY_FILENAME = "navigation.json"
SUBPANEL_TEMPLATE = "standard_v1"


def _documents(base: Path) -> Iterable[Path]:
    if not base.exists():
        return ()
    return (
        path
        for path in sorted(base.rglob("*"))
        if path.is_file() and path.suffix.lower() in {".json", ".yaml", ".yml"}
    )


def _load_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle) if path.suffix.lower() == ".json" else yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise RenderError(f"document root must be an object: {path}")
    return document


def _load_navigation_contracts(source_root: Path) -> dict[str, dict[str, Any]]:
    contracts: dict[str, dict[str, Any]] = {}
    for path in _documents(source_root / "navigation"):
        document = _load_object(path)
        if document.get("api_version") != NAVIGATION_API_VERSION or document.get("kind") != NAVIGATION_KIND:
            raise RenderError(f"unexpected navigation document in {path}")
        nav_id = document.get("metadata", {}).get("id")
        if not isinstance(nav_id, str) or not nav_id:
            raise RenderError(f"navigation contract id missing in {path}")
        if nav_id in contracts:
            raise RenderError(f"duplicate navigation contract id {nav_id!r}")
        _validate_navigation_contract(document)
        contracts[nav_id] = document
    if not contracts:
        raise RenderError("no navigation contracts found")
    return contracts


def _validate_navigation_contract(document: Mapping[str, Any]) -> None:
    nav_id = document["metadata"]["id"]
    spec = document["spec"]
    routes = spec["routes"]

    for route_id, route in routes.items():
        parent = route.get("parent")
        if parent is not None and parent not in routes:
            raise RenderError(
                f"navigation {nav_id!r} route {route_id!r} references unknown parent {parent!r}"
            )

    global_ids: set[str] = set()
    for tab in spec["global_tabs"]:
        tab_id = tab["id"]
        if tab_id in global_ids:
            raise RenderError(f"navigation {nav_id!r} has duplicate global tab {tab_id!r}")
        global_ids.add(tab_id)
        if tab["route"] not in routes:
            raise RenderError(
                f"navigation {nav_id!r} global tab {tab_id!r} references unknown route {tab['route']!r}"
            )

    group_ids: set[str] = set()
    for group in spec.get("tab_groups", []):
        group_id = group["id"]
        if group_id in group_ids:
            raise RenderError(f"navigation {nav_id!r} has duplicate tab group {group_id!r}")
        group_ids.add(group_id)
        if group["parent"] not in routes:
            raise RenderError(
                f"navigation {nav_id!r} tab group {group_id!r} references unknown parent {group['parent']!r}"
            )
        view_ids = [tab["view"] for tab in group["tabs"]]
        if len(view_ids) != len(set(view_ids)):
            raise RenderError(f"navigation {nav_id!r} tab group {group_id!r} has duplicate view ids")


def _view_specs(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    views = manifest.get("spec", {}).get("views")
    if not isinstance(views, list):
        raise RenderError("panel manifest views missing")
    indexed: dict[str, Mapping[str, Any]] = {}
    for view in views:
        view_id = view.get("id")
        if not isinstance(view_id, str) or not view_id:
            raise RenderError("panel manifest view id missing")
        indexed[view_id] = view
    return indexed


def _resolved_subpanel_group(
    manifest: Mapping[str, Any],
    navigation_contracts: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any] | None:
    subpanel = manifest.get("spec", {}).get("subpanel")
    if subpanel is None:
        return None
    if not isinstance(subpanel, Mapping):
        raise RenderError("spec.subpanel must be an object")
    if subpanel.get("template") != SUBPANEL_TEMPLATE:
        raise RenderError(f"unsupported subpanel template {subpanel.get('template')!r}")

    nav_id = subpanel.get("navigation")
    parent_id = subpanel.get("parent")
    if not isinstance(nav_id, str) or nav_id not in navigation_contracts:
        raise RenderError(f"subpanel navigation contract {nav_id!r} not found")
    navigation = navigation_contracts[nav_id]
    routes = navigation["spec"]["routes"]
    if not isinstance(parent_id, str) or parent_id not in routes:
        raise RenderError(f"subpanel parent route {parent_id!r} not found in navigation {nav_id!r}")

    metadata = manifest["metadata"]
    spec = manifest["spec"]
    dashboard_path = spec["dashboard_path"]
    tabs = []
    for view in sorted(spec["views"], key=lambda item: item["order"]):
        icon = view.get("icon")
        if not isinstance(icon, str) or not icon.startswith("mdi:"):
            raise RenderError(f"subpanel view {view['id']!r} requires an mdi icon")
        tabs.append(
            {
                "id": view["id"],
                "view": view["id"],
                "title": view["title"],
                "icon": icon,
                "path": f"{dashboard_path}/{view['path']}",
            }
        )
    if not 2 <= len(tabs) <= 5:
        raise RenderError("generated subpanel requires 2–5 tabs")

    parent = routes[parent_id]
    return {
        "id": metadata["id"],
        "title": metadata["title"],
        "dashboard_path": dashboard_path,
        "parent": {"id": parent_id, "title": parent["title"], "path": parent["path"]},
        "tabs": tabs,
        "navigation": nav_id,
        "embedded": False,
    }


def _resolved_embedded_groups(
    manifest: Mapping[str, Any],
    navigation_contracts: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    dashboard_path = manifest.get("spec", {}).get("dashboard_path")
    if not isinstance(dashboard_path, str):
        return []
    view_specs = _view_specs(manifest)
    groups: list[dict[str, Any]] = []

    for nav_id, navigation in sorted(navigation_contracts.items()):
        routes = navigation["spec"]["routes"]
        for group in navigation["spec"].get("tab_groups", []):
            if group["dashboard_path"] != dashboard_path:
                continue
            parent_id = group["parent"]
            parent = routes[parent_id]
            tabs = []
            for tab in group["tabs"]:
                view_id = tab["view"]
                view = view_specs.get(view_id)
                if view is None:
                    raise RenderError(
                        f"navigation tab group {group['id']!r} references missing manifest view {view_id!r}"
                    )
                tabs.append(
                    {
                        "id": view_id,
                        "view": view_id,
                        "title": tab["title"],
                        "icon": tab["icon"],
                        "path": f"{dashboard_path}/{view['path']}",
                    }
                )
            groups.append(
                {
                    "id": group["id"],
                    "title": group["title"],
                    "dashboard_path": dashboard_path,
                    "parent": {"id": parent_id, "title": parent["title"], "path": parent["path"]},
                    "tabs": tabs,
                    "navigation": nav_id,
                    "embedded": True,
                }
            )
    return groups


def resolved_navigation_groups(
    manifest: Mapping[str, Any],
    source_root: Path,
) -> list[dict[str, Any]]:
    navigation_root = source_root / "navigation"
    subpanel_declared = manifest.get("spec", {}).get("subpanel") is not None
    if not navigation_root.exists():
        if subpanel_declared:
            raise RenderError("generated subpanel requires a navigation contract directory")
        return []
    navigation_contracts = _load_navigation_contracts(source_root)
    direct = _resolved_subpanel_group(manifest, navigation_contracts)
    embedded = _resolved_embedded_groups(manifest, navigation_contracts)
    if direct is not None and embedded:
        raise RenderError("a manifest cannot be both a generated subpanel and host embedded tab groups")
    return [direct] if direct is not None else embedded


def _append_bottom_clearance(view: dict[str, Any]) -> None:
    spacer = {
        "type": "markdown",
        "content": "<br><br><br>",
        "text_only": True,
        "grid_options": {"columns": "full"},
    }
    if view.get("type") == "sections":
        sections = view.get("sections")
        if not isinstance(sections, list):
            raise RenderError("subpanel Sections view has no sections")
        sections.append({"type": "grid", "cards": [spacer]})
        return
    if view.get("type") == "masonry":
        cards = view.get("cards")
        if not isinstance(cards, list):
            raise RenderError("subpanel Masonry view has no cards")
        cards.append(spacer)
        return
    raise RenderError(f"unsupported subpanel view type {view.get('type')!r}")


def apply_navigation_shell(
    dashboard: Mapping[str, Any],
    manifest: Mapping[str, Any],
    source_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Apply native Home Assistant subview/back chrome from declarative navigation data."""
    groups = resolved_navigation_groups(manifest, source_root)
    if not groups:
        return copy.deepcopy(dashboard), []

    transformed = copy.deepcopy(dashboard)
    rendered_views = transformed.get("views")
    manifest_views = manifest.get("spec", {}).get("views")
    if not isinstance(rendered_views, list) or not isinstance(manifest_views, list):
        raise RenderError("navigation shell requires dashboard and manifest views")
    if len(rendered_views) != len(manifest_views):
        raise RenderError("navigation shell view count mismatch")

    rendered_by_id = {
        view_spec["id"]: rendered
        for rendered, view_spec in zip(rendered_views, manifest_views, strict=True)
    }
    claimed: set[str] = set()
    for group in groups:
        for tab in group["tabs"]:
            view_id = tab["view"]
            if view_id in claimed:
                raise RenderError(f"view {view_id!r} belongs to more than one navigation group")
            claimed.add(view_id)
            view = rendered_by_id.get(view_id)
            if view is None:
                raise RenderError(f"rendered view {view_id!r} not found for navigation shell")
            view["title"] = group["title"]
            view["subview"] = True
            view["back_path"] = group["parent"]["path"]
            _append_bottom_clearance(view)
    return transformed, groups


def navigation_shell_engine_sha256(
    base_engine_sha256: str,
    groups: list[dict[str, Any]],
) -> str:
    if not groups:
        return base_engine_sha256
    layer_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    canonical_groups = json.dumps(
        groups,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(
        f"{base_engine_sha256}:{layer_sha}:{canonical_groups}".encode("utf-8")
    ).hexdigest()


def compile_navigation_registry(source_root: Path) -> dict[str, Any]:
    navigation_contracts = _load_navigation_contracts(source_root)
    manifests = []
    for path in _documents(source_root / "manifests"):
        document = _load_object(path)
        if document.get("kind") == "PanelManifest":
            manifests.append(document)

    default_nav = navigation_contracts.get("main")
    if default_nav is None:
        default_nav = navigation_contracts[sorted(navigation_contracts)[0]]
    routes = default_nav["spec"]["routes"]
    global_tabs = [
        {
            "id": tab["id"],
            "label": tab["title"],
            "icon": tab["icon"],
            "path": routes[tab["route"]]["path"],
        }
        for tab in default_nav["spec"]["global_tabs"]
    ]

    groups: dict[str, dict[str, Any]] = {}
    for manifest in manifests:
        for group in resolved_navigation_groups(manifest, source_root):
            if group["id"] in groups:
                raise RenderError(f"duplicate resolved navigation group id {group['id']!r}")
            groups[group["id"]] = {
                "id": group["id"],
                "title": group["title"],
                "dashboard_path": group["dashboard_path"],
                "parent": group["parent"],
                "embedded": group["embedded"],
                "tabs": [
                    {
                        "id": tab["id"],
                        "label": tab["title"],
                        "icon": tab["icon"],
                        "path": tab["path"],
                    }
                    for tab in group["tabs"]
                ],
            }

    return {
        "api_version": NAVIGATION_REGISTRY_API_VERSION,
        "global_tabs": global_tabs,
        "subpanels": [groups[key] for key in sorted(groups)],
    }


def _atomic_write(path: Path, text: str) -> bool:
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    if previous == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)
    return True


def write_navigation_registry(source_root: Path, output_path: Path) -> bool:
    registry = compile_navigation_registry(source_root)
    text = json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    return _atomic_write(output_path, text)


def write_empty_navigation_registry(output_path: Path) -> bool:
    registry = {
        "api_version": NAVIGATION_REGISTRY_API_VERSION,
        "global_tabs": [],
        "subpanels": [],
    }
    text = json.dumps(registry, ensure_ascii=False, indent=2) + "\n"
    return _atomic_write(output_path, text)


__all__ = [
    "NAVIGATION_REGISTRY_FILENAME",
    "SUBPANEL_TEMPLATE",
    "apply_navigation_shell",
    "compile_navigation_registry",
    "navigation_shell_engine_sha256",
    "resolved_navigation_groups",
    "write_empty_navigation_registry",
    "write_navigation_registry",
]
