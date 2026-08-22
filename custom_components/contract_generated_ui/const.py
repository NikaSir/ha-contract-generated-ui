"""Constants for Contract Generated UI."""

from datetime import timedelta

DOMAIN = "contract_generated_ui"
NAME = "Contract Generated UI"

SOURCE_DIRECTORY = "contract_generated_ui"
SOURCE_KINDS = ("contracts", "inventory", "manifests")
SOURCE_STATUSES = ("missing", "empty", "incomplete", "valid", "invalid")
SNAPSHOT_DIRECTORY = "snapshots"
GENERATED_DIRECTORY = "generated"
FRONTEND_DIRECTORY = "frontend"
APP_SHELL_FILENAME = "nikas-app-shell.js"
APP_SHELL_STATIC_PATH = f"/{DOMAIN}/frontend/{APP_SHELL_FILENAME}"
APP_SHELL_MODULE_VERSION = "0.14.0"
APP_SHELL_MODULE_URL = f"{APP_SHELL_STATIC_PATH}?v={APP_SHELL_MODULE_VERSION}"
INFRA_SUMMARY_FILENAME = "nikas-infrastructure-summary.js"
INFRA_SUMMARY_STATIC_PATH = f"/{DOMAIN}/frontend/{INFRA_SUMMARY_FILENAME}"
INFRA_SUMMARY_MODULE_VERSION = "0.15.0"
INFRA_SUMMARY_MODULE_URL = (
    f"{INFRA_SUMMARY_STATIC_PATH}?v={INFRA_SUMMARY_MODULE_VERSION}"
)
FRONTEND_STATIC_REGISTERED = "frontend_static_registered"

SCAN_INTERVAL = timedelta(minutes=1)

ATTR_CONTRACTS = "contracts"
ATTR_INVENTORY = "inventory"
ATTR_MANIFESTS = "manifests"
ATTR_DOCUMENT_COUNT = "document_count"
ATTR_ISSUE_COUNT = "issue_count"
ATTR_ISSUES = "issues"
ATTR_SOURCE_DIRECTORY = "source_directory"
ATTR_VALIDATION_LEVEL = "validation_level"

VALIDATION_LEVEL = "contract_core_v1"
MAX_ISSUES_IN_ATTRIBUTES = 10
