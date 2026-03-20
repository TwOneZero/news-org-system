## Context

The current system has RSS feed collection logic embedded in the CLI (`news_api.py`). The architecture has:

- **Readers Layer**: `BaseReader`, `RSSReader` with adapter pattern for site-specific parsing
- **Storage Layer**: `MongoStore` with URL-based deduplication and indexing
- **CLI Layer**: Direct orchestration of collection and statistics

This design worked for CLI-only usage but creates challenges for:
1. **Web Integration**: No REST API for external systems
2. **Testing**: Tight coupling makes unit testing difficult
3. **Extensibility**: Adding AI features (LangChain summarization, sentiment analysis) would require scattered changes
4. **Reusability**: Collection logic can't be imported as a library

## Goals / Non-Goals

**Goals:**
- Provide REST API for news collection and retrieval
- Extract business logic into testable, reusable service layer
- Enable future AI/ML feature integration (LangChain) without structural changes
- Maintain backward compatibility with existing CLI
- Introduce dependency injection for better testability

**Non-Goals:**
- Complete rewrite of existing readers/adapters (they work well)
- Changes to MongoDB schema or storage layer
- Authentication/authorization (can be added later)
- Real-time WebSocket endpoints (synchronous REST only)
- Admin UI or dashboard (API-only)

## Decisions

### 1. Layered Architecture with Service Layer

**Choice**: Introduce a dedicated service layer between API and data layers.

**Rationale**:
- Separates business logic from HTTP concerns
- Makes CLI and API share the same logic
- Easier to test in isolation
- Clear boundary for future AI feature integration

**Alternatives Considered**:
- Keep logic in API routes →Rejected: Can't reuse in CLI, harder to test
- Move everything to readers →Rejected: Readers should stay focused on parsing

### 2. FastAPI for REST API

**Choice**: Use FastAPI framework.

**Rationale**:
- Native Pydantic integration (already using Pydantic models)
- Auto-generated OpenAPI documentation
- Async support for future scalability
- Type safety with Python type hints
- Lightweight, no heavy framework overhead

**Alternatives Considered**:
- Flask →Rejected: Less type-safe, manual schema validation
- Django REST →Rejected: Too heavyweight for this use case

### 3. Dependency Injection Pattern

**Choice**: Use FastAPI's dependency injection system with service factories.

**Rationale**:
- Built-in to FastAPI (`Depends()`)
- Makes testing easy (can mock services)
- Clear declaration of component dependencies
- Supports future extension (e.g., adding auth per-request)

**Example**:
```python
def get_collection_service() -> NewsCollectionService:
    return NewsCollectionService(store=store, registry=registry)
```

### 4. Project Structure

**Choice**: Create new `api/` and `services/` directories.

**Structure**:
```
src/news_org_system/
├── api/              # FastAPI application
│   ├── __init__.py
│   ├── main.py       # FastAPI app creation
│   ├── routes/       # API route modules
│   └── models/       # Request/response DTOs
├── services/         # Business logic layer
│   ├── __init__.py
│   ├── collection.py # NewsCollectionService
│   └── query.py      # ArticleQueryService
├── readers/          # (unchanged)
└── storage/          # (MongoDB Client)
```

**Rationale**:
- Clear separation of concerns
- Easy to navigate
- Scales well for future features

### 5. API Model Strategy

**Choice**: Create separate Pydantic models for API layer (DTOs), distinct from domain models.

**Rationale**:
- API models can evolve independently
- Can hide internal fields from API responses
- Validation rules may differ for API vs internal
- Domain models stay focused on business logic

**Example**:
- Domain: `Article` (in `readers/base.py`)
- API: `ArticleResponse` (in `api/models/`)

## Risks / Trade-offs

### Risk: Service Layer Abstraction Overhead

**Risk**: Adding a service layer may introduce unnecessary indirection for simple operations.

**Mitigation**:
- Keep services focused on orchestration, not data access
- Delegate complex logic to appropriate layers
- Start simple, add abstraction only when needed

### Risk: Breaking Existing CLI

**Risk**: Refactoring `news_api.py` could break existing CLI commands.

**Mitigation**:
- Refactor incrementally, keeping CLI functional throughout
- Run CLI tests after each change
- Mark CLI as deprecated but functional in transition period

### Trade-off: Sync vs Async

**Decision**: Use synchronous Python in service layer, async at API route level only.

**Rationale**:
- MongoDB driver is synchronous
- Simpler to implement and test
- Can add async later if needed
- FastAPI handles sync route execution in threadpool

**Trade-off**: Lower throughput vs implementation simplicity. Acceptable for current scale.

## Migration Plan

### Phase 1: Service Layer Extraction
1. Create `services/` directory
2. Implement `NewsCollectionService` with existing logic
3. Implement `ArticleQueryService` for article retrieval
4. Keep CLI working, refactor to use services

### Phase 2: FastAPI Application
1. Create `api/` directory structure
2. Implement basic FastAPI app with health check
3. Add API routes for collection and query
4. Create API model DTOs

### Phase 3: Integration and Testing
1. Integration tests for API endpoints
2. Ensure CLI still works
3. Update documentation

### Rollback Strategy
- Each phase is independently reversible
- Git commits provide rollback points
- CLI functionality preserved throughout

## Open Questions

1. **API Authentication**: Should we add API key authentication now or later?
   - **Decision**: Later - focus on core functionality first

2. **Pagination Strategy**: What pagination approach for article queries?
   - **Decision**: Cursor-based pagination using MongoDB `_id` for simplicity

3. **Async Future**: Should services be designed for async migration?
   - **Decision**: Keep sync for now, design interfaces to be async-compatible
