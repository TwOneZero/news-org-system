"""Base adapter class for RSS feed parsing."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict
from feedparser import FeedParserDict

from ..models.site_config import SiteConfig


class BaseRSSAdapter(ABC):
    """Abstract base class for RSS feed parsers.

    Each news site can have its own adapter to handle site-specific
    RSS structure, content extraction, and date parsing.
    """

    def __init__(self, config: SiteConfig):
        """Initialize adapter with site configuration.

        Args:
            config: Site-specific configuration for parsing
        """
        self.config = config

    @abstractmethod
    def extract_content(self, entry: FeedParserDict) -> str:
        """Extract article content from feed entry.

        Priority:
        1. content:encoded tag (highest quality from RSS)
        2. summary/description tag (fallback RSS fields)
        3. Web scraping using newspaper4k (last resort)

        Args:
            entry: Feedparser entry object

        Returns:
            Extracted article text
        """
        pass

    @abstractmethod
    def parse_date(self, entry: FeedParserDict) -> datetime:
        """Parse publication date from feed entry.

        Args:
            entry: Feedparser entry object

        Returns:
            datetime object of publication date
        """
        pass

    def get_metadata(self, entry: FeedParserDict) -> Dict:
        """Extract metadata from feed entry.

        Default implementation extracts common fields.
        Override in subclass for site-specific metadata.

        Args:
            entry: Feedparser entry object

        Returns:
            Dictionary with metadata fields
        """
        return {
            "author": entry.get("author", ""),
            "tags": [tag.term for tag in entry.get("tags", [])],
            "summary": entry.get("summary", ""),
        }
