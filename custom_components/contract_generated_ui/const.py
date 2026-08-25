"""Constants for Contract Generated UI."""

from datetime import timedelta

DOMAIN = "contract_generated_ui"
NAME = "Contract Generated UI"

SOURCE_DIRECTORY = "contract_generated_ui"
SOURCE_KINDS = ("contracts", "inventory", "manifests", "navigation")
SOURCE_STATUSES = ("missing", "empty", "incomplete", "valid", "invalid")
SNAPSHOT_DIRECTORY = "snapshots"
GENERATED_DIRECTORY = "generated"
FRONTEND_DIRECTORY = "frontend"
APP_SHELL_FILENAME = "nikas-app-shell.js"
APP_SHELL_STATIC_PATH = f"/{DOMAIN}/frontend/{APP_SHELL_FILENAME}"
INFRA_SUMMARY_FILENAME = "nikas-infrastructure-summary.js"
INFRA_SUMMARY_STATIC_PATH = f"/{DOMAIN}/frontend/{INFRA_SUMMARY_FILENAME}"
UI_BUNDLE_FILENAME = "nikas-ui.js"
UI_BUNDLE_STATIC_PATH = f"/{DOMAIN}/frontend/{UI_BUNDLE_FILENAME}"
UI_BUNDLE_BUILD = "b004"
UI_BUNDLE_MODULE_URL = f"{UI_BUNDLE_STATIC_PATH}?build={UI_BUNDLE_BUILD}"
HOUSE_HERO_FILENAME = "nikas-house-hero.js"
HOUSE_HERO_STATIC_PATH = f"/{DOMAIN}/frontend/{HOUSE_HERO_FILENAME}"
HOUSE_HERO_BUILD = "b004"
HOUSE_HERO_MODULE_URL = f"{HOUSE_HERO_STATIC_PATH}?build={HOUSE_HERO_BUILD}"
HOUSE_HERO_ASSETS_STATIC_PATH = f"/{DOMAIN}/frontend/assets"
HOUSE_HERO_ASSET_FILENAME = "house-hero-day-v1.svg"
HOUSE_HERO_ASSET_BUILD = "0310b001"
HOUSE_HERO_ASSET_URL = (
    f"{HOUSE_HERO_ASSETS_STATIC_PATH}/{HOUSE_HERO_ASSET_FILENAME}?build={HOUSE_HERO_ASSET_BUILD}"
)
GENERATED_SUBPANEL_FILENAME = "nikas-generated-subpanel.js"
GENERATED_SUBPANEL_STATIC_PATH = f"/{DOMAIN}/frontend/{GENERATED_SUBPANEL_FILENAME}"
GENERATED_SUBPANEL_BUILD = "b006"
GENERATED_SUBPANEL_MODULE_URL = (
    f"{GENERATED_SUBPANEL_STATIC_PATH}?build={GENERATED_SUBPANEL_BUILD}"
)
# Contract Generated UI owns only the generic ZONT renderer. The ZONT-specific
# application layer is HACS-managed by NikaSir/ha-zont (domain: zont_local).
GENERATED_ZONT_FILENAME = "nikas-generated-zont.js"
GENERATED_ZONT_STATIC_PATH = f"/{DOMAIN}/frontend/{GENERATED_ZONT_FILENAME}"
GENERATED_ZONT_BUILD = "b005"
GENERATED_ZONT_MODULE_URL = f"{GENERATED_ZONT_STATIC_PATH}?build={GENERATED_ZONT_BUILD}"
GENERATED_SUBPANEL_PATHS = "generated_subpanel_paths"
NAVIGATION_REGISTRY_FILENAME = "navigation.json"
NAVIGATION_REGISTRY_STATIC_PATH = f"/{DOMAIN}/{NAVIGATION_REGISTRY_FILENAME}"
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
