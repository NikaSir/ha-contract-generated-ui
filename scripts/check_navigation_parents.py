"""Check the approved native-overview hierarchy before publication."""
from pathlib import Path
import yaml


def validate(registry):
    routes = registry['spec']['routes']
    errors = []
    if routes.get('overview', {}).get('path') != '/home/overview':
        errors.append('native overview is missing')
    paths = {route['path'] for route in routes.values()}
    if len(paths) != len(routes):
        errors.append('duplicate route owner')
    for name, route in routes.items():
        if name == 'overview' and route.get('parent'):
            errors.append('native overview cannot have a parent')
        if name != 'overview' and route.get('parent') != 'overview':
            errors.append(f'{name}: main panel must have native overview parent')
        seen = set()
        current = name
        while current:
            if current in seen:
                errors.append(f'{name}: parent cycle')
                break
            seen.add(current)
            if current not in routes:
                errors.append(f'{name}: unknown parent {current}')
                break
            current = routes[current].get('parent')
    for name, route in registry['spec'].get('specialized_routes', {}).items():
        if route['path'] in paths:
            errors.append(f'{name}: duplicate route owner')
        paths.add(route['path'])
        if route.get('parent_route') != '/home/overview' or route.get('safe_return_route') != '/home/overview':
            errors.append(f'{name}: main panel parent must be native overview')
    return errors


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    errors = validate(yaml.safe_load((root / 'navigation/main.yaml').read_text()))
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Declared title hierarchy is valid.')
