"""Constants for the House-only Contract Generated UI integration."""

from datetime import timedelta

DOMAIN = "contract_generated_ui"
NAME = "Contract Generated UI"

SOURCE_DIRECTORY = "contract_generated_ui"
SOURCE_KINDS = ("contracts", "inventory", "manifests", "navigation")
SOURCE_STATUSES = ("missing", "empty", "incomplete", "valid", "invalid")
SNAPSHOT_DIRECTORY = "snapshots"
GENERATED_DIRECTORY = "generated"

FRONTEND_DIRECTORY = "frontend"
UI_BUNDLE_FILENAME = "nikas-ui.js"
UI_BUNDLE_STATIC_PATH = f"/{DOMAIN}/frontend/{UI_BUNDLE_FILENAME}"
UI_BUNDLE_BUILD = "b026"
UI_BUNDLE_MODULE_URL = f"{UI_BUNDLE_STATIC_PATH}?build={UI_BUNDLE_BUILD}"

HOUSE_HERO_FILENAME = "nikas-house-hero.js"
HOUSE_HERO_STATIC_PATH = f"/{DOMAIN}/frontend/{HOUSE_HERO_FILENAME}"
HOUSE_HERO_BUILD = "b014"
HOUSE_HERO_MODULE_URL = f"{HOUSE_HERO_STATIC_PATH}?build={HOUSE_HERO_BUILD}"
HOUSE_HERO_ASSETS_STATIC_PATH = f"/{DOMAIN}/frontend/assets"

HOUSE_PANEL_FILENAME = "dist/nikas-house-overview.js"
HOUSE_PANEL_STATIC_PATH = f"/{DOMAIN}/frontend/{HOUSE_PANEL_FILENAME}"
HOUSE_PANEL_BUILD = "b014"
HOUSE_PANEL_MODULE_URL = f"{HOUSE_PANEL_STATIC_PATH}?build={HOUSE_PANEL_BUILD}"
HOUSE_PANEL_PATH = "house_panel_path"
HOUSE_PANEL_PARALLEL_URL_PATH = "dashboard-house-v12"

FRONTEND_STATIC_REGISTERED = "frontend_static_registered"
SCAN_INTERVAL = timedelta(minutes=1)

ATTR_CONTRACTS = "contracts"
ATTR_INVENTORY = "inventory"
ATTR_MANIFESTS = "manifests"
ATTR_NAVIGATION = "navigation"
ATTR_DOCUMENT_COUNT = "document_count"
ATTR_ISSUE_COUNT = "issue_count"
ATTR_ISSUES = "issues"
ATTR_SOURCE_DIRECTORY = "source_directory"
ATTR_VALIDATION_LEVEL = "validation_level"
VALIDATION_LEVEL = "contract_core_v1"
MAX_ISSUES_IN_ATTRIBUTES = 10
