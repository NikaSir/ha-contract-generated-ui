"""Register shared Contract Generated UI application panels."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from .const import (
    DOMAIN,
    GENERATED_SUBPANEL_MODULE_URL,
    GENERATED_SUBPANEL_PATHS,
    GENERATED_ZONT_MODULE_URL,
)
from .runtime_subpanel_shell import resolved_navigation_groups

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

SUPPORTED_SUFFIXES = {".json", ".yaml", ".yml"}
WEB_COMPONENT_NAME = "nikas-generated-subpanel"
ZONT_WEB_COMPONENT_NAME = "nikas-generated-zont"


def _load_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle) if path.suffix.lower() == ".json" else yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise ValueError(f"document root must be an object: {path}")
    return document


def _manifests(source_root: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    root = source_root / "manifests"
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        document = _load_object(path)
        if document.get("kind") == "PanelManifest":
            result.append(document)
    return result


def build_generated_panel_specs(source_root: Path) -> list[dict[str, Any]]:
    """Build data-only custom-panel registrations from subpanel manifests."""
    result: list[dict[str, Any]] = []

    for manifest in _manifests(source_root):
        spec = manifest.get("spec", {})
        subpanel = spec.get("subpanel")
        if subpanel is None:
            continue
        groups = resolved_navigation_groups(manifest, source_root)
        if len(groups) != 1:
            raise ValueError(
                f"generated subpanel {manifest.get('metadata', {}).get('id')!r} "
                "must resolve to exactly one navigation group"
            )
        group = groups[0]
        if group.get("embedded"):
            continue

        panel_id = group["id"]
        dashboard_path = group["dashboard_path"]
        url_path = dashboard_path.removeprefix("/")
        if not url_path or "/" in url_path:
            raise ValueError(
                f"generated custom panel requires one top-level url path: {dashboard_path!r}"
            )

        manifest_views = spec.get("views")
        if not isinstance(manifest_views, list):
            raise ValueError(f"generated subpanel {panel_id!r} views missing")
        view_map = {
            view.get("id"): view
            for view in manifest_views
            if isinstance(view, dict) and isinstance(view.get("id"), str)
        }

        tabs: list[dict[str, Any]] = []
        for tab in group["tabs"]:
            view = view_map.get(tab["id"], {})
            tabs.append(
                {
                    "id": tab["id"],
                    "label": tab.get("title", tab["id"]),
                    "icon": tab.get("icon", "mdi:view-dashboard-outline"),
                    "placeholder": view.get("placeholder", "Раздел готов к наполнению."),
                    "readonly": view.get("readonly"),
                }
            )
        if not 2 <= len(tabs) <= 5:
            raise ValueError(f"generated subpanel {panel_id!r} requires 2–5 tabs")

        result.append(
            {
                "id": panel_id,
                "title": group["title"],
                "subtitle": group.get("subtitle", group["parent"].get("title", "")),
                "url_path": url_path,
                "parent": group["parent"],
                "source": subpanel.get("source"),
                "tabs": tabs,
                "sidebar_icon": tabs[0]["icon"],
                "webcomponent_name": ZONT_WEB_COMPONENT_NAME if panel_id == "zont" else WEB_COMPONENT_NAME,
                "module_url": GENERATED_ZONT_MODULE_URL if panel_id == "zont" else GENERATED_SUBPANEL_MODULE_URL,
            }
        )

    return result


def strip_standalone_navigation_groups(registry_path: Path) -> bool:
    """Keep the global overlay registry for Lovelace-embedded groups only."""
    if not registry_path.exists():
        return False
    document = json.loads(registry_path.read_text(encoding="utf-8"))
    groups = document.get("subpanels")
    if not isinstance(groups, list):
        raise ValueError("navigation registry subpanels must be an array")
    filtered = [group for group in groups if isinstance(group, dict) and group.get("embedded")]
    if filtered == groups:
        return False
    document["subpanels"] = filtered
    text = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    temp = registry_path.with_name(f".{registry_path.name}.tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, registry_path)
    return True


async def async_register_generated_subpanels(
    hass: HomeAssistant,
    source_root: Path,
) -> None:
    """Register standalone generated subpanels with manifest-selected web components."""
    from homeassistant.components import frontend, panel_custom

    specs = await hass.async_add_executor_job(build_generated_panel_specs, source_root)
    domain_data = hass.data.setdefault(DOMAIN, {})
    registered: list[str] = []

    for spec in specs:
        url_path = spec["url_path"]
        if frontend.async_panel_exists(hass, url_path):
            frontend.async_remove_panel(hass, url_path, warn_if_unknown=False)

        await panel_custom.async_register_panel(
            hass=hass,
            frontend_url_path=url_path,
            webcomponent_name=spec["webcomponent_name"],
            sidebar_title=spec["title"],
            sidebar_icon=spec["sidebar_icon"],
            module_url=spec["module_url"],
            embed_iframe=False,
            require_admin=False,
            handle_safe_area=True,
            config={
                "id": spec["id"],
                "title": spec["title"],
                "subtitle": spec["subtitle"],
                "parent": spec["parent"],
                "source": spec["source"],
                "tabs": spec["tabs"],
            },
        )
        registered.append(url_path)

    domain_data[GENERATED_SUBPANEL_PATHS] = registered


def async_unregister_generated_subpanels(hass: HomeAssistant) -> None:
    """Remove generated subpanels when Contract Generated UI unloads."""
    from homeassistant.components import frontend

    paths = hass.data.get(DOMAIN, {}).pop(GENERATED_SUBPANEL_PATHS, [])
    for url_path in paths:
        frontend.async_remove_panel(hass, url_path, warn_if_unknown=False)


__all__ = [
    "WEB_COMPONENT_NAME",
    "ZONT_WEB_COMPONENT_NAME",
    "async_register_generated_subpanels",
    "async_unregister_generated_subpanels",
    "build_generated_panel_specs",
    "strip_standalone_navigation_groups",
]
