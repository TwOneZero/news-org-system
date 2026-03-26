"""Constants for news source and adapter names.

This module provides centralized, type-safe constants for:
- News source identifiers (SourceName)
- RSS adapter identifiers (AdapterName)

These constants replace hardcoded strings throughout the codebase,
providing type safety, IDE autocomplete, and a single source of truth.
"""

from enum import Enum


class SourceName(str, Enum):
    """News source identifiers with associated feed URLs.

    Each source has:
    - A string value (e.g., "yonhap_economy")
    - A corresponding URL constant (e.g., YONHAP_ECONOMY_URL)
    - A class method to retrieve URLs

    Example:
        >>> source = SourceName.YONHAP_ECONOMY
        >>> print(source)  # "yonhap_economy"
        >>> url = SourceName.get_url(source)
    """

    # Yonhap news sources
    YONHAP_ECONOMY = "yonhap_economy"
    YONHAP_ECONOMY_URL = "https://www.yonhapnewstv.co.kr/category/news/economy/feed"

    # Maelil Business news sources
    MAEIL_MANAGEMENT = "maeil_management"
    MAEIL_MANAGEMENT_URL = "https://www.mk.co.kr/rss/50100032/"

    # ETnews sources
    ETNEWS_TODAY = "etnews_today"
    ETNEWS_TODAY_URL = "https://rss.etnews.com/Section901.xml"

    @classmethod
    def get_url(cls, source: 'SourceName') -> str:
        """Get feed URL for a given source.

        Args:
            source: SourceName enum member

        Returns:
            Feed URL string for the source

        Raises:
            AttributeError: If URL constant not found for source

        Example:
            >>> url = SourceName.get_url(SourceName.YONHAP_ECONOMY)
            >>> print(url)  # "https://www.yonhapnewstv.co.kr/category/news/economy/feed"
        """
        return getattr(cls, f"{source.name}_URL")


class AdapterName(str, Enum):
    """RSS adapter identifiers.

    Each adapter handles parsing and content extraction for specific
    news source structures.

    Example:
        >>> adapter = AdapterName.YONHAP
        >>> print(adapter)  # "yonhap"
    """

    DEFAULT = "default"
    YONHAP = "yonhap"
    MAEIL = "maeil"
    ETNEWS = "etnews"
