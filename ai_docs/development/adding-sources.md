# Adding New RSS Sources

This guide explains how to add new RSS feed sources to the news-org-system, including feed configuration and adapter creation.

## Overview

Adding a new RSS source involves:

1. **Understand the feed structure** - Check if it uses standard RSS format
2. **Choose or create an adapter** - Use existing adapter or create custom one
3. **Configure the feed** - Add to feed registry
4. **Test the integration** - Verify collection works

## Quick Start: Adding a Standard RSS Feed

If the site follows standard RSS/Atom format (most do), you can use the `default` adapter:

### Step 1: Test the Feed URL

```python
import feedparser

# Test if feed is accessible
url = "https://example.com/news/rss.xml"
feed = feedparser.parse(url)

print(f"Feed title: {feed.feed.get('title')}")
print(f"Number of entries: {len(feed.entries)}")
print(f"First entry: {feed.entries[0].get('title')}")
```

### Step 2: Add to Feed Registry

Edit `src/news_org_system/readers/registry.py`:

```python
from .models.rss_config import RSSFeedConfig

FEED_REGISTRY = {
    # ... existing feeds ...

    "example_news": RSSFeedConfig(
        source_name="example_news",
        feed_url="https://example.com/news/rss.xml",
        adapter_name="default",  # Use default adapter for standard RSS
        language="en",
    ),
}
```

### Step 3: Test Collection

```bash
# CLI
news-org collect --source example_news --limit 5

# API
curl -X POST http://localhost:8000/api/v1/collect/example_news \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'
```

That's it! The `default` adapter handles:
- Standard RSS content extraction
- Date parsing
- Metadata extraction
- Fallback to web scraping if needed

## Understanding Feed Registries

### Feed Registry (`FEED_REGISTRY`)

Maps **source names** to **feed configurations**:

```python
FEED_REGISTRY: Dict[str, RSSFeedConfig] = {
    "source_name": RSSFeedConfig(
        source_name="source_name",
        feed_url="https://...",
        adapter_name="adapter_name",
        language="ko",
    )
}
```

**Purpose**: Centralized configuration for all RSS feeds.

### Adapter Registry (`ADAPTER_REGISTRY`)

Maps **adapter names** to **adapter classes**:

```python
ADAPTER_REGISTRY: Dict[str, Type[BaseRSSAdapter]] = {
    "default": DefaultRSSAdapter,
    "yonhap": YonhapAdapter,
    "maeil": MaeliAdapter,
}
```

**Purpose**: Maps string names to actual adapter classes.

### How They Work Together

```python
# 1. User specifies source name
source_name = "example_news"

# 2. Get feed config from FEED_REGISTRY
config = FEED_REGISTRY[source_name]
# config.adapter_name == "default"

# 3. Get adapter class from ADAPTER_REGISTRY
adapter_class = ADAPTER_REGISTRY[config.adapter_name]
# adapter_class == DefaultRSSAdapter

# 4. Instantiate adapter with site config
adapter = adapter_class(SiteConfig(language=config.language))

# 5. Use adapter to parse feed entries
content = adapter.extract_content(entry)
```

## RSSFeedConfig Fields

```python
class RSSFeedConfig(BaseModel):
    source_name: str      # Unique identifier (alphanumeric + underscores)
    feed_url: HttpUrl     # RSS/Atom feed URL
    adapter_name: str = "default"  # Adapter to use
    enabled: bool = True  # Whether feed is active
    language: str = "ko"  # Content language (ko, en, ja, etc.)
```

### Field Details

#### `source_name`
- **Purpose**: Unique identifier for this feed
- **Format**: Alphanumeric with underscores only (e.g., `example_news`, `tech_crunch`)
- **Used in**:
  - API endpoints: `POST /api/v1/collect/{source_name}`
  - CLI commands: `news-org collect --source {source_name}`
  - Database queries: Filter by source

#### `feed_url`
- **Purpose**: URL of the RSS/Atom feed
- **Format**: Valid HTTP/HTTPS URL
- **Validation**: Automatically validated by Pydantic

#### `adapter_name`
- **Purpose**: Which adapter to use for parsing
- **Default**: `"default"` (works for most feeds)
- **Options**: `"default"`, `"yonhap"`, `"maeil"`, `"etnews"`, or custom adapters
- **How to choose**: See "Choosing or Creating Adapters" below

#### `language`
- **Purpose**: Content language for processing
- **Common values**: `"ko"` (Korean), `"en"` (English), `"ja"` (Japanese)
- **Impact**: Affects NLP processing if enabled

#### `enabled`
- **Purpose**: Toggle feed on/off without deleting configuration
- **Use case**: Temporarily disable problematic feeds
- **Default**: `True`

## Choosing or Creating Adapters

### Decision Tree

```
Does the feed follow standard RSS/Atom format?
├─ Yes → Use "default" adapter ✅
└─ No
   ├─ Is content in non-standard field?
   │  → Create custom adapter, override extract_content()
   ├─ Are dates in non-standard format?
   │  → Create custom adapter, override parse_date()
   └─ Site requires special handling?
      → Create custom adapter, override multiple methods
```

### Using Existing Adapters

**Available Adapters**:
- **`default`**: Standard RSS/Atom feeds (95% of cases)
- **`yonhap`**: Yonhap News (inherits default)
- **`maeil`**: Maeil Business (inherits default)
- **`etnews`**: ETNews (inherits default)

Most site-specific adapters (Yonhap, Maeli, ETnews) currently inherit from `DefaultRSSAdapter` because these sites follow standard RSS format. They're ready for custom logic if needed in the future.

### When to Create a Custom Adapter

Create a custom adapter when:

1. **Content extraction fails**: Default adapter returns empty/short content
2. **Date parsing fails**: Dates are in non-standard format
3. **Site-specific metadata**: Need to extract custom fields
4. **Anti-scraping**: Site blocks scrapers, need custom handling

**Don't create** if:
- Default adapter works fine
- Only changing URL or source name (use registry instead)

## Creating a Custom Adapter

### Example: Custom Content Field

**Scenario**: Site uses `<custom_content>` field instead of standard fields.

```python
# src/news_org_system/readers/adapters/mysite_adapter.py

from .default_adapter import DefaultRSSAdapter

class MysiteAdapter(DefaultRSSAdapter):
    """Adapter for mysite.com with custom content field."""

    def extract_content(self, entry) -> str:
        """Extract from custom field, fall back to default."""
        # Try custom field first
        if hasattr(entry, "custom_content"):
            return entry.custom_content

        # Fall back to default behavior
        return super().extract_content(entry)
```

### Example: Custom Date Format

**Scenario**: Site uses string date like "2024-03-20 14:30:00".

```python
from datetime import datetime
from .default_adapter import DefaultRSSAdapter

class MysiteAdapter(DefaultRSSAdapter):
    """Adapter for mysite.com with custom date format."""

    def parse_date(self, entry) -> datetime:
        """Parse custom date string format."""
        if hasattr(entry, "custom_date_str"):
            try:
                return datetime.strptime(
                    entry.custom_date_str,
                    "%Y-%m-%d %H:%M:%S"
                )
            except (ValueError, TypeError):
                pass  # Fall back to default

        # Fall back to default behavior
        return super().parse_date(entry)
```

### Example: Custom Metadata

```python
from typing import Dict
from feedparser import FeedParserDict
from .default_adapter import DefaultRSSAdapter

class MysiteAdapter(DefaultRSSAdapter):
    """Adapter for mysite.com with custom metadata."""

    def get_metadata(self, entry: FeedParserDict) -> Dict:
        """Extract custom metadata fields."""
        # Get base metadata
        metadata = super().get_metadata(entry)

        # Add custom fields
        metadata["category"] = entry.get("mysite_category", "")
        metadata["author_url"] = entry.get("author_link", "")
        metadata["views"] = entry.get("view_count", 0)

        return metadata
```

### Registering the Adapter

**Step 1**: Import in `adapters/__init__.py`

```python
# src/news_org_system/readers/adapters/__init__.py

from .mysite_adapter import MysiteAdapter

__all__ = [
    "BaseRSSAdapter",
    "DefaultRSSAdapter",
    "YonhapAdapter",
    "MaeliAdapter",
    "ETnewsAdapter",
    "MysiteAdapter",  # Add here
]
```

**Step 2**: Register in `adapters/registry.py`

```python
# src/news_org_system/readers/adapters/registry.py (if separate)
# OR in readers/registry.py

ADAPTER_REGISTRY = {
    "default": DefaultRSSAdapter,
    "yonhap": YonhapAdapter,
    "maeil": MaeliAdapter,
    "etnews": ETnewsAdapter,
    "mysite": MysiteAdapter,  # Add here
}
```

**Step 3**: Use in feed config

```python
FEED_REGISTRY["mysite_news"] = RSSFeedConfig(
    source_name="mysite_news",
    feed_url="https://mysite.com/news/rss.xml",
    adapter_name="mysite",  # Use your custom adapter
    language="en",
)
```

See @ai_docs/architecture/adapter-pattern.md for complete adapter development guide.

## Dynamic Registration (Runtime)

You can also register feeds programmatically at runtime:

```python
from news_org_system.readers.registry import register_feed, register_adapter
from news_org_system.readers.models.rss_config import RSSFeedConfig

# Register adapter dynamically
register_adapter("my_custom", MyCustomAdapter)

# Register feed dynamically
config = RSSFeedConfig(
    source_name="dynamic_source",
    feed_url="https://example.com/rss.xml",
    adapter_name="my_custom",
    language="en"
)
register_feed(config)
```

**Use cases**:
- User-defined feeds (from database, config file)
- Admin interface for adding feeds
- Plugin system for extensions

## Testing Your New Source

### Unit Test

```python
import pytest
from feedparser import FeedParserDict
from news_org_system.readers import RSSReader

def test_new_source_collection():
    """Test collecting from new source."""
    reader = RSSReader.from_source("example_news")

    # Fetch with limit
    articles = reader.fetch(limit=5)

    # Assertions
    assert len(articles) > 0
    for article in articles:
        assert article.title
        assert article.url
        assert article.content
        assert article.published_at
        assert article.source == "example_news"
```

### Integration Test (API)

```bash
# Test collection endpoint
curl -X POST http://localhost:8000/api/v1/collect/example_news \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'

# Expected response:
{
  "source": "example_news",
  "fetched": 5,
  "saved": 5,
  "skipped": 0,
  "status": "success"
}
```

### Integration Test (CLI)

```bash
# Test CLI collection
news-org collect --source example_news --limit 5

# Verify in database
news-org stats
```

## Common Pitfalls

### 1. Feed URL is Not Valid XML

**Problem**: URL returns HTML, not RSS.

**Symptoms**: `feedparser.parse()` returns 0 entries.

**Solution**:
```python
import feedparser
import requests

url = "https://example.com/news"

# Try common RSS paths
rss_paths = ["/rss.xml", "/feed", "/atom.xml", "/rss"]

for path in rss_paths:
    rss_url = url + path
    response = requests.head(rss_url)
    if response.status_code == 200:
        print(f"Found RSS: {rss_url}")
        break
```

### 2. Content Extraction Fails

**Problem**: Articles have empty or very short content.

**Symptoms**: `article.content` is empty or < 100 chars.

**Debugging**:
```python
from news_org_system.readers import RSSReader

reader = RSSReader.from_source("example_news")
articles = reader.fetch(limit=1)

article = articles[0]
print(f"Content length: {len(article.content)}")
print(f"Content preview: {article.content[:200]}")
```

**Solutions**:
1. Check if feed has `content:encoded` field
2. Check if `summary`/`description` is long enough
3. If web scraping fails, site may block scrapers
4. Create custom adapter for site-specific extraction

### 3. Date Parsing Returns Current Time

**Problem**: All articles have `published_at` = now.

**Symptoms**: Date is always current time.

**Solution**:
```python
import feedparser

url = "https://example.com/rss.xml"
feed = feedparser.parse(url)

entry = feed.entries[0]
print(f"Published: {entry.get('published')}")
print(f"Published parsed: {entry.get('published_parsed')}")
print(f"Updated: {entry.get('updated')}")
print(f"Updated parsed: {entry.get('updated_parsed')}")

# If missing, feed has no dates - create custom adapter
```

### 4. Feed Has No Entries

**Problem**: `feed.entries` is empty.

**Symptoms**: `len(feed.entries) == 0`

**Debugging**:
```python
import feedparser

feed = feedparser.parse(url)

print(f"Feed title: {feed.feed.get('title')}")
print(f"Entries: {len(feed.entries)}")
print(f"Feedparser status: {feed.get('status')}")  # HTTP status
print(f"Bozo exception: {feed.get('bozo_exception')}")  # Parsing errors
```

**Solutions**:
- Check URL is accessible (status 200)
- Check feed is valid XML (not HTML)
- Try different URL (some sites have multiple RSS feeds)

### 5. Source Name Already Exists

**Problem**: `ValueError: source_name already in registry`

**Solution**:
```python
# Check existing sources
from news_org_system.readers.registry import list_feeds

feeds = list_feeds()
print(list(feeds.keys()))
# ['yonhap_economy', 'maeil_management', 'etnews_today']

# Use unique name
FEED_REGISTRY["example_news_unique"] = RSSFeedConfig(...)
```

## Best Practices

### 1. **Test Before Committing**

Always test with actual feed data before adding to registry:

```python
# Quick test
from news_org_system.readers import RSSReader

reader = RSSReader.from_source("example_news")
articles = reader.fetch(limit=1)

if articles:
    print(f"✅ Feed works: {articles[0].title}")
else:
    print("❌ Feed returned no articles")
```

### 2. **Use Descriptive Source Names**

```python
# Good
"tech_crunch_ai"
"bbc_technology"
"reuters_business"

# Bad
"feed1"
"test"
"source"
```

### 3. **Set Language Correctly**

```python
# Korean feeds
RSSFeedConfig(..., language="ko")

# English feeds
RSSFeedConfig(..., language="en")

# Important for future NLP features
```

### 4. **Document Non-Standard Feeds**

If feed requires custom adapter, document why:

```python
FEED_REGISTRY["example_custom"] = RSSFeedConfig(
    source_name="example_custom",
    feed_url="https://example.com/rss.xml",
    adapter_name="example_custom",  # Custom adapter needed
    language="en",
)

# Add comment explaining why
# Custom adapter required: Site uses non-standard <content> field
```

### 5. **Handle Rate Limiting**

Some sites rate-limit RSS requests. Configure delays:

```python
# In service layer, add delays between sources
import time

for source_name in sources:
    service.collect_from_source(source_name)
    time.sleep(1)  # 1 second delay
```

## Complete Example

Here's a complete example of adding a new source with custom adapter:

### 1. Create Adapter

```python
# src/news_org_system/readers/adapters/techcrunch_adapter.py

from .default_adapter import DefaultRSSAdapter

class TechCrunchAdapter(DefaultRSSAdapter):
    """TechCrunch adapter with custom metadata extraction."""

    def get_metadata(self, entry) -> dict:
        """Extract TechCrunch-specific metadata."""
        metadata = super().get_metadata(entry)

        # TechCrunch uses 'tags' field extensively
        if hasattr(entry, 'tags'):
            metadata['categories'] = [tag.term for tag in entry.tags]

        return metadata
```

### 2. Register Adapter

```python
# src/news_org_system/readers/registry.py

from .adapters.techcrunch_adapter import TechCrunchAdapter

ADAPTER_REGISTRY = {
    # ... existing ...
    "techcrunch": TechCrunchAdapter,
}
```

### 3. Add Feed Configuration

```python
# src/news_org_system/readers/registry.py

FEED_REGISTRY["techcrunch_ai"] = RSSFeedConfig(
    source_name="techcrunch_ai",
    feed_url="https://techcrunch.com/category/artificial-intelligence/feed/",
    adapter_name="techcrunch",
    language="en",
)
```

### 4. Test

```python
from news_org_system.readers import RSSReader

reader = RSSReader.from_source("techcrunch_ai")
articles = reader.fetch(limit=3)

for article in articles:
    print(f"Title: {article.title}")
    print(f"Categories: {article.metadata.get('categories', [])}")
    print("---")
```
