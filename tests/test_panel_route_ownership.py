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


def test_house_registration_preserves_an_existing_route() -> None:
    function = _function(PACKAGE / "house_panel.py", "async_register_house_panel")
    assert _calls(function, "async_panel_exists")
    assert not _calls(function, "async_remove_panel")

    guards = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.If)
        and any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr == "async_panel_exists"
            for child in ast.walk(node.test)
        )
    ]
    assert len(guards) == 1
    assert any(isinstance(node, ast.Return) for node in guards[0].body)


def test_unload_removes_only_the_recorded_house_fallback() -> None:
    house = (PACKAGE / "house_panel.py").read_text(encoding="utf-8")
    init = (PACKAGE / "__init__.py").read_text(encoding="utf-8")

    assert "hass.data.setdefault(DOMAIN, {})[HOUSE_PANEL_PATH] = url_path" in house
    assert "pop(HOUSE_PANEL_PATH, None)" in house
    assert "async_unregister_house_panel(hass)" in init
    assert "async_unregister_infrastructure_panel" not in init
    assert "async_unregister_generated_subpanels" not in init
    assert "async_unregister_rooms_panel" not in init


def test_non_house_panel_owners_are_not_shipped() -> None:
    for name in ("infrastructure_panel.py", "rooms_panel.py", "generated_panels.py"):
        assert not (PACKAGE / name).exists()
