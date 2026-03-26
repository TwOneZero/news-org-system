"""Shared fixtures and configuration for pytest tests."""

import os
import pytest

from news_org_system.readers.rss_reader import RSSReader
from news_org_system.readers.base_reader import Article
from news_org_system.readers.constants import SourceName
from news_org_system.storage.mongo_store import MongoStore


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
        feed_url="https://www.yonhapnewstv.co.kr/category/news/economy/feed",
    )


@pytest.fixture
def rss_reader_yonhap_from_source():
    """RSS reader created using from_source() classmethod for Yonhap.

    Tests the new registry-based instantiation method.

    Returns:
        RSSReader instance created from registry
    """
    return RSSReader.from_source(SourceName.YONHAP_ECONOMY)


@pytest.fixture
def rss_reader_maeil_from_source():
    """RSS reader created using from_source() classmethod for Maeil.

    Returns:
        RSSReader instance created from registry
    """
    return RSSReader.from_source(SourceName.MAEIL_MANAGEMENT)


@pytest.fixture
def rss_reader_etnews_from_source():
    """RSS reader created using from_source() classmethod for ETnews.

    Returns:
        RSSReader instance created from registry
    """
    return RSSReader.from_source(SourceName.ETNEWS_TODAY)


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
            "has_html": "<" in article.content and ">" in article.content,
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
        "min_success_rate": 0.8,  # 80% of articles should pass
    }


@pytest.fixture
def mongo_store():
    """MongoStore instance for testing.

    Returns:
        MongoStore instance configured for testing
    """
    # Get MongoDB URI from environment
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    # Use test database to avoid affecting production data
    store = MongoStore(
        connection_string=mongo_uri,
        database_name="news_org_test",
        articles_collection="test_articles",
    )

    yield store

    # Cleanup: Drop test collections after tests
    try:
        store.client["news_org_test"].drop_collection("test_articles")
    except Exception:
        pass  # Ignore cleanup errors
    finally:
        store.close()

# --- FastAPI Test Fixtures ---
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from news_org_system.api.main import create_app
from news_org_system.api.dependencies import get_store

@pytest.fixture
def mock_store():
    """Mocked MongoStore for unit and integration testing."""
    mock = MagicMock(spec=MongoStore)
    return mock

@pytest.fixture
def test_client(mock_store):
    """FastAPI TestClient with overridden dependencies."""
    app = create_app()
    app.dependency_overrides[get_store] = lambda: mock_store
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

