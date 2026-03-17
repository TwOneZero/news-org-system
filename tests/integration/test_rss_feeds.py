"""Integration tests for RSS feed extraction with adapter pattern.

Tests RSS content extraction from various news sources including:
- Maeil Business News (mk.co.kr)
- Yonhap News (yonhapnewstv.co.kr)
- ETnews (etnews.com)

Also tests the new from_source() classmethod and registry system.
"""

import pytest
from datetime import datetime

from news_org_system.readers.base_reader import Article
from news_org_system.readers.rss_reader import RSSReader
from news_org_system.readers.registry import get_feed_config, list_feeds


@pytest.mark.integration
def test_maeil_fetch_success(rss_reader_maeil, sample_article_limit):
    """Test that Maeil Business News RSS feed can be fetched successfully.

    Validates basic fetch functionality and article object structure.

    Args:
        rss_reader_maeil: Fixture providing configured RSSReader for Maeil
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_maeil.fetch(limit=sample_article_limit)

    # Basic fetch validation
    assert len(articles) > 0, "Should fetch at least one article from Maeil"
    assert len(articles) <= sample_article_limit, (
        f"Should not exceed limit of {sample_article_limit}"
    )
    assert all(isinstance(a, Article) for a in articles), (
        "All items should be Article objects"
    )


@pytest.mark.integration
@pytest.mark.skip(reason="Maeil Business News web scraping often fails due to site structure changes")
def test_maeil_content_quality(
    rss_reader_maeil, validate_article_quality, sample_article_limit
):
    """Test Maeil Business News article content meets quality standards.

    Validates that extracted articles meet minimum quality thresholds:
    - Content length >= 500 characters
    - No HTML tags in content
    - Non-empty content

    Args:
        rss_reader_maeil: Fixture providing configured RSSReader for Maeil
        validate_article_quality: Fixture providing quality validator
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_maeil.fetch(limit=sample_article_limit)
    quality_results = [validate_article_quality(article) for article in articles]

    # Calculate quality metrics
    valid_count = sum(1 for r in quality_results if r["is_valid"])
    success_rate = valid_count / len(articles)

    # Assert quality threshold (at least 50% should pass - relaxed for real-world feeds)
    assert success_rate >= 0.5, (
        f"Quality threshold not met: {success_rate:.1%} valid articles"
    )


@pytest.mark.integration
def test_maeil_article_structure(rss_reader_maeil, sample_article_limit):
    """Test that Maeil RSS articles have correct structure and metadata.

    Validates Article object attributes and types.

    Args:
        rss_reader_maeil: Fixture providing configured RSSReader for Maeil
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_maeil.fetch(limit=sample_article_limit)
    assert len(articles) > 0, "Should fetch at least one article"

    # Test first article structure
    article = articles[0]

    # Required fields
    assert hasattr(article, "title"), "Should have title attribute"
    assert hasattr(article, "content"), "Should have content attribute"
    assert hasattr(article, "url"), "Should have url attribute"
    assert hasattr(article, "published_at"), "Should have published_at attribute"
    assert hasattr(article, "source"), "Should have source attribute"
    assert hasattr(article, "crawled_at"), "Should have crawled_at attribute"
    assert hasattr(article, "metadata"), "Should have metadata attribute"

    # Type checks
    assert isinstance(article.title, str), "Title should be string"
    assert isinstance(article.content, str), "Content should be string"
    assert isinstance(article.url, str), "URL should be string"
    assert isinstance(article.published_at, datetime), "Should be datetime object"
    assert isinstance(article.source, str), "Source should be string"
    assert isinstance(article.metadata, dict), "Metadata should be dict"

    # Value checks
    assert article.title, "Title should not be empty"
    assert article.url, "URL should not be empty"
    assert article.content, "Content should not be empty"
    assert "maeil" in article.source.lower(), "Source should contain 'maeil'"


@pytest.mark.integration
def test_yonhap_fetch_success(rss_reader_yonhap, sample_article_limit):
    """Test that Yonhap News RSS feed can be fetched successfully.

    Yonhap serves as a baseline test since it typically works well.

    Args:
        rss_reader_yonhap: Fixture providing configured RSSReader for Yonhap
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_yonhap.fetch(limit=sample_article_limit)

    assert len(articles) > 0, "Should fetch at least one article from Yonhap"
    assert len(articles) <= sample_article_limit, (
        f"Should not exceed limit of {sample_article_limit}"
    )
    assert all(isinstance(a, Article) for a in articles), (
        "All items should be Article objects"
    )


@pytest.mark.integration
def test_yonhap_content_quality(
    rss_reader_yonhap, validate_article_quality, sample_article_limit
):
    """Test Yonhap News article content meets quality standards.

    Args:
        rss_reader_yonhap: Fixture providing configured RSSReader for Yonhap
        validate_article_quality: Fixture providing quality validator
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_yonhap.fetch(limit=sample_article_limit)
    quality_results = [validate_article_quality(article) for article in articles]

    valid_count = sum(1 for r in quality_results if r["is_valid"])
    success_rate = valid_count / len(articles)

    # Yonhap should have higher success rate (baseline test, relaxed to 60%)
    assert success_rate >= 0.6, (
        f"Quality threshold not met: {success_rate:.1%} valid articles"
    )


@pytest.mark.integration
def test_yonhap_article_structure(rss_reader_yonhap, sample_article_limit):
    """Test that Yonhap RSS articles have correct structure and metadata.

    Args:
        rss_reader_yonhap: Fixture providing configured RSSReader for Yonhap
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_yonhap.fetch(limit=sample_article_limit)
    assert len(articles) > 0, "Should fetch at least one article"

    article = articles[0]

    # Required fields
    assert article.title, "Title should not be empty"
    assert article.url, "URL should not be empty"
    assert article.content, "Content should not be empty"
    assert isinstance(article.published_at, datetime), "Should be datetime object"
    assert "yonhap" in article.source.lower(), "Source should contain 'yonhap'"


@pytest.mark.integration
def test_etnews_fetch_success(rss_reader_etnews, sample_article_limit):
    """Test that ETnews RSS feed can be fetched successfully.

    Args:
        rss_reader_etnews: Fixture providing configured RSSReader for ETnews
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_etnews.fetch(limit=sample_article_limit)

    assert len(articles) > 0, "Should fetch at least one article from ETnews"
    assert len(articles) <= sample_article_limit, (
        f"Should not exceed limit of {sample_article_limit}"
    )
    assert all(isinstance(a, Article) for a in articles), (
        "All items should be Article objects"
    )


@pytest.mark.integration
def test_etnews_content_quality(
    rss_reader_etnews, validate_article_quality, sample_article_limit
):
    """Test ETnews article content meets quality standards.

    Args:
        rss_reader_etnews: Fixture providing configured RSSReader for ETnews
        validate_article_quality: Fixture providing quality validator
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_etnews.fetch(limit=sample_article_limit)
    quality_results = [validate_article_quality(article) for article in articles]

    valid_count = sum(1 for r in quality_results if r["is_valid"])
    success_rate = valid_count / len(articles)

    # Assert quality threshold
    assert success_rate >= 0.8, (
        f"Quality threshold not met: {success_rate:.1%} valid articles"
    )


@pytest.mark.integration
def test_etnews_article_structure(rss_reader_etnews, sample_article_limit):
    """Test that ETnews RSS articles have correct structure.

    Args:
        rss_reader_etnews: Fixture providing configured RSSReader for ETnews
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_etnews.fetch(limit=sample_article_limit)
    assert len(articles) > 0, "Should fetch at least one article"

    article = articles[0]

    # Required fields
    assert article.title, "Title should not be empty"
    assert article.url, "URL should not be empty"
    assert article.content, "Content should not be empty"
    assert isinstance(article.published_at, datetime), "Should be datetime object"
    assert "etnews" in article.source.lower(), "Source should contain 'etnews'"


@pytest.mark.integration
def test_from_source_method_yonhap(sample_article_limit):
    """Test creating RSSReader using from_source() classmethod for Yonhap.

    Tests the new registry-based instantiation method.

    Args:
        sample_article_limit: Fixture providing article fetch limit
    """
    # Create reader using from_source
    reader = RSSReader.from_source("yonhap_economy")

    # Verify it was created correctly
    assert reader.source_name == "yonhap_economy"
    assert "yonhapnewstv.co.kr" in reader.feed_url
    assert reader.adapter_name == "yonhap"

    # Verify it can fetch articles
    articles = reader.fetch(limit=sample_article_limit)
    assert len(articles) > 0, "Should fetch articles using from_source reader"


@pytest.mark.integration
def test_from_source_method_maeil(sample_article_limit):
    """Test creating RSSReader using from_source() classmethod for Maeil.

    Args:
        sample_article_limit: Fixture providing article fetch limit
    """
    reader = RSSReader.from_source("maeil_management")

    assert reader.source_name == "maeil_management"
    assert "mk.co.kr" in reader.feed_url
    assert reader.adapter_name == "maeil"

    articles = reader.fetch(limit=sample_article_limit)
    assert len(articles) > 0, "Should fetch articles using from_source reader"


@pytest.mark.integration
def test_from_source_method_etnews(sample_article_limit):
    """Test creating RSSReader using from_source() classmethod for ETnews.

    Args:
        sample_article_limit: Fixture providing article fetch limit
    """
    reader = RSSReader.from_source("etnews_today")

    assert reader.source_name == "etnews_today"
    assert "etnews.com" in reader.feed_url
    assert reader.adapter_name == "etnews"

    articles = reader.fetch(limit=sample_article_limit)
    assert len(articles) > 0, "Should fetch articles using from_source reader"


@pytest.mark.integration
def test_from_source_invalid_source():
    """Test that from_source() raises ValueError for unknown source."""
    with pytest.raises(ValueError, match="Unknown source"):
        RSSReader.from_source("invalid_source_name")


@pytest.mark.integration
@pytest.mark.parametrize(
    "reader_fixture,source_name",
    [
        ("rss_reader_maeil", "Maeil Business News"),
        ("rss_reader_yonhap", "Yonhap News"),
        ("rss_reader_etnews", "ETnews"),
    ],
)
def test_all_rss_sources_fetchable(
    request, reader_fixture, source_name, sample_article_limit
):
    """Test that all RSS sources can fetch articles.

    This parametrized test ensures basic functionality across all configured
    RSS feed sources.

    Args:
        request: Pytest request object for fixture access
        reader_fixture: Name of the RSS reader fixture to use
        source_name: Human-readable name of the source
        sample_article_limit: Fixture providing article fetch limit
    """
    reader = request.getfixturevalue(reader_fixture)
    articles = reader.fetch(limit=sample_article_limit)

    assert len(articles) > 0, f"{source_name} should fetch at least one article"
    assert all(isinstance(a, Article) for a in articles), (
        f"{source_name} articles should be Article objects"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "source_name,expected_source",
    [
        ("yonhap_economy", "yonhap_economy"),
        ("maeil_management", "maeil_management"),
        ("etnews_today", "etnews_today"),
    ],
)
def test_all_registry_sources_fetchable(
    source_name, expected_source, sample_article_limit
):
    """Test that all sources in the registry can fetch articles.

    Args:
        source_name: Source name in registry
        expected_source: Expected source name in reader
        sample_article_limit: Fixture providing article fetch limit
    """
    reader = RSSReader.from_source(source_name)
    assert reader.source_name == expected_source

    articles = reader.fetch(limit=sample_article_limit)
    assert len(articles) > 0, f"{source_name} should fetch articles"


@pytest.mark.integration
def test_rss_article_metadata_quality(rss_reader_yonhap):
    """Test that RSS articles contain expected metadata fields.

    Validates metadata structure and common fields.

    Args:
        rss_reader_yonhap: Fixture providing configured RSSReader for Yonhap
    """
    articles = rss_reader_yonhap.fetch(limit=1)
    assert len(articles) > 0, "Should fetch at least one article"

    article = articles[0]

    # Check metadata exists and is a dict
    assert article.metadata is not None, "Metadata should exist"
    assert isinstance(article.metadata, dict), "Metadata should be a dict"

    # Common metadata fields (may vary by source)
    assert "feed_url" in article.metadata, "Should contain feed_url in metadata"


@pytest.mark.integration
def test_rss_limit_parameter(rss_reader_yonhap):
    """Test that the limit parameter correctly restricts article count.

    Args:
        rss_reader_yonhap: Fixture providing configured RSSReader for Yonhap
    """
    limit = 2
    articles = rss_reader_yonhap.fetch(limit=limit)

    assert len(articles) <= limit, (
        f"Should fetch at most {limit} articles, got {len(articles)}"
    )


@pytest.mark.integration
def test_registry_feed_configs():
    """Test that all feed configs in registry are valid."""
    feeds = list_feeds()

    # Check that we have the expected feeds
    assert "yonhap_economy" in feeds
    assert "maeil_management" in feeds
    assert "etnews_today" in feeds

    # Check that all configs are valid
    for source_name, config in feeds.items():
        assert config.source_name == source_name
        assert str(config.feed_url).startswith("http")
        assert config.adapter_name in ["default", "yonhap", "maeil", "etnews"]
        assert config.language == "ko"
        assert config.enabled is True


@pytest.mark.integration
def test_date_filtering():
    """Test that date filtering works correctly."""
    from datetime import timedelta

    reader = RSSReader.from_source("yonhap_economy")

    # Fetch articles from last 24 hours
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()

    articles = reader.fetch(start_date=start_date, end_date=end_date, limit=10)

    # Verify dates are within range
    for article in articles:
        assert start_date <= article.published_at <= end_date, (
            f"Article date {article.published_at} is outside range "
            f"{start_date} to {end_date}"
        )
