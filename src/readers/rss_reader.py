"""RSS feed reader using adapter pattern for flexible site-specific parsing."""

import feedparser
from datetime import datetime
from typing import List, Optional

from .base_reader import BaseReader, Article
from .registry import FEED_REGISTRY, get_adapter, get_feed_config
from .models.site_config import SiteConfig


class RSSReader(BaseReader):
    """Reader for RSS/Atom news feeds using adapter pattern.

    This reader supports multiple news sources through site-specific adapters,
    making it easy to add new sources without modifying core logic.

    Example:
        >>> # Using predefined feed from registry
        >>> reader = RSSReader.from_source("yonhap_economy")
        >>> articles = reader.fetch(limit=10)

        >>> # Using custom feed URL
        >>> reader = RSSReader(
        ...     source_name="custom",
        ...     feed_url="https://example.com/rss.xml"
        ... )
        >>> articles = reader.fetch(limit=10)
    """

    # Keep for backward compatibility (deprecated - use registry instead)
    FEED_URLS = {
        "yonhap_economy": "https://www.yonhapnewstv.co.kr/category/news/economy/feed",
        "maeil_management": "https://www.mk.co.kr/rss/50100032/",
        "etnews_today": "https://rss.etnews.com/Section901.xml",
    }

    def __init__(
        self,
        source_name: str = "rss",
        feed_url: Optional[str] = None,
        adapter_name: str = "default",
        site_config: Optional[SiteConfig] = None,
    ):
        """Initialize the RSS reader.

        Args:
            source_name: Name identifier for this source
            feed_url: Custom RSS feed URL (if not using predefined feeds)
            adapter_name: Name of the adapter to use for parsing
            site_config: Site-specific configuration for content extraction
        """
        super().__init__(source_name)
        self.feed_url = feed_url
        self.adapter_name = adapter_name
        self.site_config = site_config or SiteConfig()

    @classmethod
    def from_source(cls, source_name: str) -> "RSSReader":
        """Create RSSReader from a registered source name.

        Args:
            source_name: Name of registered news source (e.g., 'yonhap_economy')

        Returns:
            Configured RSSReader instance

        Raises:
            ValueError: If source_name is not found in registry

        Example:
            >>> reader = RSSReader.from_source("yonhap_economy")
            >>> articles = reader.fetch(limit=10)
        """
        config = get_feed_config(source_name)
        if not config:
            raise ValueError(
                f"Unknown source '{source_name}'. "
                f"Available sources: {list(FEED_REGISTRY.keys())}"
            )

        return cls(
            source_name=config.source_name,
            feed_url=str(config.feed_url),
            adapter_name=config.adapter_name,
            site_config=SiteConfig(language=config.language),
        )

    def fetch(
        self,
        limit: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Article]:
        """Fetch articles from RSS feed.

        Args:
            limit: Maximum number of articles to fetch
            start_date: Filter articles published after this date
            end_date: Filter articles published before this date

        Returns:
            List of Article objects with full content extracted
        """
        articles = []

        # Determine which feed(s) to fetch
        feeds_to_fetch = (
            [self.feed_url] if self.feed_url else list(self.FEED_URLS.values())
        )

        for feed_url in feeds_to_fetch:
            if not feed_url:
                continue

            try:
                feed = feedparser.parse(feed_url)

                # Get adapter for this source
                adapter = get_adapter(self.adapter_name, self.site_config)

                for entry in feed.entries:
                    # Apply date filters
                    published_date = adapter.parse_date(entry)
                    if start_date and published_date < start_date:
                        continue
                    if end_date and published_date > end_date:
                        continue

                    # Extract article URL
                    url = entry.get("link")
                    if not url:
                        continue

                    # Extract content using adapter
                    content = adapter.extract_content(entry)

                    # Get metadata from adapter
                    metadata = adapter.get_metadata(entry)
                    metadata["feed_url"] = feed_url

                    article = Article(
                        source=self.source_name,
                        url=url,
                        title=entry.get("title", ""),
                        content=content,
                        published_at=published_date,
                        crawled_at=datetime.now(),
                        metadata=metadata,
                    )
                    articles.append(article)

                    # Check limit
                    if limit and len(articles) >= limit:
                        break

            except Exception as e:
                print(f"Error fetching feed {feed_url}: {e}")
                continue

        return articles
