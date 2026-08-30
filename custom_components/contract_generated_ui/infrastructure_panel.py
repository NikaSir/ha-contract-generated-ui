"""Register the integration-owned Infrastructure overview panel."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

from .const import (
    DOMAIN,
    INFRASTRUCTURE_PANEL_MODULE_URL,
    INFRASTRUCTURE_PANEL_PATH,
)
from .runtime_infrastructure_summary import (
    SUMMARY_RENDERER,
    SUMMARY_VARIANTS,
    required_summary_roles,
)
from .runtime_renderer import (
    _index_contracts,
    _index_inventory,
    _load_object,
    _render_manifest,
)
from .runtime_subpanel_shell import compile_navigation_registry

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

INFRASTRUCTURE_PANEL_TEMPLATE = "infrastructure_overview_v1"
INFRASTRUCTURE_PANEL_WEB_COMPONENT = "nikas-infrastructure-overview"


def _infrastructure_manifest(source_root: Path) -> dict[str, Any]:
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
                and panel.get("template") == INFRASTRUCTURE_PANEL_TEMPLATE
            ):
                matches.append(manifest)
    if len(matches) != 1:
        raise ValueError(
            "exactly one specialized Infrastructure manifest is required; "
            f"found {len(matches)}"
        )
    return matches[0]


def _card_config(module: Mapping[str, Any]) -> dict[str, Any]:
    contract_id = module.get("contract")
    title = module.get("title")
    roles = module.get("roles")
    if not isinstance(contract_id, str) or contract_id not in SUMMARY_VARIANTS:
        raise ValueError("specialized Infrastructure module contract is unsupported")
    if not isinstance(title, str) or not title or not isinstance(roles, list):
        raise ValueError("specialized Infrastructure module title/roles missing")

    by_name = {
        role.get("role"): role
        for role in roles
        if isinstance(role, Mapping) and isinstance(role.get("role"), str)
    }
    required = required_summary_roles(contract_id, "overview")
    missing = [name for name in required if name not in by_name]
    if missing:
        raise ValueError(
            f"specialized Infrastructure module {contract_id!r} missing roles: "
            + ", ".join(missing)
        )

    role_config: dict[str, dict[str, str]] = {}
    external_targets: set[str] = set()
    for name in required:
        role = by_name[name]
        entity_id = role.get("entity_id")
        label = role.get("label")
        if not isinstance(entity_id, str) or not isinstance(label, str):
            raise ValueError(f"specialized Infrastructure role {name!r} is incomplete")
        role_config[name] = {"entity": entity_id, "label": label}
        action = role.get("action")
        if isinstance(action, Mapping) and action.get("kind") == "navigate":
            target = action.get("target")
            if isinstance(target, str) and target.startswith("/") and not target.startswith(
                "/dashboard-infrastructure/"
            ):
                external_targets.add(target)
    if len(external_targets) > 1:
        raise ValueError("specialized Infrastructure module has conflicting details routes")

    result: dict[str, Any] = {
        "variant": SUMMARY_VARIANTS[contract_id],
        "title": title,
        "roles": role_config,
    }
    if external_targets:
        result["details_path"] = next(iter(external_targets))
    return result


def build_infrastructure_panel_spec(source_root: Path) -> dict[str, Any]:
    """Resolve Infrastructure overview cards from verified semantic inventory."""
    manifest = _infrastructure_manifest(source_root)
    metadata = manifest.get("metadata", {})
    spec = manifest.get("spec", {})
    dashboard_path = spec.get("dashboard_path")
    if not isinstance(dashboard_path, str) or not dashboard_path.startswith("/"):
        raise ValueError("specialized Infrastructure dashboard_path is invalid")
    url_path = dashboard_path.removeprefix("/")
    if not url_path or "/" in url_path:
        raise ValueError("specialized Infrastructure requires one top-level URL path")

    views = spec.get("views")
    overview = next(
        (view for view in views or [] if isinstance(view, dict) and view.get("id") == "overview"),
        None,
    )
    if not isinstance(overview, dict) or overview.get("renderer") != SUMMARY_RENDERER:
        raise ValueError("specialized Infrastructure overview renderer is invalid")

    contracts = _index_contracts(source_root)
    inventory, snapshot_ids = _index_inventory(source_root)
    _, trace = _render_manifest(
        manifest,
        contracts,
        inventory,
        snapshot_ids=snapshot_ids,
    )
    semantic_views = trace.get("semantics", {}).get("views")
    semantic_overview = next(
        (view for view in semantic_views or [] if isinstance(view, dict) and view.get("id") == "overview"),
        None,
    )
    modules = semantic_overview.get("modules") if isinstance(semantic_overview, dict) else None
    if not isinstance(modules, list) or len(modules) != 4:
        raise ValueError("specialized Infrastructure overview requires four verified modules")

    navigation = compile_navigation_registry(source_root)
    tabs = navigation.get("global_tabs")
    if not isinstance(tabs, list) or not 3 <= len(tabs) <= 5:
        raise ValueError("specialized Infrastructure requires 3–5 global tabs")

    title = overview.get("title")
    view_path = overview.get("path")
    if not isinstance(title, str) or not title or not isinstance(view_path, str) or not view_path:
        raise ValueError("specialized Infrastructure overview metadata is incomplete")

    return {
        "id": metadata.get("id", "infrastructure"),
        "title": title,
        "sidebar_title": metadata.get("title", "Инфраструктура"),
        "sidebar_icon": "mdi:server-network",
        "url_path": url_path,
        "default_path": f"{dashboard_path}/{view_path}",
        "cards": [_card_config(module) for module in modules],
        "tabs": tabs,
    }


async def async_register_infrastructure_panel(hass: HomeAssistant, source_root: Path) -> None:
    """Register the Infrastructure fallback only when its route is unowned."""
    from homeassistant.components import frontend, panel_custom

    panel_spec = await hass.async_add_executor_job(build_infrastructure_panel_spec, source_root)
    url_path = panel_spec["url_path"]
    if frontend.async_panel_exists(hass, url_path):
        return

    await panel_custom.async_register_panel(
        hass=hass,
        frontend_url_path=url_path,
        webcomponent_name=INFRASTRUCTURE_PANEL_WEB_COMPONENT,
        sidebar_title=panel_spec["sidebar_title"],
        sidebar_icon=panel_spec["sidebar_icon"],
        module_url=INFRASTRUCTURE_PANEL_MODULE_URL,
        embed_iframe=False,
        require_admin=False,
        handle_safe_area=True,
        config={
            "id": panel_spec["id"],
            "title": panel_spec["title"],
            "default_path": panel_spec["default_path"],
            "cards": panel_spec["cards"],
            "tabs": panel_spec["tabs"],
        },
    )
    hass.data.setdefault(DOMAIN, {})[INFRASTRUCTURE_PANEL_PATH] = url_path


def async_unregister_infrastructure_panel(hass: HomeAssistant) -> None:
    """Remove only the Infrastructure fallback registered by this integration."""
    from homeassistant.components import frontend

    url_path = hass.data.get(DOMAIN, {}).pop(INFRASTRUCTURE_PANEL_PATH, None)
    if isinstance(url_path, str):
        frontend.async_remove_panel(hass, url_path, warn_if_unknown=False)


__all__ = [
    "INFRASTRUCTURE_PANEL_TEMPLATE",
    "INFRASTRUCTURE_PANEL_WEB_COMPONENT",
    "async_register_infrastructure_panel",
    "async_unregister_infrastructure_panel",
    "build_infrastructure_panel_spec",
]
