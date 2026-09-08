"""Constants for the common Contract Generated UI integration."""

from datetime import timedelta

DOMAIN = "contract_generated_ui"
NAME = "NikaS Contract Generated UI"

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
