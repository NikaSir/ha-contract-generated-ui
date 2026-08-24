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
GENERATED_SUBPANEL_FILENAME = "nikas-generated-subpanel.js"
GENERATED_SUBPANEL_STATIC_PATH = f"/{DOMAIN}/frontend/{GENERATED_SUBPANEL_FILENAME}"
GENERATED_SUBPANEL_BUILD = "b006"
GENERATED_SUBPANEL_MODULE_URL = (
    f"{GENERATED_SUBPANEL_STATIC_PATH}?build={GENERATED_SUBPANEL_BUILD}"
)
GENERATED_ZONT_FILENAME = "nikas-generated-zont-v080.js"
GENERATED_ZONT_STATIC_PATH = f"/{DOMAIN}/frontend/{GENERATED_ZONT_FILENAME}"
GENERATED_ZONT_BUILD = "b001"
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
