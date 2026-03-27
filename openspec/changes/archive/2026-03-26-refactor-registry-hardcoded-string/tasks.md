# Implementation Tasks

## 1. Core Layer - Constants and Registry

- [x] 1.1 Create `src/news_org_system/readers/constants.py` module
- [x] 1.2 Define `SourceName` enum with all source names as string enums
- [x] 1.3 Define `AdapterName` enum with all adapter names as string enums
- [x] 1.4 Add feed URLs as class-level constants in `SourceName` enum
- [x] 1.5 Add `get_url()` class method to `SourceName` for URL retrieval
- [x] 1.6 Update `src/news_org_system/readers/registry.py` to import constants
- [x] 1.7 Replace hardcoded strings in `FEED_REGISTRY` with enum values
- [x] 1.8 Replace hardcoded strings in `ADAPTER_REGISTRY` with enum values
- [x] 1.9 Update `readers/__init__.py` to export constants module
- [x] 1.10 Run registry unit tests: `pytest tests/unit/test_registry.py -v`
- [x] 1.11 Verify enum string conversion: `python -c "from news_org_system.readers.constants import SourceName; print(SourceName.YONHAP_ECONOMY == 'yonhap_economy')"`

## 2. Service Layer Migration

- [x] 2.1 Update `src/news_org_system/services/collection.py`:
  - [x] Import `SourceName` and `AdapterName` from constants
  - [x] Replace hardcoded "yonhap_economy", "maeil_management", "etnews_today" with `SourceName` enums
  - [x] Replace hardcoded "yonhap", "maeil", "etnews" with `AdapterName` enums
  - [x] Update error messages to convert enum values to strings
- [x] 2.2 Update `src/news_org_system/services/query.py`:
  - [x] Import constants module
  - [x] Replace hardcoded source names with `SourceName` enums
  - [x] Update query filters to use enum values
- [x] 2.3 Update `src/news_org_system/services/stats.py`:
  - [x] Import constants module
  - [x] Replace hardcoded source names with `SourceName` enums
- [x] 2.4 Run service layer tests: `pytest tests/unit/test_services.py -v`

## 3. API Layer Migration

- [x] 3.1 Update `src/news_org_system/api/models/collection.py`:
  - [x] Import constants module
  - [x] Update API models to work with enum values (ensure string serialization)
  - [x] Verify Pydantic models serialize enum values correctly
- [x] 3.2 Update `src/news_org_system/api/models/stats.py`:
  - [x] Import constants module
  - [x] Replace hardcoded source names with `SourceName` enums
- [x] 3.3 Update `src/news_org_system/api/routes/collection.py`:
  - [x] Import constants module
  - [x] Update route handlers to use enum values
  - [x] Verify dynamic source result processing works
- [x] 3.4 Run API tests: `pytest tests/integration/test_api.py -v`
- [x] 3.5 Verify OpenAPI schema generation: Start API server and check `http://localhost:8000/openapi.json`
- [x] 3.6 Test API endpoints manually with curl or Postman

## 4. Test Suite Migration

- [x] 4.1 Update `tests/conftest.py`:
  - [x] Import constants module
  - [x] Update test fixtures for each source (yonhap_economy, maeil_management, etnews_today)
  - [x] Replace hardcoded strings in fixture definitions
- [x] 4.2 Update `tests/unit/test_registry.py`:
  - [x] Import constants module
  - [x] Replace all hardcoded source names with `SourceName` enums
  - [x] Replace all hardcoded adapter names with `AdapterName` enums
  - [x] Update test assertions to use enum values
- [x] 4.3 Update `tests/integration/test_rss_to_mongo.py`:
  - [x] Import constants module
  - [x] Replace hardcoded source names in test cases
  - [x] Update test data and mock objects
- [x] 4.4 Update `tests/integration/test_rss_feeds.py`:
  - [x] Import constants module
  - [x] Replace hardcoded source names in all test functions
  - [x] Update feed URL references with enum constants
- [x] 4.5 Run full test suite: `pytest -v`
- [x] 4.6 Run unit tests only: `pytest -m unit -v`
- [x] 4.7 Run integration tests only: `pytest -m integration -v`

## 5. CLI and Cleanup

- [x] 5.1 Update `src/news_org_system/news_api.py`:
  - [x] Import constants module
  - [x] Update error messages that list available sources
  - [x] Ensure CLI output displays string values (not enum repr)
- [x] 5.2 Clean up `src/news_org_system/readers/rss_reader.py`:
  - [x] Remove duplicate URL mapping (lines 33-35)
  - [x] Verify feed fetching still works after cleanup
- [x] 5.3 Test CLI commands:
  - [x] Run `news-org collect --source yonhap_economy --limit 5`
  - [x] Run `news-org stats`
  - [x] Verify output is correct

## 6. Verification and Validation

- [x] 6.1 Search for remaining hardcoded strings:
  - [x] `grep -r "yonhap_economy" src/ tests/` (should find only in constants)
  - [x] `grep -r "maeil_management" src/ tests/` (should find only in constants)
  - [x] `grep -r "etnews_today" src/ tests/` (should find only in constants)
  - [x] `grep -r '"yonhap"' src/ tests/` (should find only in constants)
  - [x] `grep -r '"maeil"' src/ tests/` (should find only in constants)
  - [x] `grep -r '"etnews"' src/ tests/` (should find only in constants)
- [x] 6.2 Verify no circular imports:
  - [x] Run `python -c "from news_org_system.readers.constants import SourceName, AdapterName"`
  - [x] Run `python -c "from news_org_system.readers.registry import FEED_REGISTRY, ADAPTER_REGISTRY"`
- [x] 6.3 Verify backward compatibility:
  - [x] Test all API endpoints return same responses
  - [x] Test all CLI commands work unchanged
  - [x] Verify MongoDB queries work correctly
- [x] 6.4 Final full test run: `pytest --cov=news_org_system --cov-report=term-missing`
- [x] 6.5 Check for type errors (if using mypy): `mypy src/news_org_system/`
- [x] 6.6 Verify IDE autocomplete works for constants

## 7. Documentation Updates

- [x] 7.1 Update `CLAUDE.md` with constants usage examples
- [x] 7.4 Verify auto-generated API docs (Swagger/ReDoc) are correct

## 8. Final Checks

- [x] 8.1 Ensure all files have been saved and committed
- [x] 8.2 Run final integration test: `pytest -v --tb=short`
- [x] 8.3 Verify API server starts without errors
- [x] 8.4 Test complete collection workflow end-to-end
- [x] 8.5 Check for any TODO or FIXME comments left in code
- [x] 8.6 Verify git status shows only expected changes
