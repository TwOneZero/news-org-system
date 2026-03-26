# Proposal: Refactor Registry Hardcoded Strings

## Why

Currently, source names (e.g., "etnews_today", "yonhap_economy"), feed URLs, and adapter names are hardcoded as string literals throughout the codebase. This creates maintenance challenges when adding, modifying, or removing news sources:

- **No Single Source of Truth**: Source names and URLs are duplicated across multiple files (registry.py, rss_reader.py, tests, API models)
- **Fragile to Changes**: Removing or renaming a source like "etnews_today" requires finding and updating 20+ files across the codebase
- **Error-Prone**: Typos in hardcoded strings can cause runtime errors that only surface during execution
- **Hard to Maintain**: Developers must manually search for all usages when making changes

## What Changes

- **Centralize Constants**: Create a dedicated constants module for source names, adapter names, and related configuration strings
- **Update Registry**: Refactor `readers/registry.py` to use centralized constants instead of string literals
- **Update All References**: Replace hardcoded string usages across:
  - Service layer (`services/collection.py`, `services/stats.py`, `services/query.py`)
  - API layer (`api/models/`, `api/routes/`)
  - Test files (`tests/unit/test_registry.py`, `tests/integration/`, `tests/conftest.py`)
  - CLI (`news_api.py`)

- **Remove Duplication**: Clean up duplicate URL mappings in `rss_reader.py`

## Capabilities

### New Capabilities

None - this is a pure refactoring with no new functionality or behavior changes.

### Modified Capabilities

None - this refactoring does not change any requirements or external behavior. All APIs, CLI commands, and service interfaces remain identical. Only implementation details change (string literals → constants).

## Impact

- **Service Layer**: `services/collection.py`, `services/query.py`, `services/stats.py` will import and use constants
- **API Layer**: API models and routes will reference constants instead of hardcoded strings
- **Test Suite**: All test files using source names, URLs, or adapter names will be updated
- **Registry Module**: `readers/registry.py` will be refactored to define and export constants
- **Reader Module**: `readers/rss_reader.py` duplicate URL mappings will be removed
- **Backward Compatibility**: 100% - no API or CLI changes, all existing functionality preserved

**Files Affected** (estimated 20+ files):
- Core: `readers/registry.py`, `readers/rss_reader.py`, `readers/__init__.py`
- Services: `services/collection.py`, `services/query.py`, `services/stats.py`
- API: `api/models/collection.py`, `api/models/stats.py`, `api/routes/collection.py`
- Tests: `tests/unit/test_registry.py`, `tests/conftest.py`, `tests/integration/test_rss_to_mongo.py`, `tests/integration/test_rss_feeds.py`
- CLI: `news_api.py`
