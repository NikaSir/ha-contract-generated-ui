import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "custom_components" / "contract_generated_ui"


def _function(path: Path, name: str) -> ast.AsyncFunctionDef:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return node
    raise AssertionError(f"missing async function {name} in {path}")


def _calls(function: ast.AsyncFunctionDef, attribute: str) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == attribute
    ]


def _existing_route_guard(
    function: ast.AsyncFunctionDef,
) -> ast.If:
    for node in ast.walk(function):
        if not isinstance(node, ast.If):
            continue
        if any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr == "async_panel_exists"
            for child in ast.walk(node.test)
        ):
            return node
    raise AssertionError("missing existing-route guard")


def test_central_panel_registration_never_removes_an_existing_route() -> None:
    targets = (
        (PACKAGE / "house_panel.py", "async_register_house_panel"),
        (
            PACKAGE / "infrastructure_panel.py",
            "async_register_infrastructure_panel",
        ),
        (
            PACKAGE / "generated_panels.py",
            "async_register_generated_subpanels",
        ),
    )

    for path, name in targets:
        function = _function(path, name)
        assert _calls(function, "async_panel_exists")
        assert not _calls(function, "async_remove_panel")
        guard = _existing_route_guard(function)
        if name == "async_register_generated_subpanels":
            assert any(isinstance(node, ast.Continue) for node in guard.body)
        else:
            assert any(isinstance(node, ast.Return) for node in guard.body)


def test_unload_still_removes_only_paths_recorded_as_cgui_owned() -> None:
    house = (PACKAGE / "house_panel.py").read_text(encoding="utf-8")
    infrastructure = (PACKAGE / "infrastructure_panel.py").read_text(
        encoding="utf-8"
    )
    generated = (PACKAGE / "generated_panels.py").read_text(encoding="utf-8")

    assert "hass.data.setdefault(DOMAIN, {})[HOUSE_PANEL_PATH] = url_path" in house
    assert "pop(HOUSE_PANEL_PATH, None)" in house
    assert (
        "hass.data.setdefault(DOMAIN, {})[INFRASTRUCTURE_PANEL_PATH] = url_path"
        in infrastructure
    )
    assert "pop(INFRASTRUCTURE_PANEL_PATH, None)" in infrastructure
    assert "domain_data[GENERATED_SUBPANEL_PATHS] = registered" in generated
    assert "pop(GENERATED_SUBPANEL_PATHS, [])" in generated
