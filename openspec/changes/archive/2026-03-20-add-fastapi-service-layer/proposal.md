## Why

The current CLI-based RSS collection system lacks a programmatic API interface and has tight coupling between collection logic and the CLI layer. This makes it difficult to integrate with web services, external systems, or future AI-powered features like article summarization and sentiment analysis. Adding a service layer abstraction now will provide a clean foundation for extensibility.

## What Changes

- Add FastAPI application with REST API endpoints for news collection and retrieval
- Extract RSS collection logic into a dedicated service layer (`NewsCollectionService`)
- Refactor existing `news_api.py` CLI to use the new service layer
- Add API endpoints for:
  - Triggering news collection from configured feeds
  - Retrieving collected articles with filtering and pagination
  - Getting collection statistics
- Add project structure to support future AI/ML features (LangChain integration)
- Introduce dependency injection pattern for better testability and extensibility

## Capabilities

### New Capabilities

- `rest-api`: HTTP REST API for accessing news collection and retrieval functionality
- `news-collection-service`: Service layer abstraction for RSS feed collection operations
- `article-query`: Query and filter collected articles with pagination support
- `collection-stats`: Statistics and metrics for news collection operations

### Modified Capabilities

(None - this is a new feature addition, no existing spec requirements are changing)

## Impact

**Affected Code:**
- `src/news_org_system/news_api.py`: Will be refactored to use service layer
- `src/news_org_system/readers/`: May need minor adjustments for service integration

**New Code:**
- `src/news_org_system/services/`: New service layer directory
- `src/news_org_system/api/`: New FastAPI application directory
- API models/schemas for request/response DTOs

**Dependencies:**
- Add `fastapi`, `uvicorn`, `pydantic` (already present, will extend usage)

**Systems:**
- MongoDB storage remains unchanged
- Existing RSS feed adapters remain unchanged
- CLI commands will be preserved for backward compatibility
