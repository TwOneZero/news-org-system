"""Data readers for various news sources."""

from .base_reader import BaseReader, Article
from .rss_reader import RSSReader

# Constants module
from .constants import SourceName, AdapterName

# New adapter pattern exports
from .models import RSSFeedConfig, RSSItem, SiteConfig
from .adapters import BaseRSSAdapter, DefaultRSSAdapter
from .registry import (
    get_adapter,
    get_feed_config,
    register_adapter,
    register_feed,
    list_feeds,
    list_adapters,
    FEED_REGISTRY,
)

__all__ = [
    # Core readers
    "BaseReader",
    "Article",
    "RSSReader",
    # Constants
    "SourceName",
    "AdapterName",
    # Pydantic models
    "RSSFeedConfig",
    "RSSItem",
    "SiteConfig",
    # Adapters
    "BaseRSSAdapter",
    "DefaultRSSAdapter",
    # Registry
    "get_adapter",
    "get_feed_config",
    "register_adapter",
    "register_feed",
    "list_feeds",
    "list_adapters",
    "FEED_REGISTRY",
]
