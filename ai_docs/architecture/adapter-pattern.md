# Adapter Pattern for RSS Feed Parsing

The news-org-system uses the **Adapter pattern** to handle site-specific RSS feed parsing. This design enables flexible extensibility when adding new news sources with unique RSS structures.

## Overview

### Problem
Different news sites have varying RSS feed structures:
- Some use standard RSS/Atom format
- Some have custom content fields
- Some require special date parsing
- Some need web scraping for full content

### Solution
**Adapter pattern**: Create site-specific adapters that implement a common interface (`BaseRSSAdapter`).

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     RSSReader                           │
│  - Manages feed fetching                                │
│  - Delegates parsing to adapter                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ uses
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 BaseRSSAdapter                          │
│  - Abstract interface                                   │
│  - extract_content() (abstract)                         │
│  - parse_date() (abstract)                              │
│  - get_metadata() (default implementation)              │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ inherited by
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Default    │  │   Yonhap     │  │   Maeli      │
│   Adapter    │  │   Adapter    │  │   Adapter    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## BaseRSSAdapter Interface

**Location**: `src/news_org_system/readers/adapters/base.py`

```python
class BaseRSSAdapter(ABC):
    """Abstract base class for RSS feed parsers."""

    def __init__(self, config: SiteConfig):
        """Initialize adapter with site configuration."""
        self.config = config

    @abstractmethod
    def extract_content(self, entry: FeedParserDict) -> str:
        """Extract article content from feed entry."""
        pass

    @abstractmethod
    def parse_date(self, entry: FeedParserDict) -> datetime:
        """Parse publication date from feed entry."""
        pass

    def get_metadata(self, entry: FeedParserDict) -> Dict:
        """Extract metadata from feed entry (default implementation)."""
        return {
            "author": entry.get("author", ""),
            "tags": [tag.term for tag in entry.get("tags", [])],
            "summary": entry.get("summary", ""),
        }
```

### Key Methods

#### `extract_content(entry)`
Extract article text from feed entry with multi-stage fallback:
1. **content:encoded tag** - Highest quality, full content from RSS
2. **summary/description tag** - Fallback RSS fields
3. **Web scraping** - Last resort using newspaper4k

#### `parse_date(entry)`
Parse publication date from feed entry:
- Tries `published_parsed`, `updated_parsed` fields
- Falls back to current time if no date found

#### `get_metadata(entry)` (Optional Override)
Extract metadata like author, tags, summary. Default implementation handles common fields.

## DefaultRSSAdapter

**Location**: `src/news_org_system/readers/adapters/default_adapter.py`

### Purpose
Handles standard RSS/Atom feeds with generic content extraction. Works for most news sites following RSS specifications.

### Content Extraction Strategy

```python
def extract_content(self, entry) -> str:
    """Multi-stage fallback strategy."""

    # 1. Try content:encoded (highest quality)
    if hasattr(entry, "content") and entry.content:
        return strip_html(entry.content[0].value)

    # 2. Try summary/description if long enough
    rss_content = entry.summary or entry.description
    if len(strip_html(rss_content)) >= min_content_length:
        return strip_html(rss_content)

    # 3. Web scraping as last resort
    article = NewspaperArticle(url)
    article.download()
    article.parse()
    return article.text
```

### Date Parsing

```python
def parse_date(self, entry) -> datetime:
    """Try various date fields in order."""
    for field in ["published_parsed", "updated_parsed"]:
        if hasattr(entry, field) and getattr(entry, field):
            time_struct = getattr(entry, field)
            return datetime(*time_struct[:6])
    return datetime.now()  # Fallback
```

### HTML Stripping

Uses BeautifulSoup to remove HTML tags while preserving text:
```python
def _strip_html(self, html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)
```

## Site-Specific Adapters

### YonhapAdapter

**Location**: `src/news_org_system/readers/adapters/yonhap_adapter.py`

```python
class YonhapAdapter(DefaultRSSAdapter):
    """Yonhap News RSS adapter.

    Currently inherits default behavior as Yonhap follows
    standard RSS format. Can be extended with Yonhap-specific
    logic if needed.
    """
    pass  # Inherits all DefaultRSSAdapter methods
```

**When to Extend**:
- If Yonhap changes RSS format
- If custom content extraction needed
- If date parsing differs

### MaeliAdapter

**Location**: `src/news_org_system/readers/adapters/maeil_adapter.py`

Similar structure - can override specific methods as needed.

### ETnewsAdapter

**Location**: `src/news_org_system/readers/adapters/etnews_adapter.py`

Similar structure - can override specific methods as needed.

## Adapter Registration

Adapters are registered in `readers/registry.py`:

```python
from ..adapters.default_adapter import DefaultRSSAdapter
from ..adapters.yonhap_adapter import YonhapAdapter
from ..adapters.maeil_adapter import MaeliAdapter
from ..adapters.etnews_adapter import ETnewsAdapter

ADAPTER_REGISTRY = {
    "default": DefaultRSSAdapter,
    "yonhap": YonhapAdapter,
    "maeil": MaeliAdapter,
    "etnews": ETnewsAdapter,
}
```

## Feed Registry Configuration

Feeds are configured with their adapters in `readers/registry.py`:

```python
FEED_REGISTRY = {
    "yonhap_economy": RSSFeedConfig(
        source_name="yonhap_economy",
        feed_url="https://www.yonhapnewstv.co.kr/category/news/economy/feed",
        adapter_name="yonhap",  # Maps to ADAPTER_REGISTRY
        language="ko",
    ),
    "maeil_management": RSSFeedConfig(
        source_name="maeil_management",
        feed_url="https://news.mbn.co.kr/management/rss/",
        adapter_name="maeil",
        language="ko",
    ),
}
```

## Creating a Custom Adapter

### Step 1: Create Adapter Class

```python
# src/news_org_system/readers/adapters/mysite_adapter.py

from .default_adapter import DefaultRSSAdapter
from datetime import datetime

class MysiteAdapter(DefaultRSSAdapter):
    """Custom adapter for mysite.com."""

    def extract_content(self, entry) -> str:
        """Custom content extraction for mysite.com."""
        # Example: Extract from custom field
        if hasattr(entry, "mysite_content"):
            return entry.mysite_content

        # Fall back to default behavior
        return super().extract_content(entry)

    def parse_date(self, entry) -> datetime:
        """Custom date parsing for mysite.com."""
        # Example: Parse custom date format
        if hasattr(entry, "custom_date"):
            return datetime.strptime(entry.custom_date, "%Y-%m-%d")

        # Fall back to default behavior
        return super().parse_date(entry)
```

### Step 2: Register Adapter

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

```python
# src/news_org_system/readers/adapters/registry.py (or where ADAPTER_REGISTRY is)

ADAPTER_REGISTRY = {
    "default": DefaultRSSAdapter,
    "yonhap": YonhapAdapter,
    "maeil": MaeliAdapter,
    "etnews": ETnewsAdapter,
    "mysite": MysiteAdapter,  # Add here
}
```

### Step 3: Configure Feed

```python
# src/news_org_system/readers/registry.py

FEED_REGISTRY["mysite_news"] = RSSFeedConfig(
    source_name="mysite_news",
    feed_url="https://mysite.com/news/rss.xml",
    adapter_name="mysite",  # Points to your adapter
    language="en",
)
```

### Step 4: Test

```python
from news_org_system.readers import RSSReader

# Test with your new source
reader = RSSReader.from_source("mysite_news")
articles = reader.fetch(limit=5)

for article in articles:
    print(f"Title: {article.title}")
    print(f"Content: {article.content[:100]}...")
    print(f"Date: {article.published_at}")
    print("---")
```

## Common Adapter Customizations

### Custom Content Extraction

**Scenario**: Site uses non-standard content field.

```python
def extract_content(self, entry) -> str:
    # Try custom field first
    if hasattr(entry, "custom_content_field"):
        return entry.custom_content_field

    # Fall back to default
    return super().extract_content(entry)
```

### Custom Date Parsing

**Scenario**: Site uses non-standard date format.

```python
def parse_date(self, entry) -> datetime:
    # Parse custom date string
    if hasattr(entry, "custom_date_string"):
        return datetime.strptime(
            entry.custom_date_string,
            "%Y-%m-%d %H:%M:%S"
        )

    # Fall back to default
    return super().parse_date(entry)
```

### Custom Metadata Extraction

**Scenario**: Site has site-specific metadata.

```python
def get_metadata(self, entry) -> Dict:
    """Get base metadata and add site-specific fields."""
    metadata = super().get_metadata(entry)

    # Add custom fields
    metadata["category"] = entry.get("mysite_category", "")
    metadata["author_url"] = entry.get("author_link", "")

    return metadata
```

### Disabling Web Scraping

**Scenario**: Site blocks scrapers, RSS-only mode.

```python
def extract_content(self, entry) -> str:
    """Only use RSS content, no web scraping."""
    # Try RSS fields only
    if hasattr(entry, "content") and entry.content:
        return strip_html(entry.content[0].value)

    if hasattr(entry, "summary"):
        return strip_html(entry.summary)

    # Return empty string instead of scraping
    return ""
```

## Edge Cases and Error Handling

### Missing Content

**Problem**: Entry has no content field.

**Solution**:
```python
# DefaultRSSAdapter handles this gracefully
def extract_content(self, entry) -> str:
    # Returns empty string if all methods fail
    return ""  # Better than crashing
```

### Invalid Date

**Problem**: Date field is malformed.

**Solution**:
```python
# DefaultRSSAdapter falls back to current time
def parse_date(self, entry) -> datetime:
    try:
        # Parse date...
        return parsed_date
    except (ValueError, TypeError):
        return datetime.now()  # Safe fallback
```

### Web Scraping Failures

**Problem**: newspaper4k fails to extract content.

**Solution**:
```python
# DefaultRSSAdapter catches exceptions
try:
    article.download()
    article.parse()
    return article.text
except Exception as e:
    print(f"Scraping failed: {e}")
    return ""  # Fall back to RSS content
```

### HTML in Content

**Problem**: RSS content contains HTML tags.

**Solution**:
```python
# DefaultRSSAdapter strips HTML with BeautifulSoup
def _strip_html(self, html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)
```

## Best Practices

### 1. **Inherit from DefaultRSSAdapter**
Don't start from `BaseRSSAdapter` unless you need completely different logic. `DefaultRSSAdapter` has robust fallback strategies.

### 2. **Override Only What's Needed**
If content extraction works but dates don't, only override `parse_date()`.

### 3. **Call super() for Fallbacks**
Let parent class handle cases you don't specifically customize.

```python
def extract_content(self, entry) -> str:
    # Custom logic
    if custom_condition:
        return custom_extraction(entry)

    # Fall back to default
    return super().extract_content(entry)
```

### 4. **Log Custom Behavior**
Help with debugging by logging when custom logic is used.

```python
import logging
logger = logging.getLogger(__name__)

def extract_content(self, entry) -> str:
    if custom_field:
        logger.debug(f"Using custom extraction for {entry.get('link')}")
        return custom_field
    return super().extract_content(entry)
```

### 5. **Test with Real Data**
Test your adapter with actual RSS feed entries, not just examples.

```python
# Test with real feed
import feedparser

feed = feedparser.parse("https://mysite.com/rss.xml")
entry = feed.entries[0]

adapter = MysiteAdapter(config)
content = adapter.extract_content(entry)
print(f"Extracted: {len(content)} chars")
```

## Testing Adapters

### Unit Test Example

```python
import pytest
from feedparser import FeedParserDict
from news_org_system.readers.adapters.mysite_adapter import MysiteAdapter

def test_mysite_adapter_custom_content():
    """Test custom content extraction."""
    config = SiteConfig(language="en")
    adapter = MysiteAdapter(config)

    # Mock entry with custom field
    entry = FeedParserDict()
    entry.mysite_content = "Custom content here"

    content = adapter.extract_content(entry)
    assert content == "Custom content here"

def test_mysite_adapter_fallback():
    """Test fallback to default behavior."""
    config = SiteConfig(language="en")
    adapter = MysiteAdapter(config)

    # Mock entry without custom field
    entry = FeedParserDict()
    entry.summary = "Summary here"

    content = adapter.extract_content(entry)
    assert "Summary" in content
```

## When to Create a New Adapter

Create a new adapter when:

1. ✅ **Non-standard content field**: Site uses custom field for article content
2. ✅ **Special date format**: Date parsing requires custom logic
3. ✅ **Site-specific metadata**: Unique metadata fields to extract
4. ✅ **Anti-scraping measures**: Need custom handling for blocked sites
5. ✅ **Language-specific parsing**: Needs special NLP or tokenization

**Don't create** a new adapter if:
- ❌ DefaultRSSAdapter already works
- ❌ Only configuration changes (e.g., different URL)
- ❌ Just to add a feed (use registry instead)
