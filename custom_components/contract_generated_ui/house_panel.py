"""Register the integration-owned House overview specialized panel."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .const import DOMAIN, HOUSE_PANEL_MODULE_URL, HOUSE_PANEL_PATH
from .runtime_house import HOUSE_RENDERER, house_overview_config
from .runtime_renderer import (
    _index_contracts,
    _index_inventory,
    _load_object,
    _render_manifest,
)
from .runtime_subpanel_shell import compile_navigation_registry

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

HOUSE_PANEL_TEMPLATE = "house_overview_v1"
HOUSE_PANEL_WEB_COMPONENT = "nikas-house-overview"


def _house_manifest(source_root: Path) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    manifests_root = source_root / "manifests"
    if manifests_root.exists():
        for path in sorted(manifests_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".json", ".yaml", ".yml"}:
                continue
            manifest = _load_object(path)
            panel = manifest.get("spec", {}).get("specialized_panel")
            if (
                manifest.get("kind") == "PanelManifest"
                and isinstance(panel, dict)
                and panel.get("template") == HOUSE_PANEL_TEMPLATE
            ):
                matches.append(manifest)
    if len(matches) != 1:
        raise ValueError(
            "exactly one specialized House manifest is required; "
            f"found {len(matches)}"
        )
    return matches[0]


def build_house_panel_spec(source_root: Path) -> dict[str, Any]:
    """Resolve the House panel config from verified private semantic inventory."""
    manifest = _house_manifest(source_root)
    metadata = manifest.get("metadata", {})
    spec = manifest.get("spec", {})
    views = spec.get("views")
    if not isinstance(views, list) or len(views) != 1 or not isinstance(views[0], dict):
        raise ValueError("specialized House panel requires exactly one view")
    view = views[0]
    if view.get("renderer") != HOUSE_RENDERER:
        raise ValueError("specialized House panel requires house_home_v1")

    dashboard_path = spec.get("dashboard_path")
    if not isinstance(dashboard_path, str) or not dashboard_path.startswith("/"):
        raise ValueError("specialized House panel dashboard_path is invalid")
    url_path = dashboard_path.removeprefix("/")
    if not url_path or "/" in url_path:
        raise ValueError("specialized House panel requires one top-level URL path")

    contracts = _index_contracts(source_root)
    inventory, snapshot_ids = _index_inventory(source_root)
    _, trace = _render_manifest(
        manifest,
        contracts,
        inventory,
        snapshot_ids=snapshot_ids,
    )
    navigation = compile_navigation_registry(source_root)
    tabs = navigation.get("global_tabs")
    if not isinstance(tabs, list) or not 3 <= len(tabs) <= 5:
        raise ValueError("specialized House panel requires 3–5 global tabs")

    hero = house_overview_config(trace, manifest)
    title = view.get("title")
    if not isinstance(title, str) or not title:
        raise ValueError("specialized House panel title is missing")
    view_path = view.get("path")
    if not isinstance(view_path, str) or not view_path:
        raise ValueError("specialized House panel view path is missing")

    return {
        "id": metadata.get("id", "house_v11_preview"),
        "title": title,
        "sidebar_title": metadata.get("title", "Дом"),
        "sidebar_icon": "mdi:home-outline",
        "url_path": url_path,
        "default_path": f"{dashboard_path}/{view_path}",
        "hero": hero,
        "tabs": tabs,
    }


async def async_register_house_panel(hass: HomeAssistant, source_root: Path) -> None:
    """Register the House fallback only when the canonical route is unowned."""
    from homeassistant.components import frontend, panel_custom

    panel_spec = await hass.async_add_executor_job(build_house_panel_spec, source_root)
    url_path = panel_spec["url_path"]
    if frontend.async_panel_exists(hass, url_path):
        return

    await panel_custom.async_register_panel(
        hass=hass,
        frontend_url_path=url_path,
        webcomponent_name=HOUSE_PANEL_WEB_COMPONENT,
        sidebar_title=panel_spec["sidebar_title"],
        sidebar_icon=panel_spec["sidebar_icon"],
        module_url=HOUSE_PANEL_MODULE_URL,
        embed_iframe=False,
        require_admin=False,
        handle_safe_area=True,
        config={
            "id": panel_spec["id"],
            "title": panel_spec["title"],
            "default_path": panel_spec["default_path"],
            "hero": panel_spec["hero"],
            "tabs": panel_spec["tabs"],
        },
    )
    hass.data.setdefault(DOMAIN, {})[HOUSE_PANEL_PATH] = url_path


def async_unregister_house_panel(hass: HomeAssistant) -> None:
    """Remove only the House fallback registered by this integration."""
    from homeassistant.components import frontend

    url_path = hass.data.get(DOMAIN, {}).pop(HOUSE_PANEL_PATH, None)
    if isinstance(url_path, str):
        frontend.async_remove_panel(hass, url_path, warn_if_unknown=False)


__all__ = [
    "HOUSE_PANEL_TEMPLATE",
    "HOUSE_PANEL_WEB_COMPONENT",
    "async_register_house_panel",
    "async_unregister_house_panel",
    "build_house_panel_spec",
]
