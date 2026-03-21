# Extending the Service Layer

This guide explains how to extend the service layer with new services, following established patterns in the news-org-system.

## Overview

The **service layer** contains business logic that orchestrates between the API layer and data layer (readers + storage). Services are reusable by both CLI and API.

### Current Services

| Service | Responsibility | Location |
|---------|---------------|----------|
| `NewsCollectionService` | Orchestrate RSS feed collection | `services/collection.py` |
| `ArticleQueryService` | Query and retrieve articles | `services/query.py` |
| `StatisticsService` | Aggregate statistics | `services/stats.py` |

## Service Layer Architecture

### Design Principles

1. **Orchestration, Not Data Access**: Services coordinate between readers and storage, but don't directly access database
2. **Dependency Injection**: Services receive dependencies via constructor
3. **Error Handling**: Graceful error handling with logging
4. **Reusability**: Services work with CLI and API
5. **Testability**: Mock dependencies for unit testing

### Service Structure

```python
class ExampleService:
    """Service for [purpose].

    This service provides [what it does].
    """

    def __init__(self, store: MongoStore, ...):
        """Initialize the service.

        Args:
            store: MongoStore instance for data access
            ...: Other dependencies
        """
        self.store = store
        # ... initialize other dependencies

    def method_name(self, ...) -> Dict:
        """Public method that does something.

        Args:
            ...: Method arguments

        Returns:
            Dictionary with results
        """
        # ... implementation
```

## Creating a New Service

### Step 1: Define Service Class

Create `src/news_org_system/services/your_service.py`:

```python
"""Service for [your purpose]."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..storage import MongoStore

logger = logging.getLogger(__name__)


class YourService:
    """Service for [what it does].

    This service provides [key capabilities].
    """

    def __init__(self, store: MongoStore, other_dep=None):
        """Initialize the service.

        Args:
            store: MongoStore instance for data access
            other_dep: Optional other dependency
        """
        self.store = store
        self.other_dep = other_dep
```

### Step 2: Implement Methods

#### Example: Data Processing Service

```python
class DataProcessingService:
    """Service for processing article data."""

    def __init__(self, store: MongoStore):
        """Initialize the service."""
        self.store = store

    def process_recent_articles(
        self,
        hours: int = 24,
        batch_size: int = 100
    ) -> Dict:
        """Process articles from the last N hours.

        Args:
            hours: Number of hours to look back
            batch_size: Number of articles to process at once

        Returns:
            Dictionary with processing results:
            {
                "processed": int,
                "failed": int,
                "errors": List[str]
            }
        """
        from datetime import timedelta

        # Calculate date range
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Query recent articles
        articles = self.store.articles_collection.find({
            "published_at": {"$gte": cutoff_time}
        }).limit(batch_size)

        results = {
            "processed": 0,
            "failed": 0,
            "errors": []
        }

        # Process each article
        for article in articles:
            try:
                # Your processing logic here
                self._process_single_article(article)
                results["processed"] += 1

            except Exception as e:
                logger.error(f"Error processing article {article.get('_id')}: {e}")
                results["failed"] += 1
                results["errors"].append(str(e))

        logger.info(f"Processed {results['processed']} articles, {results['failed']} failed")

        return results

    def _process_single_article(self, article: Dict) -> None:
        """Process a single article.

        Args:
            article: Article document from MongoDB
        """
        # Your processing logic
        # Example: Extract entities, update metadata, etc.
        pass
```

#### Example: Analytics Service

```python
class AnalyticsService:
    """Service for article analytics and insights."""

    def __init__(self, store: MongoStore):
        """Initialize the service."""
        self.store = store

    def get_trending_keywords(
        self,
        source: Optional[str] = None,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict]:
        """Get trending keywords from recent articles.

        Args:
            source: Filter by source (optional)
            days: Number of days to look back
            limit: Maximum number of keywords to return

        Returns:
            List of dictionaries with keyword and count:
            [
                {"keyword": str, "count": int},
                ...
            ]
        """
        from datetime import timedelta
        from collections import Counter

        # Calculate date range
        cutoff_time = datetime.now() - timedelta(days=days)

        # Build query
        query = {"published_at": {"$gte": cutoff_time}}
        if source:
            query["source"] = source

        # Fetch articles
        articles = self.store.articles_collection.find(
            query,
            {"tags": 1, "title": 1}
        )

        # Extract and count keywords
        keywords = []
        for article in articles:
            # Extract from tags
            if "tags" in article:
                keywords.extend(article["tags"])

            # You could also extract from title, content, etc.

        # Count and sort
        counter = Counter(keywords)
        trending = [
            {"keyword": keyword, "count": count}
            for keyword, count in counter.most_common(limit)
        ]

        return trending
```

### Step 3: Export from Package

Update `src/news_org_system/services/__init__.py`:

```python
"""Service layer for news collection system."""

from .collection import NewsCollectionService
from .query import ArticleQueryService
from .stats import StatisticsService
from .your_service import YourService  # Add your service

__all__ = [
    "NewsCollectionService",
    "ArticleQueryService",
    "StatisticsService",
    "YourService",  # Export it
]
```

## Dependency Injection Patterns

### Constructor Injection

Pass dependencies via constructor (recommended):

```python
class YourService:
    def __init__(self, store: MongoStore, registry: Optional[Dict] = None):
        self.store = store
        self.registry = registry or FEED_REGISTRY
```

### Optional Dependencies

Make dependencies optional with defaults:

```python
class YourService:
    def __init__(
        self,
        store: MongoStore,
        cache: Optional[Cache] = None,
        notifier: Optional[Notifier] = None
    ):
        self.store = store
        self.cache = cache  # May be None
        self.notifier = notifier  # May be None

    def method(self):
        # Check if dependency exists before using
        if self.cache:
            self.cache.get(...)
```

### Factory Functions

Create factory functions for complex initialization:

```python
def create_your_service_with_cache(store: MongoStore) -> YourService:
    """Create service with cache dependency."""
    cache = RedisCache()
    return YourService(store=store, cache=cache)
```

## Common Service Patterns

### Pagination

Follow the pagination pattern from `ArticleQueryService`:

```python
def query_with_pagination(
    self,
    page: int = 1,
    page_size: int = 20
) -> Dict:
    """Query with pagination support."""

    # Enforce maximum page size
    max_page_size = 100
    effective_page_size = min(page_size, max_page_size)

    # Calculate skip
    skip = (page - 1) * effective_page_size

    # Get total count
    total = self.store.collection.count_documents({})

    # Calculate total pages
    total_pages = (total + effective_page_size - 1) // effective_page_size

    # Execute query
    results = self.store.collection.find({}) \
        .skip(skip) \
        .limit(effective_page_size)

    return {
        "results": list(results),
        "total": total,
        "page": page,
        "page_size": effective_page_size,
        "total_pages": total_pages
    }
```

### Filtering

Follow the filtering pattern:

```python
def query_with_filters(
    self,
    source: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    keyword: Optional[str] = None
) -> List:
    """Query with multiple filters."""

    query = {}

    # Add source filter
    if source:
        query["source"] = source

    # Add date range filter
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query["published_at"] = date_filter

    # Add keyword search
    if keyword:
        query["$or"] = [
            {"title": {"$regex": keyword, "$options": "i"}},
            {"content": {"$regex": keyword, "$options": "i"}}
        ]

    return self.store.collection.find(query)
```

### Batch Processing

Process items in batches for efficiency:

```python
def process_in_batches(
    self,
    query: Dict,
    batch_size: int = 100,
    processor: Callable = None
) -> Dict:
    """Process documents in batches."""

    skip = 0
    total_processed = 0
    errors = []

    while True:
        # Fetch batch
        batch = list(
            self.store.collection.find(query)
            .skip(skip)
            .limit(batch_size)
        )

        if not batch:
            break

        # Process batch
        for doc in batch:
            try:
                if processor:
                    processor(doc)
                total_processed += 1
            except Exception as e:
                errors.append(str(e))

        # Move to next batch
        skip += batch_size

    return {
        "total_processed": total_processed,
        "errors": errors
    }
```

### Error Handling

Consistent error handling pattern:

```python
def method_with_error_handling(self, ...) -> Dict:
    """Method with comprehensive error handling."""

    try:
        # Validate inputs
        if not self._validate_inputs(...):
            raise ValueError("Invalid inputs")

        # Execute logic
        result = self._do_work(...)

        # Log success
        logger.info(f"Operation completed successfully")

        return {
            "status": "success",
            "data": result
        }

    except ValueError as e:
        # Input validation errors
        logger.warning(f"Validation error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "error_type": "validation"
        }

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": "An unexpected error occurred",
            "error_type": "internal"
        }
```

## Testing Services

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from news_org_system.services import YourService

def test_your_service_method():
    """Test service method with mocked storage."""

    # Arrange
    mock_store = Mock()
    mock_store.collection.find.return_value = [
        {"title": "Article 1"},
        {"title": "Article 2"}
    ]

    service = YourService(store=mock_store)

    # Act
    result = service.your_method(param="value")

    # Assert
    assert result["status"] == "success"
    assert len(result["data"]) == 2
    mock_store.collection.find.assert_called_once()
```

### Integration Test Example

```python
import pytest
from news_org_system.services import YourService
from news_org_system.storage import MongoStore

@pytest.mark.integration
def test_service_integration(db_instance):
    """Test service with real database."""

    # Arrange
    store = MongoStore()
    service = YourService(store=store)

    # Act
    result = service.your_method()

    # Assert
    assert result["status"] == "success"
```

## Integrating with API Layer

### Step 1: Create Dependency Function

Add to `api/dependencies.py`:

```python
def get_your_service(
    store: MongoStore = Depends(get_store)
) -> YourService:
    """Get YourService instance."""
    from ..services import YourService
    return YourService(store=store)
```

### Step 2: Create Route Handler

Create `api/routes/your_routes.py`:

```python
from fastapi import APIRouter, Depends
from ..dependencies import get_your_service
from ..services import YourService

router = APIRouter()

@router.post("/process")
def process_articles(
    param: str,
    service: YourService = Depends(get_your_service)
):
    """Process articles with service."""
    result = service.your_method(param=param)
    return result
```

### Step 3: Register Router

Update `api/main.py`:

```python
from .routes import your_routes

app.include_router(
    your_routes.router,
    prefix="/api/v1",
    tags=["YourFeature"]
)
```

## Integrating with CLI Layer

Services work with CLI without modification:

```python
# news_api.py or CLI module

from news_org_system.services import YourService
from news_org_system.storage import MongoStore

def cli_command():
    """CLI command using service."""
    store = MongoStore()
    service = YourService(store=store)

    result = service.your_method(param="value")

    print(f"Processed: {result['processed']}")
```

## Performance Considerations

### Lazy Loading

Lazy-load expensive resources:

```python
class YourService:
    def __init__(self, store: MongoStore):
        self.store = store
        self._heavy_resource = None

    @property
    def heavy_resource(self):
        """Lazy-load heavy resource."""
        if self._heavy_resource is None:
            self._heavy_resource = self._create_heavy_resource()
        return self._heavy_resource
```

### Caching

Cache expensive computations:

```python
from functools import lru_cache

class YourService:
    @lru_cache(maxsize=128)
    def _expensive_computation(self, param: str) -> Dict:
        """Expensive computation with caching."""
        # Expensive operation
        return result
```

### Streaming

Stream large result sets:

```python
def stream_articles(self, query: Dict):
    """Stream articles one at a time."""

    cursor = self.store.collection.find(query)

    for article in cursor:
        yield article
```

## Best Practices

### 1. **Keep Services Focused**

Each service should have a single, clear responsibility.

```python
# Good: Single responsibility
class ArticleSummarizationService:
    """Summarize articles."""
    pass

class ArticleSentimentService:
    """Analyze sentiment."""
    pass

# Bad: Multiple responsibilities
class ArticleProcessingService:
    """Summarize, sentiment, translate, etc."""
    pass
```

### 2. **Use Type Hints**

Help with IDE support and catch errors early:

```python
def query_articles(
    self,
    source: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """Query articles with type hints."""
    pass
```

### 3. **Log Important Operations**

Help with debugging and monitoring:

```python
import logging

logger = logging.getLogger(__name__)

def important_method(self):
    """Log start, success, and errors."""
    logger.info("Starting important operation")

    try:
        result = self._do_work()
        logger.info(f"Operation completed: {len(result)} items")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        raise
```

### 4. **Validate Inputs**

Fail fast with clear error messages:

```python
def method_with_validation(self, article_id: str):
    """Validate inputs before processing."""

    if not article_id:
        raise ValueError("article_id is required")

    if not isinstance(article_id, str):
        raise TypeError("article_id must be a string")

    # Proceed with validated input
```

### 5. **Return Consistent Structures**

Use consistent return structures:

```python
# Recommended structure
{
    "status": "success",  # or "error"
    "data": ...,          # on success
    "error": ...,         # on error
    "metadata": {...}     # optional metadata
}
```
