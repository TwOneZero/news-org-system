"""Shared fixtures and configuration for pytest tests."""

import pytest
from datetime import datetime

from src.readers.rss_reader import RSSReader
from src.readers.base_reader import Article


@pytest.fixture
def rss_reader_maeil():
    """RSS reader configured for Maeil Business News.

    Returns:
        RSSReader instance configured for Maeil Business News feed
    """
    return RSSReader("maeil_test", feed_url="https://www.mk.co.kr/rss/50100032/")


@pytest.fixture
def rss_reader_bbc():
    """RSS reader configured for BBC.

    Returns:
        RSSReader instance configured for BBC news feed
    """
    return RSSReader("bbc_test", feed_url="https://feeds.bbci.co.uk/news/rss.xml")


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
