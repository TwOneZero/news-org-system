## 1. Project Setup

- [x] 1.1 Add FastAPI and uvicorn dependencies to project
- [x] 1.2 Create `src/news_org_system/services/` directory
- [x] 1.3 Create `src/news_org_system/api/` directory structure
- [x] 1.4 Create `src/news_org_system/api/routes/` directory
- [x] 1.5 Create `src/news_org_system/api/models/` directory

## 2. Service Layer Implementation

- [x] 2.1 Create `services/__init__.py` with exports
- [x] 2.2 Implement `NewsCollectionService` class in `services/collection.py`
- [x] 2.3 Implement `ArticleQueryService` class in `services/query.py`
- [x] 2.4 Implement `StatisticsService` class in `services/stats.py`
- [x] 2.5 Add error handling and logging to services
- [x] 2.6 Write unit tests for collection service
- [x] 2.7 Write unit tests for query service
- [x] 2.8 Write unit tests for statistics service

## 3. API Models (DTOs)

- [x] 3.1 Create `api/models/__init__.py`
- [x] 3.2 Create `ArticleResponse` model for article data
- [x] 3.3 Create `CollectionRequest` model for triggering collection
- [x] 3.4 Create `CollectionResponse` model for collection results
- [x] 3.5 Create `ArticleListResponse` model for paginated results
- [x] 3.6 Create `StatisticsResponse` model for stats endpoint
- [x] 3.7 Create error response models
- [x] 3.8 Add model validation and serialization

## 4. FastAPI Application Setup

- [x] 4.1 Create `api/main.py` with FastAPI app factory
- [x] 4.2 Configure CORS middleware
- [x] 4.3 Set up dependency injection for services
- [x] 4.4 Create MongoDB connection dependency
- [x] 4.5 Add startup and shutdown event handlers
- [x] 4.6 Configure environment variables for API (host, port)

## 5. API Routes Implementation

- [x] 5.1 Create `api/routes/__init__.py`
- [x] 5.2 Implement health check endpoint at `/health`
- [x] 5.3 Create collection routes module
- [x] 5.4 Implement POST `/api/v1/collect` endpoint (all feeds)
- [x] 5.5 Implement POST `/api/v1/collect/{source}` endpoint (specific feed)
- [x] 5.6 Create query routes module
- [x] 5.7 Implement GET `/api/v1/articles` endpoint (with filters and pagination)
- [x] 5.8 Implement GET `/api/v1/articles/{id}` endpoint (single article)
- [x] 5.9 Create statistics routes module
- [x] 5.10 Implement GET `/api/v1/stats` endpoint (overall statistics)
- [x] 5.11 Implement GET `/api/v1/stats/{source}` endpoint (per-source statistics)
- [x] 5.12 Add error handlers for 404, 422, and 500 errors

## 6. CLI Refactoring

- [x] 6.1 Update `news_api.py` to use `NewsCollectionService`
- [x] 6.2 Update `news_api.py` to use `ArticleQueryService`
- [x] 6.3 Update `news_api.py` to use `StatisticsService`

## 7. Testing

- [x] 7.1 Write integration tests for collection endpoints
- [x] 7.2 Write integration tests for query endpoints
- [x] 7.3 Write integration tests for statistics endpoints
- [x] 7.4 Write tests for error handling
- [x] 7.5 Write tests for pagination
- [x] 7.6 Write tests for filtering
- [x] 7.7 Add test fixtures for test database

## 8. Documentation and Configuration

- [x] 8.1 Create API documentation in README
- [x] 8.2 Add example API requests to documentation
- [x] 8.3 Create example `.env` entries for API configuration
- [x] 8.4 Add API startup script or command
- [x] 8.5 Update main README with API usage instructions
- [x] 8.6 Document service layer architecture

## 9. Verification

- [x] 9.1 Run all unit tests and ensure they pass
- [x] 9.2 Run all integration tests and ensure they pass
- [x] 9.3 Start FastAPI application and verify health check
- [x] 9.4 Test collection endpoint manually
- [x] 9.5 Test query endpoint manually
- [x] 9.6 Test statistics endpoint manually
- [x] 9.7 Verify CLI commands still function correctly
- [x] 9.8 Check OpenAPI documentation at `/docs`
