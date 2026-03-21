# Architectural Decision Records

This document records key architectural decisions made during the evolution of the news-org-system, including the rationale, alternatives considered, and trade-offs.

For the complete original design document from the FastAPI migration, see @openspec/changes/archive/2026-03-20-add-fastapi-service-layer/design.md.

## Context

The news-org-system began as a CLI-only application for collecting news from RSS feeds. As the project evolved, requirements emerged for:
- REST API for external system integration
- Better testability through separation of concerns
- Foundation for AI/ML features (LangChain, sentiment analysis)
- Reusable business logic layer

These decisions document the architectural evolution from CLI-only to a layered architecture with FastAPI integration.

---

## Decision 1: Service Layer Extraction

**Status**: ✅ Implemented (commit `b071203`)

### Problem
The original CLI architecture (`news_api.py`) had:
- **Tight Coupling**: Business logic embedded in CLI commands
- **Poor Testability**: Difficult to unit test without CLI framework
- **No Reusability**: Logic couldn't be imported as a library
- **Scattered Changes**: Adding features would require changes across CLI

### Decision
Extract business logic into a dedicated **service layer** between API and data layers.

### Architecture

**Before (CLI-only)**:
```
CLI Commands (news_api.py)
  └─ Direct calls to → Readers + Storage
```

**After (Layered)**:
```
CLI Commands
  └─ Service Layer → Readers + Storage

API Routes
  └─ Service Layer → Readers + Storage
```

### Rationale

**Benefits**:
1. **Code Reuse**: CLI and API share the same business logic
2. **Testability**: Services can be tested in isolation without HTTP/CLI framework
3. **Clear Boundaries**: Separation of orchestration from data access
4. **AI Integration**: Clear integration point for future AI features (AIService)

**Why Not Alternatives**:

| Alternative | Rejected Because |
|-------------|------------------|
| Keep logic in API routes | Can't reuse in CLI, harder to test |
| Move everything to readers | Readers should stay focused on parsing, not orchestration |
| Use framework-specific services | Ties to specific framework (FastAPI/Flask), reduces flexibility |

### Implementation

**Services Created**:
- **`NewsCollectionService`**: Orchestrate feed collection
- **`ArticleQueryService`**: Article retrieval and filtering
- **`StatisticsService`**: Data aggregation

**Example**:
```python
# Service layer (services/collection.py)
class NewsCollectionService:
    def __init__(self, store: MongoStore, registry: Dict = None):
        self.store = store
        self.registry = registry or FEED_REGISTRY

    def collect_all(self, days_back: int = 1, limit: int = 50) -> Dict:
        # Orchestrate collection from all sources
        for source_name, reader in self.readers.items():
            articles = reader.fetch(days_back, limit)
            self.store.save_articles(articles)
        return results
```

### Trade-offs

**Pros**:
- ✅ Clear separation of concerns
- ✅ Easy to test (mock storage/readers)
- ✅ Reusable across interfaces (CLI, API, future UI)
- ✅ Clear extension point for AI features

**Cons**:
- ❌ Additional indirection for simple operations
- ❌ More files to navigate

**Mitigation**:
- Keep services focused on orchestration, not data access
- Start simple, add abstraction only when needed

### Impact

This decision enabled:
- FastAPI integration without duplicating logic
- Unit testing without HTTP framework
- Future LangChain integration (AIService alongside existing services)

---

## Decision 2: FastAPI Framework Selection

**Status**: ✅ Implemented (commit `b071203`)

### Problem
Need a REST API framework for the news collection system.

### Decision
Use **FastAPI** as the REST API framework.

### Alternatives Considered

#### Flask
**Rejected Because**:
- Less type-safe (manual type validation)
- No automatic OpenAPI generation
- Manual schema validation with Marshmallow/Cerberus

#### Django REST
**Rejected Because**:
- Too heavyweight for this use case
- Requires Django ORM (we use MongoDB directly via pymongo)
- More complex deployment

#### FastAPI ✅
**Selected Because**:
- **Native Pydantic Integration**: Already using Pydantic models
- **Auto-generated OpenAPI**: `/docs` and `/redoc` out of the box
- **Type Safety**: Python type hints for validation
- **Async Support**: Ready for future async migration
- **Lightweight**: Minimal overhead vs Django

### Implementation

**Application Factory Pattern**:
```python
# api/main.py
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="News Collection System API",
        version="0.1.0",
        lifespan=lifespan  # Startup/shutdown hooks
    )
    # Register routes, middleware
    return app
```

**Dependency Injection**:
```python
# api/dependencies.py
def get_collection_service(
    store: MongoStore = Depends(get_store)
) -> NewsCollectionService:
    """Get CollectionService instance."""
    return NewsCollectionService(store=store)

# Usage in routes
@router.post("/collect")
def collect_articles(
    request: CollectionRequest,
    service: NewsCollectionService = Depends(get_collection_service)
):
    return service.collect_all(...)
```

### Benefits Realized

1. **Type Safety**: Catch errors at development time
2. **Auto Documentation**: Swagger UI at `/docs` without extra work
3. **Testing**: Easy to mock dependencies with `Depends()`
4. **Validation**: Pydantic models validate automatically

### Trade-offs

**Pros**:
- ✅ Excellent developer experience
- ✅ Modern Python patterns (type hints, async)
- ✅ Growing ecosystem and community

**Cons**:
- ❌ Younger framework than Flask/Django (less battle-tested)
- ❌ Smaller ecosystem (but FastAPI-compatible Flask middlewares work)

**Mitigation**:
- FastAPI is mature enough for production (v0.100+)
- Starlette (underlying framework) is proven

---

## Decision 3: Dependency Injection Pattern

**Status**: ✅ Implemented (commit `b071203`)

### Problem
How to manage component dependencies (services, storage) in API routes?

### Decision
Use FastAPI's built-in dependency injection system with service factories.

### Implementation

**Singleton Storage**:
```python
# api/dependencies.py
_store: Optional[MongoStore] = None

def get_store() -> MongoStore:
    """Get singleton MongoStore instance."""
    global _store
    if _store is None:
        _store = MongoStore()
    return _store
```

**Service Factories**:
```python
def get_collection_service(
    store: MongoStore = Depends(get_store)
) -> NewsCollectionService:
    """Get NewsCollectionService instance."""
    return NewsCollectionService(store=store)
```

**Usage in Routes**:
```python
@router.post("/collect")
def collect_articles(
    request: CollectionRequest,
    service: NewsCollectionService = Depends(get_collection_service)
):
    # Service is injected automatically
    return service.collect_all(...)
```

### Rationale

**Benefits**:
1. **Clear Dependencies**: Explicit in function signatures
2. **Testability**: Easy to mock in tests
3. **Singleton Management**: MongoStore shared across requests
4. **Lazy Loading**: Services created only when needed
5. **Framework Integration**: Built into FastAPI

**Alternatives Rejected**:

| Alternative | Rejected Because |
|-------------|------------------|
| Global variables | Hard to test, implicit dependencies |
| Manual service locator | Less clear, not type-safe |
| DI framework (dependency-injector) | Overkill for this size |

### Testing Benefits

```python
# Test with mocked service
def test_collect_articles(monkeypatch):
    """Test collection endpoint."""
    def mock_service():
        return Mock(spec=NewsCollectionService)

    # Override dependency
    app.dependency_overrides[get_collection_service] = mock_service

    response = client.post("/api/v1/collect")
    assert response.status_code == 200
```

### Future Extensibility

Easy to add:
- **Authentication**: Inject `current_user` dependency
- **Request Scoping**: Per-request service instances
- **Configuration**: Inject config objects

---

## Decision 4: DTO Separation (API Models vs Domain Models)

**Status**: ✅ Implemented (commit `b071203`)

### Problem
Should API responses use the same Pydantic models as domain entities?

### Decision
**No**. Create separate Pydantic models for API layer (DTOs), distinct from domain models.

### Architecture

**Domain Model** (`readers/base_reader.py`):
```python
class Article(BaseModel):
    """Domain model for articles."""
    url: str
    title: str
    content: str
    source: str
    published_at: datetime
    crawled_at: datetime
    metadata: Dict[str, Any] = {}
    # Internal fields
    _id: Optional[str] = None
```

**API Response DTO** (`api/models/articles.py`):
```python
class ArticleResponse(BaseModel):
    """API response model for articles."""
    id: str = Field(alias="_id")
    source: str
    url: str
    title: str
    content: str
    published_at: datetime
    crawled_at: datetime
    metadata: Dict[str, Any] = {}

    class Config:
        populate_by_name = True
```

### Rationale

**Benefits**:
1. **Independent Evolution**: API models can change without affecting domain
2. **Hide Internals**: Don't expose `_id`, internal metadata in API
3. **Different Validation**: API may have stricter validation rules
4. **Response Shaping**: Can include computed fields, hide sensitive data
5. **Versioning**: API v1 and v2 can have different models

**Example Differences**:
```python
# Domain: Has internal fields
class Article:
    _id: str  # MongoDB ObjectId
    internal_flags: Dict
    raw_feed_data: Dict

# API DTO: Clean response
class ArticleResponse:
    id: str  # Renamed from _id
    # No internal_flags or raw_feed_data exposed
```

### Trade-offs

**Pros**:
- ✅ API and domain evolve independently
- ✅ Can hide internal implementation details
- ✅ Different validation per layer

**Cons**:
- ❌ More model classes to maintain
- ❌ Mapping between layers (though minimal in this case)

**Mitigation**:
- Keep mapping simple (field aliases, minor transformations)
- Use Pydantic's `model_copy()` for conversion

### Implementation Pattern

```python
# Service layer returns domain models
articles: List[Article] = query_service.query_articles(...)

# API layer converts to DTOs
response_articles = [
    ArticleResponse(**article.model_dump())
    for article in articles
]
```

---

## Decision 5: Synchronous Services with Async API

**Status**: ✅ Current implementation

### Problem
Should services be async or sync?

### Decision
**Synchronous services** with async at API route level only.

### Architecture

```python
# API routes: async (FastAPI runs in threadpool)
@router.post("/collect")
async def collect_articles(
    service: NewsCollectionService = Depends(get_collection_service)
):
    # FastAPI runs sync service call in threadpool
    return service.collect_all(...)

# Services: synchronous
class NewsCollectionService:
    def collect_all(self, days_back: int, limit: int) -> Dict:
        # Sync MongoDB operations
        articles = reader.fetch(...)
        self.store.save_articles(articles)
        return results
```

### Rationale

**Why Sync**:
1. **MongoDB Driver**: `pymongo` is synchronous (sync driver)
2. **Simplicity**: Easier to implement and test
3. **Sufficient**: Current scale doesn't require async throughput
4. **FastAPI Handling**: FastAPI runs sync routes in threadpool automatically

**Trade-offs**:

| Factor | Sync (Current) | Async (Future) |
|--------|----------------|----------------|
| Throughput | Lower (threadpool) | Higher (event loop) |
| Complexity | Simple | More complex (async/await) |
| MongoDB Driver | pymongo (sync) | motor (async) |
| Testing | Simple | Requires async test setup |

### Decision: Accept Lower Throughput for Simplicity

**Reasoning**:
- Current usage: CLI + internal API, not high-traffic public API
- Can optimize later if needed (async migration path preserved)
- Development speed > premature optimization

### Future Migration Path

If async becomes necessary:
1. Switch to `motor` (async MongoDB driver)
2. Make service methods async: `async def collect_all(...)`
3. Update API routes: `await service.collect_all(...)`
4. Service interfaces remain compatible (just add `await`)

**Design for Future**:
- Service methods don't block on external HTTP calls (only DB)
- I/O operations are集中在 storage layer (easy to make async)
- No global state that would break with async

---

## Decision 6: Project Structure

**Status**: ✅ Implemented (commit `b071203`)

### Problem
How to organize code for clarity and scalability?

### Decision
Layered directory structure mirroring architecture.

### Structure

```
src/news_org_system/
├── api/              # FastAPI application
│   ├── main.py       # App factory
│   ├── dependencies.py  # DI functions
│   ├── models/       # API DTOs
│   └── routes/       # Route handlers
├── services/         # Business logic
│   ├── collection.py
│   ├── query.py
│   └── stats.py
├── readers/          # RSS parsing
│   ├── adapters/
│   └── registry.py
└── storage/          # MongoDB
    └── mongo_store.py
```

### Rationale

**By Layer** (not by feature):
- ✅ Clear boundaries
- ✅ Easy to find code
- ✅ Scales well (add services, routes separately)

**Alternative Rejected**: Feature-based structure
```
src/news_org_system/
├── collection/       # Feature: collection
│   ├── api.py        # API routes
│   ├── service.py    # Service
│   └── storage.py    # Data access
```

**Rejected Because**:
- Harder to see architecture at a glance
- Duplication across features (API patterns, service patterns)
- Harder to share code between features

---

## Summary of Architectural Principles

Based on these decisions, the system follows:

1. **Layered Architecture**: Clear separation (API → Service → Data)
2. **Dependency Injection**: Explicit, testable dependencies
3. **DTO Separation**: API models independent from domain
4. **Synchronous First**: Simple over fast, async-ready
5. **Factory Pattern**: App and service factories for flexibility
6. **Adapter Pattern**: Extensible feed parsing

These principles enable:
- ✅ Testability (mock at any layer)
- ✅ Reusability (services in CLI and API)
- ✅ Extensibility (clear extension points)
- ✅ Maintainability (clear structure)
