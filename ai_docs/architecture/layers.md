# Layer Architecture

The news-org-system follows a **layered architecture** pattern with clear separation of concerns. This design enables independent testing, code reuse between CLI and API, and future extensibility for AI features.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  - HTTP request/response handling                            │
│  - Route definitions (collection, query, stats, health)      │
│  - Request validation with Pydantic                          │
│  - Dependency injection                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  - Business logic orchestration                              │
│  - CollectionService: News collection workflows              │
│  - QueryService: Article retrieval and filtering             │
│  - StatisticsService: Data aggregation                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │   Readers       │  │        Storage                   │  │
│  │  - RSSReader    │  │  - MongoStore                    │  │
│  │  - Adapters     │  │  - URL-based deduplication       │  │
│  │  - Registry     │  │  - Indexing                      │  │
│  └─────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## API Layer

**Location**: `src/news_org_system/api/`

### Responsibilities

- **HTTP Handling**: Request/response processing, status codes, error handling
- **Route Definition**: RESTful endpoint organization
- **Validation**: Request parameter validation using Pydantic models
- **Dependency Injection**: Service instantiation via FastAPI's `Depends()`
- **Documentation**: Auto-generated OpenAPI/Swagger docs

### Key Components

#### Application Factory (`main.py`)
```python
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        lifespan=lifespan,  # Startup/shutdown hooks
        title="News Collection System API",
        version="0.1.0"
    )
    # Register routes, middleware, exception handlers
    return app
```

**Design Points**:
- Factory pattern for testability (can create multiple app instances)
- Lifespan context manager for MongoDB connection management
- CORS middleware configuration
- Global exception handlers for consistent error responses

#### Dependency Injection (`dependencies.py`)
```python
def get_collection_service(
    store: MongoStore = Depends(get_store)
) -> NewsCollectionService:
    """Get NewsCollectionService instance."""
    return NewsCollectionService(store=store)
```

**Benefits**:
- **Testing**: Easy to mock services in tests
- **Singleton Pattern**: MongoStore shared across requests
- **Clear Dependencies**: Explicit service requirements
- **Lazy Loading**: Services created only when needed

#### Route Organization (`routes/`)
- **`health.py`**: Health check endpoint
- **`collection.py`**: News collection endpoints (`POST /api/v1/collect`)
- **`query.py`**: Article query endpoints (`GET /api/v1/articles`)
- **`stats.py`**: Statistics endpoints (`GET /api/v1/stats`)

Each route module:
- Uses dependency injection to get services
- Defines Pydantic models for request/response
- Handles HTTP-specific logic (status codes, headers)
- Delegates business logic to service layer

#### API Models (`models/`)
Separate Pydantic models for API layer (DTOs):
- **`articles.py`**: Article response models
- **`collection.py`**: Collection request/response models
- **`stats.py`**: Statistics response models
- **`common.py`**: Shared models (pagination, error responses)

**Why Separate DTOs?**
- API models evolve independently from domain models
- Can hide internal fields (e.g., `_id`, internal metadata)
- Different validation rules for API vs internal use
- Domain models stay focused on business logic

### Testing Strategy

```python
# Test with mocked services
def test_collect_articles(monkeypatch):
    """Test collection endpoint with mocked service."""
    async def mock_collect(*args, **kwargs):
        return {"total_saved": 10}

    monkeypatch.setattr(
        "news_org_system.api.routes.collection.NewsCollectionService.collect_all",
        mock_collect
    )

    response = client.post("/api/v1/collect")
    assert response.status_code == 200
```

- Mock service layer, not HTTP internals
- Test FastAPI `TestClient` for integration tests
- Validate request/response models

## Service Layer

**Location**: `src/news_org_system/services/`

### Responsibilities

- **Business Logic**: Core application workflows
- **Orchestration**: Coordinating between readers and storage
- **Error Handling**: Graceful error management and logging
- **Transformation**: Converting between layers if needed
- **Code Reuse**: Shared by both CLI and API

### Key Services

#### CollectionService (`collection.py`)
**Purpose**: Orchestrate news collection from RSS feeds.

**Key Methods**:
- `collect_all()`: Collect from all configured feeds
- `collect_from_source()`: Collect from specific feed
- `list_sources()`: List available feed sources

**Workflow**:
```python
# 1. Lazy-load RSS readers for all sources
readers = self.readers  # Dictionary of source_name -> RSSReader

# 2. For each source:
#    a. Fetch articles from RSS feed
articles = reader.fetch(start_date, end_date, limit)

#    b. Save to storage with deduplication
save_result = self.store.save_articles(articles)

#    c. Track results (fetched, saved, skipped)
results["sources"][source_name] = {
    "fetched": len(articles),
    "saved": save_result["saved"],
    "skipped": save_result["skipped"]
}
```

**Design Points**:
- **Lazy Loading**: Readers created only when needed
- **Error Isolation**: Failure in one source doesn't stop others
- **Detailed Results**: Per-source statistics for monitoring
- **Date Range Handling**: Flexible date range parameters

#### QueryService (`query.py`)
**Purpose**: Retrieve and filter articles from storage.

**Key Methods**:
- `query_articles()`: Search with filters (source, date range, keyword)
- `get_article()`: Get single article by ID
- Pagination support

#### StatisticsService (`stats.py`)
**Purpose**: Aggregate statistics from stored articles.

**Key Methods**:
- `get_overall_stats()`: Total articles, sources, date ranges
- `get_source_stats()`: Per-source statistics
- `get_collection_history()`: Recent collection operations

### Testing Strategy

```python
# Test with mocked storage
def test_collect_all():
    """Test CollectionService.collect_all()."""
    mock_store = Mock(spec=MongoStore)
    mock_store.save_articles.return_value = {"saved": 5, "skipped": 2}

    service = NewsCollectionService(store=mock_store)
    result = service.collect_all(limit=10)

    assert result["total_saved"] == 5
    mock_store.save_articles.assert_called()
```

- Mock storage layer, not service internals
- Test business logic and error scenarios
- Verify orchestration (readers → storage flow)

## Data Layer

**Location**: `src/news_org_system/readers/` and `src/news_org_system/storage/`

### Reader Sub-Layer

**Purpose**: Parse RSS/Atom feeds and extract article data.

#### Components

**RSSReader** (`rss_reader.py`)
- Generic RSS/Atom feed parsing
- Adapter pattern for site-specific extraction
- Date filtering and limiting

**Adapters** (`adapters/`)
- **`base.py`**: Abstract `BaseRSSAdapter` interface
- **`default_adapter.py`**: Default parsing logic
- **`yonhap_adapter.py`**: Yonhap News-specific parsing
- **`maeil_adapter.py`**: Maeil Business-specific parsing
- **`etnews_adapter.py`**: ETNews-specific parsing

**Registry** (`registry.py`)
- Centralized feed configuration
- Maps source names to `RSSFeedConfig` objects
- Defines feed URL, adapter, language per source

#### Data Models
- **`Article`**: Domain model (title, content, url, published_at, etc.)
- **`RSSFeedConfig`**: Feed configuration (source_name, feed_url, adapter_name)

### Storage Sub-Layer

**Purpose**: Persist articles and provide query interface.

#### MongoStore (`storage/mongo_store.py`)

**Key Features**:
- **URL-based Deduplication**: Prevents duplicate articles
- **Indexing**: Efficient queries on url, source, published_at
- **Flexible Querying**: Filter by source, date range, keyword
- **Statistics Aggregation**: Built-in aggregation pipelines

**Key Methods**:
- `save_articles()`: Bulk insert with duplicate handling
- `query_articles()`: Search with filters and pagination
- `get_article()`: Retrieve single article by ID
- `get_stats()`: Aggregate statistics

## Inter-Layer Communication

### Request Flow Example: POST /api/v1/collect

```
1. HTTP Request → API Layer
   POST /api/v1/collect
   Body: {"days_back": 1, "limit": 50}

2. API Layer (routes/collection.py)
   - Validate request with Pydantic model
   - Get CollectionService via dependency injection
   - Call service.collect_all(days_back=1, limit=50)

3. Service Layer (services/collection.py)
   - Calculate date range from days_back
   - Get RSS readers from registry
   - For each source:
     a. Call reader.fetch() → List[Article]
     b. Call store.save_articles(articles) → SaveResult
     c. Aggregate results

4. Data Layer
   - Reader Layer: RSSReader.fetch()
     * Parse feed with feedparser
     * Extract items with adapter
     * Return List[Article]
   - Storage Layer: MongoStore.save_articles()
     * Check for duplicates (URL-based)
     * Insert new articles
     * Return {saved, skipped} counts

5. Response Flow (Reverse)
   Service Layer → API Layer → HTTP Response
   {
     "timestamp": "...",
     "total_fetched": 150,
     "total_saved": 45,
     "sources": {...}
   }
```

### Dependency Graph

```
API Layer
  └─ depends on → Service Layer
                    └─ depends on → Data Layer
                                    ├─ Readers (RSSReader, adapters)
                                    └─ Storage (MongoStore)

Service Layer
  └─ can be used independently by CLI

No reverse dependencies (Data Layer → Service Layer)
```

## Benefits of This Architecture

### 1. **Separation of Concerns**
- API: HTTP only
- Services: Business logic only
- Data: Parsing/persistence only

### 2. **Testability**
- Each layer can be tested in isolation
- Mock dependencies easily
- Clear test boundaries

### 3. **Code Reuse**
- Service layer shared by CLI and API
- Readers reusable in different contexts
- Storage layer abstracted (can swap implementations)

### 4. **Extensibility**
- Add new API endpoints without changing services
- Add new services without breaking existing ones
- Swap storage implementation (e.g., PostgreSQL)
- Easy to add AI features (new AIService)

### 5. **Independent Evolution**
- API models change without affecting domain models
- Services change without affecting HTTP layer
- Storage changes don't affect business logic

## Future Considerations

### Async Migration
Current: Sync services with async API routes (FastAPI runs sync in threadpool)

Future path:
1. Make service methods async (`async def collect_all()`)
2. Use async MongoDB driver (motor)
3. Benefits: Better throughput for concurrent requests

### Caching Layer
Potential addition:
- Cache frequently accessed articles
- Cache feed parsing results
- Integrate between Service and Data layers

### Event Bus
For future AI features:
- Service layer publishes events (article_collected)
- AI services subscribe and process (summarization, sentiment)
- Decouples collection from AI processing
