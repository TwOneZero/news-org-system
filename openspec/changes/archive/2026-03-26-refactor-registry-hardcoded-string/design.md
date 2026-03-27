# Design: Refactor Registry Hardcoded Strings

## Context

### Current State

The news-org-system currently defines RSS feed sources and adapters in `src/news_org_system/readers/registry.py` with hardcoded string literals:

```python
FEED_REGISTRY: Dict[str, RSSFeedConfig] = {
    "yonhap_economy": RSSFeedConfig(
        source_name="yonhap_economy",  # duplicated key
        feed_url="https://www.yonhapnewstv.co.kr/category/news/economy/feed",
        adapter_name="yonhap",
        language="ko",
    ),
    "maeil_management": RSSFeedConfig(
        source_name="maeil_management",
        feed_url="https://www.mk.co.kr/rss/50100032/",
        adapter_name="maeil",
        language="ko",
    ),
    "etnews_today": RSSFeedConfig(
        source_name="etnews_today",
        feed_url="https://rss.etnews.com/Section901.xml",
        adapter_name="etnews",
        language="ko",
    ),
}
```

These hardcoded strings ("yonhap_economy", "maeil_management", "etnews_today", "yonhap", "maeil", "etnews") are used throughout:
- Service layer (collection, query, stats)
- API layer (models, routes)
- Tests (unit, integration, fixtures)
- CLI (error messages, validation)
- Documentation (examples, API docs)

### Problem Analysis

From the codebase exploration, we identified:
- **20+ files** reference these hardcoded strings
- **3 layers** (services, API, storage) depend on string values
- **50+ locations** across tests use source names directly
- **1 duplicate URL mapping** in `rss_reader.py` (legacy code)

When removing or renaming a source like "etnews_today", developers must:
1. Find all string usages via grep/search
2. Update each location manually
3. Risk missing indirect references (e.g., error messages)
4. Update tests separately
5. Verify documentation accuracy

### Constraints

- **Zero Breaking Changes**: API contracts, CLI interfaces, and service interfaces must remain unchanged
- **Python 3.12+**: Use modern Python features (enums, type aliases)
- **Pydantic Models**: Constants must be compatible with Pydantic validation
- **Test Coverage**: All existing tests must pass after refactoring
- **Documentation**: Generated from code (OpenAPI), so constants should be self-documenting

## Goals / Non-Goals

### Goals

1. **Single Source of Truth**: Define source names, adapter names, and URLs in one place
2. **Type Safety**: Use Python enums to prevent typos and enable IDE autocomplete
3. **Easy Maintenance**: Adding/removing sources requires changes in only one module
4. **IDE Support**: Constants should be discoverable via autocomplete
5. **Self-Documenting**: Code should be readable without external documentation
6. **100% Backward Compatibility**: No changes to external behavior or APIs

### Non-Goals

- **Dynamic Configuration**: Not adding runtime config files (YAML, JSON, env vars)
- **Database-Driven Sources**: Not moving feed configuration to database (future consideration)
- **API Changes**: Not modifying REST API contracts or behavior
- **Performance Optimization**: Not optimizing for runtime performance (constants are already fast)

## Decisions

### Decision 1: Use Python Enums for Constants

**Choice**: Use `enum.Enum` for source names and adapter names.

**Rationale**:
- **Type Safety**: Enums prevent typos at development time (not runtime)
- **IDE Support**: Autocomplete discovers all valid options
- **Single Source of Truth**: One place to define all values
- **String Conversion**: Can convert to strings for Pydantic/dict usage
- **Import-Friendly**: Easy to import: `from news_org_system.readers.constants import Source`

**Alternatives Considered**:

| Alternative | Rejected Because |
|-------------|------------------|
| String constants module | Less type-safe, no IDE autocomplete, can typo values |
| Dataclasses/pydantic models | Overkill for simple constants, more complex |
| Configuration files | Adds runtime parsing, harder to maintain, breaks type safety |
| Database storage | Too complex for current use case, adds infrastructure dependency |

**Implementation**:
```python
# readers/constants.py
from enum import Enum

class SourceName(str, Enum):
    """News source identifiers."""
    YONHAP_ECONOMY = "yonhap_economy"
    MAEIL_MANAGEMENT = "maeil_management"
    ETNEWS_TODAY = "etnews_today"

class AdapterName(str, Enum):
    """RSS adapter identifiers."""
    DEFAULT = "default"
    YONHAP = "yonhap"
    MAEIL = "maeil"
    ETNEWS = "etnews"
```

### Decision 2: Separate Module for Constants

**Choice**: Create `readers/constants.py` module.

**Rationale**:
- **Clear Organization**: Constants are clearly separated from logic
- **Import Flexibility**: Can import specific constants: `from .constants import SourceName`
- **Avoid Circular Imports**: Registry depends on constants, not vice versa
- **Future Extensibility**: Can add related constants (languages, categories) here

**Alternatives Considered**:
- **Constants in registry.py** → Rejected: Mixes configuration with logic, harder to import
- **Constants in __init__.py** → Rejected: Clutters namespace, unclear what's exported
- **Global constants module** → Rejected: Over-engineering, these are reader-specific

### Decision 3: Feed URLs as Class-Level Constants

**Choice**: Define feed URLs as class-level constants in `SourceName` enum.

**Rationale**:
- **Co-located**: Source name and URL are always defined together
- **Immutable**: URLs can't be accidentally modified
- **Discoverable**: IDE autocomplete shows URL when source is selected
- **Self-Documenting**: Each source has its URL immediately visible

**Implementation**:
```python
class SourceName(str, Enum):
    """News source identifiers with feed URLs."""
    YONHAP_ECONOMY = "yonhap_economy"
    YONHAP_ECONOMY_URL = "https://www.yonhapnewstv.co.kr/category/news/economy/feed"

    MAEIL_MANAGEMENT = "maeil_management"
    MAEIL_MANAGEMENT_URL = "https://www.mk.co.kr/rss/50100032/"

    ETNEWS_TODAY = "etnews_today"
    ETNEWS_TODAY_URL = "https://rss.etnews.com/Section901.xml"

    @classmethod
    def get_url(cls, source: 'SourceName') -> str:
        """Get feed URL for a source."""
        return getattr(cls, f"{source.name}_URL")
```

**Alternative Rejected**: Separate `FeedURL` enum → Rejected because it separates related values

### Decision 4: Registry Refactoring Strategy

**Choice**: Update registry to use enums while maintaining dict structure.

**Rationale**:
- **Backward Compatible**: Registry still returns dicts, keys are strings (via enum inheritance)
- **Minimal Changes**: Existing code using `FEED_REGISTRY[source_name]` still works
- **Type Safe**: Registry definition uses enums, preventing typos

**Implementation**:
```python
# readers/registry.py
from .constants import SourceName, AdapterName

FEED_REGISTRY: Dict[str, RSSFeedConfig] = {
    SourceName.YONHAP_ECONOMY: RSSFeedConfig(
        source_name=SourceName.YONHAP_ECONOMY,
        feed_url=SourceName.YONHAP_ECONOMY_URL,
        adapter_name=AdapterName.YONHAP,
        language="ko",
    ),
    # ...
}
```

### Decision 5: Gradual Migration Strategy

**Choice**: Refactor in layers from core to edges.

**Rationale**:
- **Incremental**: Can test each layer independently
- **Low Risk**: Core changes first, edges last
- **Easy Rollback**: Can revert individual layers if issues arise

**Migration Order**:
1. **Core**: Create constants module, update registry (2 files)
2. **Services**: Update service layer to import constants (3 files)
3. **API**: Update API models and routes (4 files)
4. **Tests**: Update test suite (10+ files)
5. **CLI**: Update CLI error messages (1 file)
6. **Cleanup**: Remove duplicate URL mapping in rss_reader.py

## Risks / Trade-offs

### Risk 1: Enum String Conversion

**Risk**: Pydantic models and MongoDB expect strings, not enum objects.

**Mitigation**:
- Use `str, Enum` multiple inheritance so enum values are strings
- Auto-convert in Pydantic validators if needed
- Test all serialization/deserialization paths

**Validation**:
```python
# Verify enum values are strings
assert isinstance(SourceName.YONHAP_ECONOMY, str)
assert SourceName.YONHAP_ECONOMY == "yonhap_economy"
```

### Risk 2: Breaking Dynamic Source Access

**Risk**: Code that dynamically constructs source name strings (e.g., `f"{source}_stats"`) will break.

**Mitigation**:
- Audit codebase for dynamic string construction
- Keep registry as dict for dynamic access
- Provide helper functions for common patterns

**Example**:
```python
# Before (dynamic)
source_name = "yonhap_economy"
feed_config = FEED_REGISTRY[source_name]

# After (still works - enum values are strings)
source_name = SourceName.YONHAP_ECONOMY  # this IS "yonhap_economy"
feed_config = FEED_REGISTRY[source_name]
```

### Risk 3: Test Maintenance Burden

**Risk**: 50+ test locations need updating, high chance of missing some.

**Mitigation**:
- Use global search-replace with careful validation
- Run tests after each file change
- Add test to verify all source names are in constants
- Keep string usage in tests where it makes sense (e.g., mock data)

**Strategy**:
- Run full test suite after each layer migration
- Use grep to find remaining hardcoded strings: `"yonhap_economy"`, `"etnews_today"`, etc.

### Risk 4: Enum Naming Conflicts

**Risk**: Enum member names (YONHAP_ECONOMY) might conflict with URL constants (YONHAP_ECONOMY_URL).

**Mitigation**:
- Use consistent naming convention: `{SOURCE_NAME}` and `{SOURCE_NAME}_URL`
- Document naming convention in docstrings
- Add linting rule to catch conflicts

### Trade-off: Verbosity vs Type Safety

**Trade-off**: `SourceName.YONHAP_ECONOMY` is more verbose than `"yonhap_economy"`.

**Acceptance**: Type safety and IDE support outweigh verbosity cost. Developer experience improves overall.

## Migration Plan

### Phase 1: Core Layer (Foundation)

**Files**: `readers/constants.py` (new), `readers/registry.py`

1. Create `readers/constants.py` with `SourceName` and `AdapterName` enums
2. Update `readers/registry.py` to import and use constants
3. Run unit tests: `pytest tests/unit/test_registry.py`
4. Verify registry exports: `python -c "from news_org_system.readers.constants import SourceName; print(SourceName.YONHAP_ECONOMY)"`

**Success Criteria**:
- All registry tests pass
- Registry dict keys are string values (not enum objects)
- Constants can be imported independently

**Rollback**: Delete constants.py, revert registry.py changes

### Phase 2: Service Layer

**Files**: `services/collection.py`, `services/query.py`, `services/stats.py`

1. Update imports: `from ..readers.constants import SourceName, AdapterName`
2. Replace hardcoded strings with enum values
3. Update error messages to use enum values
4. Run service tests: `pytest tests/unit/test_services.py`

**Success Criteria**:
- All service tests pass
- Services import constants correctly
- Error messages still display strings

**Rollback**: Revert service file changes

### Phase 3: API Layer

**Files**: `api/models/collection.py`, `api/models/stats.py`, `api/routes/collection.py`

1. Update Pydantic models to use constants in validators
2. Update route handlers to use constants
3. Verify OpenAPI schema generation: `curl http://localhost:8000/openapi.json`
4. Test API endpoints: `pytest tests/integration/test_api.py`

**Success Criteria**:
- API tests pass
- OpenAPI docs render correctly
- API responses unchanged (backward compatible)

**Rollback**: Revert API file changes

### Phase 4: Test Suite

**Files**: `tests/unit/test_registry.py`, `tests/conftest.py`, `tests/integration/` (10+ files)

1. Update test fixtures to use constants
2. Replace hardcoded strings in test assertions
3. Update test data and mock objects
4. Run full test suite: `pytest`

**Success Criteria**:
- All tests pass
- No test code still uses hardcoded source names
- Test coverage maintained

**Rollback**: Revert test file changes

### Phase 5: CLI and Cleanup

**Files**: `news_api.py`, `readers/rss_reader.py`

1. Update CLI error messages to use constants
2. Remove duplicate URL mapping in `rss_reader.py`
3. Run CLI commands: `news-org collect`, `news-org stats`
4. Final verification: Full test suite + manual CLI testing

**Success Criteria**:
- CLI works correctly
- No duplicate URL definitions
- Zero hardcoded strings remaining (verify via grep)

**Rollback**: Revert CLI and rss_reader.py changes

## Open Questions

### Q1: Should we validate that all enum members have corresponding registry entries?

**Status**: Open

**Options**:
1. Add startup validation that checks all `SourceName` members are in `FEED_REGISTRY`
2. Skip validation, rely on tests
3. Add linter rule instead

**Recommendation**: Option 1 (startup validation) - catches mismatches early

### Q2: Should feed URLs be in separate enum or as attributes of SourceName?

**Status**: Resolved (Decision 3) - as attributes in SourceName enum

**Rationale**: Keeps related values co-located, easier to maintain

### Q3: How to handle documentation generation (OpenAPI, README)?

**Status**: Resolved - no changes needed

**Rationale**: Enums inherit from str, so they serialize to strings correctly in OpenAPI docs

### Q4: Should we add a utility function to list all available sources?

**Status**: Open

**Options**:
1. Keep existing `list_feeds()` function
2. Add `SourceName.all()` class method
3. Both - convenience wrapper that calls enum

**Recommendation**: Option 1 (keep existing) - maintains backward compatibility

## Testing Strategy

### Unit Tests

- **Constants Module**: Test enum values, string conversion, URL retrieval
- **Registry**: Test registry uses enums, dict keys are strings
- **Services**: Test services use constants correctly
- **API Models**: Test Pydantic serialization with enums

### Integration Tests

- **API Endpoints**: Verify API contracts unchanged, responses valid
- **CLI Commands**: Test CLI with all commands
- **End-to-End**: Run full collection pipeline

### Regression Tests

- Search for remaining hardcoded strings: `grep -r "yonhap_economy" src/ tests/`
- Verify all imports resolve
- Check no circular dependencies
- Validate OpenAPI schema generation

## Success Criteria

1. ✅ Zero hardcoded source name strings in production code
2. ✅ Zero hardcoded adapter name strings in production code
3. ✅ All tests pass (unit, integration)
4. ✅ API contracts unchanged (backward compatible)
5. ✅ CLI functionality unchanged
6. ✅ OpenAPI docs generate correctly
7. ✅ No circular import errors
8. ✅ IDE autocomplete discovers all constants
9. ✅ Type checking passes (if using mypy/pyright)
