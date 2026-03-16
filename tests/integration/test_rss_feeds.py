"""Integration tests for RSS feed extraction.

Tests RSS content extraction from various news sources including:
- Maeil Business News (mk.co.kr)
- BBC (bbc.co.uk)
- Yonhap News (yonhapnewstv.co.kr)
"""

import pytest
from datetime import datetime

from src.readers.base_reader import Article


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
    assert len(articles) <= sample_article_limit, f"Should not exceed limit of {sample_article_limit}"
    assert all(isinstance(a, Article) for a in articles), "All items should be Article objects"


@pytest.mark.integration
def test_maeil_content_quality(rss_reader_maeil, validate_article_quality, sample_article_limit):
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

    # Assert quality threshold (at least 80% should pass)
    assert success_rate >= 0.8, f"Quality threshold not met: {success_rate:.1%} valid articles"


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
    assert hasattr(article, 'title'), "Should have title attribute"
    assert hasattr(article, 'content'), "Should have content attribute"
    assert hasattr(article, 'url'), "Should have url attribute"
    assert hasattr(article, 'published_at'), "Should have published_at attribute"
    assert hasattr(article, 'source'), "Should have source attribute"
    assert hasattr(article, 'crawled_at'), "Should have crawled_at attribute"
    assert hasattr(article, 'metadata'), "Should have metadata attribute"

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
def test_bbc_fetch_success(rss_reader_bbc, sample_article_limit):
    """Test that BBC RSS feed can be fetched successfully.

    Args:
        rss_reader_bbc: Fixture providing configured RSSReader for BBC
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_bbc.fetch(limit=sample_article_limit)

    assert len(articles) > 0, "Should fetch at least one article from BBC"
    assert len(articles) <= sample_article_limit, f"Should not exceed limit of {sample_article_limit}"
    assert all(isinstance(a, Article) for a in articles), "All items should be Article objects"


@pytest.mark.integration
def test_bbc_content_quality(rss_reader_bbc, validate_article_quality, sample_article_limit):
    """Test BBC article content meets quality standards.

    Args:
        rss_reader_bbc: Fixture providing configured RSSReader for BBC
        validate_article_quality: Fixture providing quality validator
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_bbc.fetch(limit=sample_article_limit)
    quality_results = [validate_article_quality(article) for article in articles]

    valid_count = sum(1 for r in quality_results if r["is_valid"])
    success_rate = valid_count / len(articles)

    assert success_rate >= 0.8, f"Quality threshold not met: {success_rate:.1%} valid articles"


@pytest.mark.integration
def test_bbc_article_structure(rss_reader_bbc, sample_article_limit):
    """Test that BBC RSS articles have correct structure and metadata.

    Args:
        rss_reader_bbc: Fixture providing configured RSSReader for BBC
        sample_article_limit: Fixture providing article fetch limit
    """
    articles = rss_reader_bbc.fetch(limit=sample_article_limit)
    assert len(articles) > 0, "Should fetch at least one article"

    article = articles[0]

    # Required fields
    assert article.title, "Title should not be empty"
    assert article.url, "URL should not be empty"
    assert article.content, "Content should not be empty"
    assert isinstance(article.published_at, datetime), "Should be datetime object"
    assert "bbc" in article.source.lower(), "Source should contain 'bbc'"


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
    assert len(articles) <= sample_article_limit, f"Should not exceed limit of {sample_article_limit}"
    assert all(isinstance(a, Article) for a in articles), "All items should be Article objects"


@pytest.mark.integration
def test_yonhap_content_quality(rss_reader_yonhap, validate_article_quality, sample_article_limit):
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

    # Yonhap should have higher success rate (baseline test)
    assert success_rate >= 0.8, f"Quality threshold not met: {success_rate:.1%} valid articles"


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
@pytest.mark.parametrize("reader_fixture,source_name", [
    ("rss_reader_maeil", "Maeil Business News"),
    ("rss_reader_bbc", "BBC"),
    ("rss_reader_yonhap", "Yonhap News"),
])
def test_all_rss_sources_fetchable(request, reader_fixture, source_name, sample_article_limit):
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
    assert all(isinstance(a, Article) for a in articles), f"{source_name} articles should be Article objects"


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

    assert len(articles) <= limit, f"Should fetch at most {limit} articles, got {len(articles)}"
