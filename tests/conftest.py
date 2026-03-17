"""Shared fixtures and configuration for pytest tests."""

import pytest
from datetime import datetime

from news_org_system.readers.rss_reader import RSSReader
from news_org_system.readers.base_reader import Article


@pytest.fixture
def rss_reader_maeil():
    """RSS reader configured for Maeil Business News.

    Returns:
        RSSReader instance configured for Maeil Business News feed
    """
    return RSSReader("maeil_test", feed_url="https://www.mk.co.kr/rss/50100032/")


@pytest.fixture
def rss_reader_etnews():
    """RSS reader configured for ETnews.

    Returns:
        RSSReader instance configured for ETnews feed
    """
    return RSSReader("etnews_test", feed_url="https://rss.etnews.com/Section901.xml")


@pytest.fixture
def rss_reader_yonhap():
    """RSS reader configured for Yonhap News.

    Returns:
        RSSReader instance configured for Yonhap News economy feed
    """
    return RSSReader(
        "yonhap_test",
        feed_url="https://www.yonhapnewstv.co.kr/category/news/economy/feed"
    )


@pytest.fixture
def rss_reader_yonhap_from_source():
    """RSS reader created using from_source() classmethod for Yonhap.

    Tests the new registry-based instantiation method.

    Returns:
        RSSReader instance created from registry
    """
    return RSSReader.from_source("yonhap_economy")


@pytest.fixture
def rss_reader_maeil_from_source():
    """RSS reader created using from_source() classmethod for Maeil.

    Returns:
        RSSReader instance created from registry
    """
    return RSSReader.from_source("maeil_management")


@pytest.fixture
def rss_reader_etnews_from_source():
    """RSS reader created using from_source() classmethod for ETnews.

    Returns:
        RSSReader instance created from registry
    """
    return RSSReader.from_source("etnews_today")


@pytest.fixture
def validate_article_quality():
    """Factory function to validate article quality.

    Returns a function that performs quality checks and returns
    a dict with validation results.

    Returns:
        Function that takes an Article and returns validation dict
    """
    def _validate(article: Article) -> dict:
        """Validate article quality.

        Args:
            article: Article object to validate

        Returns:
            Dict with validation results:
            - is_valid: bool indicating if article passes all checks
            - issues: list of issue descriptions
            - content_length: length of article content
            - has_html: whether content contains HTML tags
        """
        issues = []

        if len(article.content) < 500:
            issues.append("Too short (< 500 chars)")
        if "<" in article.content and ">" in article.content:
            issues.append("Contains HTML tags")
        if not article.content.strip():
            issues.append("Empty content")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "content_length": len(article.content),
            "has_html": "<" in article.content and ">" in article.content
        }

    return _validate


@pytest.fixture
def sample_article_limit():
    """Default number of articles to fetch per test.

    Returns:
        Integer limit for article fetching
    """
    return 3


@pytest.fixture
def quality_thresholds():
    """Quality thresholds for validation.

    Returns:
        Dict with quality threshold values
    """
    return {
        "min_content_length": 500,
        "max_html_ratio": 0.1,  # Max 10% HTML characters
        "min_success_rate": 0.8  # 80% of articles should pass
    }
