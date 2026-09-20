"""Constants for the common Contract Generated UI integration."""

from datetime import timedelta

DOMAIN = "contract_generated_ui"
NAME = "NikaS Contract Generated UI"

FRONTEND_DIRECTORY = "frontend"
FRONTEND_STATIC_PATH = f"/{DOMAIN}/frontend"
FRONTEND_STATIC_REGISTERED = "frontend_static_registered"
DEVICE_AVAILABILITY_PANEL_FILENAME = "device-availability-panel.js"
DEVICE_AVAILABILITY_PANEL_BUILD = "b005"
DEVICE_AVAILABILITY_PANEL_MODULE_URL = (
    f"{FRONTEND_STATIC_PATH}/{DEVICE_AVAILABILITY_PANEL_FILENAME}"
    f"?build={DEVICE_AVAILABILITY_PANEL_BUILD}"
)
DEVICE_AVAILABILITY_PANEL_URL_PATH = "dashboard-device-availability"
DEVICE_AVAILABILITY_PANEL_PATH = "device_availability_panel_path"

SOURCE_DIRECTORY = "contract_generated_ui"
SOURCE_KINDS = ("contracts", "inventory", "manifests", "navigation")
SOURCE_STATUSES = ("missing", "empty", "incomplete", "valid", "invalid")
SNAPSHOT_DIRECTORY = "snapshots"
GENERATED_DIRECTORY = "generated"

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
