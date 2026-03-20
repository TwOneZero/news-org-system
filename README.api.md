# News Collection System API

REST API for collecting and querying news articles from RSS feeds.

## Quick Start

### Starting the API Server

```bash
# Using the installed command
news-org-api

# Or using Python module
python -m news_org_system.api.main

# Or with uvicorn directly
uvicorn news_org_system.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check

**GET** `/health`

Check API and database connectivity status.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-03-20T12:00:00",
  "services": {
    "mongodb": "connected"
  }
}
```

### Collection Endpoints

#### Collect from All Feeds

**POST** `/api/v1/collect`

Trigger news collection from all configured RSS feeds.

```bash
curl -X POST http://localhost:8000/api/v1/collect \
  -H "Content-Type: application/json" \
  -d '{"days_back": 1, "limit": 50}'
```

**Request Body:**
```json
{
  "days_back": 1,    // Number of days to look back (1-30)
  "limit": 50        // Maximum articles per source (1-500)
}
```

**Response:**
```json
{
  "timestamp": "2025-03-20T12:00:00",
  "start_date": "2025-03-19T12:00:00",
  "end_date": "2025-03-20T12:00:00",
  "total_fetched": 150,
  "total_saved": 45,
  "sources": {
    "yonhap_economy": {
      "fetched": 50,
      "saved": 15,
      "skipped": 35,
      "status": "success"
    },
    "maeil_management": {
      "fetched": 50,
      "saved": 18,
      "skipped": 32,
      "status": "success"
    },
    "etnews_today": {
      "fetched": 50,
      "saved": 12,
      "skipped": 38,
      "status": "success"
    }
  }
}
```

#### Collect from Specific Feed

**POST** `/api/v1/collect/{source_name}`

Collect articles from a specific RSS feed.

```bash
curl -X POST http://localhost:8000/api/v1/collect/yonhap_economy \
  -H "Content-Type: application/json" \
  -d '{"days_back": 1, "limit": 50}'
```

**Response:**
```json
{
  "source": "yonhap_economy",
  "timestamp": "2025-03-20T12:00:00",
  "start_date": "2025-03-19T12:00:00",
  "end_date": "2025-03-20T12:00:00",
  "fetched": 50,
  "saved": 15,
  "skipped": 35,
  "status": "success"
}
```

### Query Endpoints

#### Query Articles

**GET** `/api/v1/articles`

Retrieve articles with filtering and pagination.

```bash
curl "http://localhost:8000/api/v1/articles?page=1&page_size=20"
```

**Query Parameters:**
- `source` (optional): Filter by source name (e.g., "yonhap_economy")
- `start_date` (optional): Filter articles after this date (ISO format)
- `end_date` (optional): Filter articles before this date (ISO format)
- `keyword` (optional): Search in title and content
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Results per page, max 100 (default: 20)

**Examples:**
```bash
# Get recent articles
curl "http://localhost:8000/api/v1/articles"

# Filter by source
curl "http://localhost:8000/api/v1/articles?source=yonhap_economy"

# Search by keyword
curl "http://localhost:8000/api/v1/articles?keyword=AI&page=1&page_size=10"

# Date range filter
curl "http://localhost:8000/api/v1/articles?start_date=2025-03-19T00:00:00&end_date=2025-03-20T23:59:59"
```

**Response:**
```json
{
  "articles": [
    {
      "id": "507f1f77bcf86cd799439011",
      "source": "yonhap_economy",
      "url": "https://example.com/article1",
      "title": "Article Title",
      "content": "Article content...",
      "published_at": "2025-03-20T10:00:00",
      "crawled_at": "2025-03-20T10:05:00",
      "metadata": {}
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

#### Get Single Article

**GET** `/api/v1/articles/{article_id}`

Retrieve a single article by its ID.

```bash
curl http://localhost:8000/api/v1/articles/507f1f77bcf86cd799439011
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "source": "yonhap_economy",
  "url": "https://example.com/article1",
  "title": "Article Title",
  "content": "Article content...",
  "published_at": "2025-03-20T10:00:00",
  "crawled_at": "2025-03-20T10:05:00",
  "metadata": {}
}
```

### Statistics Endpoints

#### Get Overall Statistics

**GET** `/api/v1/stats`

Get aggregate statistics about the news collection.

```bash
curl http://localhost:8000/api/v1/stats
```

**Response:**
```json
{
  "total_articles": 1500,
  "total_sources": 3,
  "by_source": {
    "yonhap_economy": 500,
    "maeil_management": 600,
    "etnews_today": 400
  },
  "date_range": {
    "oldest": "2025-03-01T00:00:00",
    "newest": "2025-03-20T12:00:00"
  },
  "last_collection": "2025-03-20T12:00:00",
  "generated_at": "2025-03-20T12:05:00"
}
```

#### Get Source Statistics

**GET** `/api/v1/stats/{source_name}`

Get detailed statistics for a specific source.

```bash
curl http://localhost:8000/api/v1/stats/yonhap_economy
```

**Response:**
```json
{
  "source": "yonhap_economy",
  "feed_url": "https://www.yonhapnewstv.co.kr/category/news/economy/feed",
  "adapter_name": "yonhap",
  "total_articles": 500,
  "oldest_article": "2025-03-01T00:00:00",
  "newest_article": "2025-03-20T12:00:00"
}
```

#### Get Collection History

**GET** `/api/v1/stats/history`

Get recent collection operation history.

```bash
curl "http://localhost:8000/api/v1/stats/history?limit=20"
```

**Response:**
```json
[
  {
    "timestamp": "2025-03-20T12:00:00",
    "source": "yonhap_economy",
    "articles_collected": 15
  },
  {
    "timestamp": "2025-03-20T12:00:00",
    "source": "maeil_management",
    "articles_collected": 18
  }
]
```

## Configuration

Configure the API using environment variables:

```bash
# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=news_org
MONGO_COLLECTION=articles

# API Server
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Available Sources

The following RSS feed sources are configured:

- `yonhap_economy`: Yonhap News TV Economy
- `maeil_management`: Maeil Business Management
- `etnews_today`: ETNews Today

## Error Responses

The API uses standard HTTP status codes:

- `200 OK`: Successful request
- `404 Not Found`: Resource not found
- `422 Validation Error`: Invalid request parameters
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "status_code": 404
}
```

## Architecture

The API is built with a layered architecture:

- **Routes**: HTTP endpoint definitions
- **Models**: Request/response DTOs with Pydantic
- **Services**: Business logic layer (reusable by CLI)
- **Storage**: MongoDB data access layer

This design allows:
- Easy testing (mockable services)
- Code reuse between CLI and API
- Clear separation of concerns
- Future extensibility (auth, rate limiting, etc.)
