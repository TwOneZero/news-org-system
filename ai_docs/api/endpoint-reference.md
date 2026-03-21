# API Endpoint Reference

Complete reference for all REST API endpoints in the news-org-system.

**Base URL**: `http://localhost:8000`

**API Version**: v1

**Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

For quick start and usage examples, see @README.api.md.

---

## Health Endpoints

### GET /health

Check API and database connectivity status.

**Request**:
```bash
curl http://localhost:8000/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-03-21T12:00:00",
  "services": {
    "mongodb": "connected"
  }
}
```

**Fields**:
- `status`: "healthy" or "unhealthy"
- `timestamp`: ISO 8601 timestamp
- `services.mongodb`: "connected" or "disconnected"

---

## Collection Endpoints

### POST /api/v1/collect

Collect articles from **all** configured RSS feeds.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/collect \
  -H "Content-Type: application/json" \
  -d '{
    "days_back": 1,
    "limit": 50
  }'
```

**Request Body** (`CollectionRequest`):
```json
{
  "days_back": 1,    // Number of days to look back (1-30, default: 1)
  "limit": 50        // Maximum articles per source (1-500, default: 50)
}
```

**Parameters**:
- `days_back`: How many days back to collect (range: 1-30)
- `limit`: Maximum articles to fetch per source (range: 1-500)

**Response** (200 OK):
```json
{
  "timestamp": "2026-03-21T12:00:00",
  "start_date": "2026-03-20T12:00:00",
  "end_date": "2026-03-21T12:00:00",
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

**Response Fields**:
- `timestamp`: When collection started (ISO 8601)
- `start_date`: Start of date range (ISO 8601)
- `end_date`: End of date range (ISO 8601)
- `total_fetched`: Total articles fetched from all sources
- `total_saved`: Total new articles saved (duplicates excluded)
- `sources`: Dictionary with per-source results
  - `fetched`: Articles fetched from this source
  - `saved`: New articles saved
  - `skipped`: Duplicate articles skipped
  - `status`: "success" or "error"

**Error Responses**:
- `500 Internal Server Error`: Collection failed

---

### POST /api/v1/collect/{source_name}

Collect articles from a **specific** RSS feed.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/collect/yonhap_economy \
  -H "Content-Type: application/json" \
  -d '{
    "days_back": 1,
    "limit": 50
  }'
```

**Path Parameters**:
- `source_name`: Name of the feed source (e.g., "yonhap_economy", "maeil_management", "etnews_today")

**Request Body**: Same as `/api/v1/collect`

**Response** (200 OK):
```json
{
  "source": "yonhap_economy",
  "timestamp": "2026-03-21T12:00:00",
  "start_date": "2026-03-20T12:00:00",
  "end_date": "2026-03-21T12:00:00",
  "fetched": 50,
  "saved": 15,
  "skipped": 35,
  "status": "success"
}
```

**Error Responses**:
- `404 Not Found`: Source not found in registry
  ```json
  {
    "error": "Source 'unknown_source' not found in registry. Available sources: ['yonhap_economy', 'maeil_management', 'etnews_today']",
    "detail": "...",
    "status_code": 404
  }
  ```
- `500 Internal Server Error`: Collection failed

---

## Query Endpoints

### GET /api/v1/articles

Query articles with filtering and pagination.

**Request**:
```bash
# Get recent articles
curl "http://localhost:8000/api/v1/articles"

# Filter by source
curl "http://localhost:8000/api/v1/articles?source=yonhap_economy"

# Search by keyword
curl "http://localhost:8000/api/v1/articles?keyword=AI&page=1&page_size=10"

# Date range filter
curl "http://localhost:8000/api/v1/articles?start_date=2026-03-20T00:00:00&end_date=2026-03-21T23:59:59"
```

**Query Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `source` | string | No | Filter by source name | `yonhap_economy` |
| `start_date` | datetime | No | Filter articles after this date (ISO 8601) | `2026-03-20T00:00:00` |
| `end_date` | datetime | No | Filter articles before this date (ISO 8601) | `2026-03-21T23:59:59` |
| `keyword` | string | No | Search in title and content (case-insensitive) | `AI` |
| `page` | integer | No | Page number (1-indexed, default: 1) | `1` |
| `page_size` | integer | No | Results per page (1-100, default: 20) | `20` |

**Response** (200 OK):
```json
{
  "articles": [
    {
      "id": "507f1f77bcf86cd799439011",
      "source": "yonhap_economy",
      "url": "https://example.com/article1",
      "title": "Article Title",
      "content": "Article content...",
      "published_at": "2026-03-21T10:00:00",
      "crawled_at": "2026-03-21T10:05:00",
      "metadata": {
        "author": "John Doe",
        "tags": ["economy", "finance"],
        "summary": "Brief summary..."
      }
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

**Response Fields**:
- `articles`: Array of article objects
  - `id`: MongoDB ObjectId as string
  - `source`: Source name
  - `url`: Article URL
  - `title`: Article title
  - `content`: Article content (full text)
  - `published_at`: Publication timestamp (ISO 8601)
  - `crawled_at`: Collection timestamp (ISO 8601)
  - `metadata`: Optional metadata (author, tags, summary)
- `total`: Total matching articles
- `page`: Current page number
- `page_size`: Articles per page
- `total_pages`: Total number of pages

**Pagination**:
- Page numbers are 1-indexed (start at 1)
- If `page_size` > 100, it's automatically reduced to 100
- Response may include `warning` field if page_size was reduced

**Search Behavior**:
- `keyword`: Case-insensitive regex search in title OR content
- `start_date`/`end_date`: Inclusive range filter on `published_at`
- `source`: Exact match on source name

---

### GET /api/v1/articles/{article_id}

Get a single article by its ID.

**Request**:
```bash
curl http://localhost:8000/api/v1/articles/507f1f77bcf86cd799439011
```

**Path Parameters**:
- `article_id`: MongoDB ObjectId as string

**Response** (200 OK):
```json
{
  "id": "507f1f77bcf86cd799439011",
  "source": "yonhap_economy",
  "url": "https://example.com/article1",
  "title": "Article Title",
  "content": "Article content...",
  "published_at": "2026-03-21T10:00:00",
  "crawled_at": "2026-03-21T10:05:00",
  "metadata": {
    "author": "John Doe",
    "tags": ["economy", "finance"],
    "summary": "Brief summary..."
  }
}
```

**Error Responses**:
- `404 Not Found`: Article not found
  ```json
  {
    "error": "Article with id '507f1f77bcf86cd799439011' not found",
    "detail": "...",
    "status_code": 404
  }
  ```

---

## Statistics Endpoints

### GET /api/v1/stats

Get overall statistics about the news collection.

**Request**:
```bash
curl http://localhost:8000/api/v1/stats
```

**Response** (200 OK):
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
    "oldest": "2026-03-01T00:00:00",
    "newest": "2026-03-21T12:00:00"
  },
  "last_collection": "2026-03-21T12:00:00",
  "generated_at": "2026-03-21T12:05:00"
}
```

**Response Fields**:
- `total_articles`: Total articles in database
- `total_sources`: Number of configured sources
- `by_source`: Article count per source
- `date_range`: Oldest and newest article dates
- `last_collection`: Most recent collection timestamp
- `generated_at`: When stats were generated

---

### GET /api/v1/stats/{source_name}

Get detailed statistics for a specific source.

**Request**:
```bash
curl http://localhost:8000/api/v1/stats/yonhap_economy
```

**Path Parameters**:
- `source_name`: Name of the source

**Response** (200 OK):
```json
{
  "source": "yonhap_economy",
  "feed_url": "https://www.yonhapnewstv.co.kr/category/news/economy/feed",
  "adapter_name": "yonhap",
  "total_articles": 500,
  "oldest_article": "2026-03-01T00:00:00",
  "newest_article": "2026-03-21T12:00:00"
}
```

**Error Responses**:
- `404 Not Found`: Source not found (if queried via API, though current implementation returns null)

---

### GET /api/v1/stats/history

Get recent collection operation history.

**Request**:
```bash
curl "http://localhost:8000/api/v1/stats/history?limit=20"
```

**Query Parameters**:
- `limit`: Maximum number of history entries (default: 20)

**Response** (200 OK):
```json
[
  {
    "timestamp": "2026-03-21T12:00:00",
    "source": "yonhap_economy",
    "articles_collected": 15
  },
  {
    "timestamp": "2026-03-21T12:00:00",
    "source": "maeil_management",
    "articles_collected": 18
  },
  {
    "timestamp": "2026-03-21T12:00:00",
    "source": "etnews_today",
    "articles_collected": 12
  }
]
```

**Response Fields**:
- `timestamp`: When collection occurred
- `source`: Source name
- `articles_collected`: Number of new articles collected

**Note**: History is derived from article `crawled_at` timestamps. For production, consider storing collection operations in a separate collection.

---

## Error Handling

### Standard Error Response Format

All error responses follow this format:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "status_code": 404
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| `200 OK` | Request succeeded |
| `404 Not Found` | Resource not found (article, source) |
| `422 Unprocessable Entity` | Validation error (invalid parameters) |
| `500 Internal Server Error` | Server error |

### Common Errors

**Validation Error** (422):
```json
{
  "error": "Validation error",
  "detail": [
    {
      "loc": ["body", "days_back"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ],
  "status_code": 422
}
```

**Source Not Found** (404):
```json
{
  "error": "Source 'unknown_source' not found in registry. Available sources: ['yonhap_economy', 'maeil_management', 'etnews_today']",
  "detail": "...",
  "status_code": 404
}
```

**Internal Server Error** (500):
```json
{
  "error": "Internal server error",
  "detail": "Connection to MongoDB failed",
  "status_code": 500
}
```

---

## Available Sources

The following RSS feed sources are configured:

| Source Name | Description | Feed URL | Adapter |
|-------------|-------------|----------|---------|
| `yonhap_economy` | Yonhap News TV Economy | https://www.yonhapnewstv.co.kr/category/news/economy/feed | yonhap |
| `maeil_management` | Maeil Business Management | https://www.mk.co.kr/rss/50100032/ | maeil |
| `etnews_today` | ETNews Today | https://rss.etnews.com/Section901.xml | etnews |

**Note**: See @ai_docs/development/adding-sources.md for adding new sources.

---

## Authentication

**Current Status**: No authentication required.

**Future Plans**: API key authentication may be added. Check @ai_docs/architecture/design-decisions.md for authentication decisions.

---

## Rate Limiting

**Current Status**: No rate limiting.

**Future Plans**: Rate limiting may be added for public API deployment.

---

## CORS

The API supports CORS (Cross-Origin Resource Sharing).

**Default Allowed Origins**:
- `http://localhost:3000`
- `http://localhost:8000`

**Configuration**:
```bash
# Set via environment variable
CORS_ORIGINS=http://example.com,https://example.com
```

---

## SDK / Client Libraries

**Current Status**: No official SDK available.

**Using with cURL**: See examples above

**Using with Python (requests)**:
```python
import requests

# Collect articles
response = requests.post(
    "http://localhost:8000/api/v1/collect",
    json={"days_back": 1, "limit": 50}
)
print(response.json())

# Query articles
response = requests.get(
    "http://localhost:8000/api/v1/articles",
    params={"source": "yonhap_economy", "page_size": 10}
)
print(response.json())
```

**Using with JavaScript (fetch)**:
```javascript
// Collect articles
const response = await fetch('http://localhost:8000/api/v1/collect', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({days_back: 1, limit: 50})
});
const data = await response.json();
console.log(data);

// Query articles
const response = await fetch(
  'http://localhost:8000/api/v1/articles?source=yonhap_economy&page_size=10'
);
const data = await response.json();
console.log(data);
```

---

## Pagination Strategy

**Current Implementation**: Offset-based pagination

- Use `page` and `page_size` parameters
- `page` is 1-indexed (start at 1)
- Calculate skip offset: `skip = (page - 1) * page_size`

**Limitations**:
- If data changes during pagination, results may shift
- For large datasets, cursor-based pagination is more efficient

**Future**: May migrate to cursor-based pagination using MongoDB `_id` (see @ai_docs/architecture/design-decisions.md)

---

## OpenAPI Documentation

The API auto-generates OpenAPI 3.0 specification.

**Access**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

**Features**:
- Interactive API exploration
- Request/response schemas
- Try-it-out functionality
- Code examples for multiple languages

---

## Versioning

**Current Version**: v1

**Versioning Strategy**: URL-based versioning (`/api/v1/`)

**Future Versions**:
- v2 may include breaking changes
- v1 will remain supported for backward compatibility

---

## Testing Endpoints

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on an endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. View response

### Using cURL

See examples in each endpoint section above.

### Using Python

```python
import requests

base_url = "http://localhost:8000"

# Health check
response = requests.get(f"{base_url}/health")
print(response.json())

# Collect articles
response = requests.post(
    f"{base_url}/api/v1/collect",
    json={"days_back": 1, "limit": 50}
)
print(response.json())

# Query articles
response = requests.get(
    f"{base_url}/api/v1/articles",
    params={"page": 1, "page_size": 10}
)
print(response.json())
```

---

## Integration Examples

### Periodic Collection

```python
import requests
import schedule
import time

def collect_news():
    """Collect news every hour."""
    response = requests.post(
        "http://localhost:8000/api/v1/collect",
        json={"days_back": 1, "limit": 100}
    )
    print(f"Collected {response.json()['total_saved']} new articles")

# Run every hour
schedule.every().hour.do(collect_news)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Monitor New Articles

```python
import requests
import time

def monitor_new_articles(source="yonhap_economy", interval=60):
    """Monitor for new articles from a source."""
    last_count = 0

    while True:
        # Get current stats
        response = requests.get(
            f"http://localhost:8000/api/v1/stats/{source}"
        )
        stats = response.json()
        current_count = stats['total_articles']

        # Check for new articles
        if current_count > last_count:
            new_articles = current_count - last_count
            print(f"🎉 {new_articles} new articles from {source}")
            last_count = current_count

        time.sleep(interval)

monitor_new_articles()
```

### Search and Alert

```python
import requests

def search_and_alert(keyword, source=None):
    """Search articles and alert if matches found."""
    params = {"keyword": keyword, "page_size": 20}
    if source:
        params["source"] = source

    response = requests.get(
        "http://localhost:8000/api/v1/articles",
        params=params
    )
    data = response.json()

    if data["total"] > 0:
        print(f"🚨 Found {data['total']} articles matching '{keyword}'")
        for article in data["articles"][:5]:
            print(f"  - {article['title']}")
            print(f"    {article['url']}")
    else:
        print(f"✅ No articles found matching '{keyword}'")

search_and_alert("AI", "yonhap_economy")
```
