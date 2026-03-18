"""Abstract base class for data readers."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional


class Article:
    """Represents a single article or disclosure."""

    def __init__(
        self,
        source: str,
        url: str,
        title: str,
        content: str,
        published_at: datetime,
        crawled_at: datetime,
        metadata: Optional[Dict] = None,
    ):
        self.source = source
        self.url = url
        self.title = title
        self.content = content
        self.published_at = published_at
        self.crawled_at = crawled_at
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        """Convert article to dictionary format."""
        return {
            "source": self.source,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "published_at": self.published_at,
            "crawled_at": self.crawled_at,
            "metadata": self.metadata,
        }


class BaseReader(ABC):
    """Abstract base class for data readers.

    All readers should inherit from this class and implement the fetch method.
    """

    def __init__(self, source_name: str):
        """Initialize the reader.

        Args:
            source_name: Name of the data source (e.g., 'yonhap', 'maeil')
        """
        self.source_name = source_name

    @abstractmethod
    def fetch(
        self,
        limit: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Article]:
        """Fetch articles from the data source.

        Args:
            limit: Maximum number of articles to fetch
            start_date: Filter articles published after this date
            end_date: Filter articles published before this date

        Returns:
            List of Article objects
        """
        pass
