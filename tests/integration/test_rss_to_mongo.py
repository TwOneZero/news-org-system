"""Integration tests for RSS feed collection to MongoDB storage.

Tests the complete pipeline:
1. Fetch articles from RSS feeds
2. Store articles in MongoDB
3. Verify storage and retrieval
"""

from datetime import datetime

import pytest

from news_org_system.readers.rss_reader import RSSReader


@pytest.mark.integration
def test_rss_to_mongo_pipeline_yonhap(mongo_store, sample_article_limit):
    """Test complete pipeline: RSS fetch → MongoDB save for Yonhap.

    Args:
        mongo_store: MongoStore fixture for testing
        sample_article_limit: Fixture providing article fetch limit
    """
    # 1. Fetch articles from RSS
    reader = RSSReader.from_source("yonhap_economy")
    articles = reader.fetch(limit=sample_article_limit)

    assert len(articles) > 0, "Should fetch at least one article"

    # 2. Save to MongoDB
    result = mongo_store.save_articles(articles)

    # 3. Verify save results
    assert result["saved"] > 0, "Should save at least one article"
    assert result["saved"] + result["skipped"] == len(articles), (
        "Saved + skipped should equal total articles"
    )

    # 4. Verify articles are in database
    for article in articles:
        saved_article = mongo_store.get_article_by_url(article.url)
        assert saved_article is not None, f"Article should be saved: {article.url}"
        assert saved_article["title"] == article.title
        assert saved_article["source"] == article.source


@pytest.mark.integration
def test_rss_to_mongo_pipeline_etnews(mongo_store, sample_article_limit):
    """Test complete pipeline: RSS fetch → MongoDB save for ETnews.

    Args:
        mongo_store: MongoStore fixture for testing
        sample_article_limit: Fixture providing article fetch limit
    """
    # 1. Fetch articles from RSS
    reader = RSSReader.from_source("etnews_today")
    articles = reader.fetch(limit=sample_article_limit)

    assert len(articles) > 0, "Should fetch at least one article"

    # 2. Save to MongoDB
    result = mongo_store.save_articles(articles)

    # 3. Verify save results
    assert result["saved"] > 0, "Should save at least one article"

    # 4. Verify articles are in database
    for article in articles:
        saved_article = mongo_store.get_article_by_url(article.url)
        assert saved_article is not None, f"Article should be saved: {article.url}"


@pytest.mark.integration
def test_duplicate_detection(mongo_store):
    """Test that duplicate articles are not saved again.

    Args:
        mongo_store: MongoStore fixture for testing
    """
    # 1. Fetch articles
    reader = RSSReader.from_source("yonhap_economy")
    articles = reader.fetch(limit=1)

    assert len(articles) > 0, "Should fetch at least one article"

    # 2. Save first time
    result1 = mongo_store.save_articles(articles)
    assert result1["saved"] > 0, "Should save article on first attempt"
    assert result1["skipped"] == 0, "Should not skip on first attempt"

    # 3. Save same articles again (should be skipped)
    result2 = mongo_store.save_articles(articles)
    assert result2["saved"] == 0, "Should not save duplicates"
    assert result2["skipped"] > 0, "Should skip duplicate articles"


@pytest.mark.integration
def test_retrieve_by_source(mongo_store, sample_article_limit):
    """Test retrieving articles by source.

    Args:
        mongo_store: MongoStore fixture for testing
        sample_article_limit: Fixture providing article fetch limit
    """
    # 1. Save articles from different sources
    yonhap_reader = RSSReader.from_source("yonhap_economy")
    yonhap_articles = yonhap_reader.fetch(limit=sample_article_limit)

    etnews_reader = RSSReader.from_source("etnews_today")
    etnews_articles = etnews_reader.fetch(limit=sample_article_limit)

    mongo_store.save_articles(yonhap_articles)
    mongo_store.save_articles(etnews_articles)

    # 2. Retrieve by source
    yonhap_retrieved = mongo_store.get_articles(source="yonhap_economy")
    etnews_retrieved = mongo_store.get_articles(source="etnews_today")

    # 3. Verify retrieval
    assert len(yonhap_retrieved) > 0, "Should retrieve Yonhap articles"
    assert len(etnews_retrieved) > 0, "Should retrieve ETnews articles"

    # Verify source filter works
    for article in yonhap_retrieved:
        assert article["source"] == "yonhap_economy"
    for article in etnews_retrieved:
        assert article["source"] == "etnews_today"


@pytest.mark.integration
def test_retrieve_by_date_range(mongo_store):
    """Test retrieving articles by date range.

    Args:
        mongo_store: MongoStore fixture for testing
    """
    # 1. Save articles
    reader = RSSReader.from_source("yonhap_economy")
    articles = reader.fetch(limit=5)

    mongo_store.save_articles(articles)

    # 2. Retrieve recent articles
    from datetime import timedelta

    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()

    recent_articles = mongo_store.get_articles(
        start_date=start_date, end_date=end_date, limit=10
    )

    # 3. Verify date range
    assert len(recent_articles) > 0, "Should retrieve articles within date range"
    for article in recent_articles:
        article_date = article["published_at"]
        if isinstance(article_date, datetime):
            assert start_date <= article_date <= end_date, (
                f"Article date {article_date} should be within range"
            )


@pytest.mark.integration
def test_get_stats(mongo_store, sample_article_limit):
    """Test getting statistics about stored articles.

    Args:
        mongo_store: MongoStore fixture for testing
        sample_article_limit: Fixture providing article fetch limit
    """
    # 1. Save articles
    reader = RSSReader.from_source("yonhap_economy")
    articles = reader.fetch(limit=sample_article_limit)

    mongo_store.save_articles(articles)

    # 2. Get stats
    stats = mongo_store.get_stats()

    # 3. Verify stats
    assert stats["total"] > 0, "Should have at least one article"
    assert "by_source" in stats, "Should have source breakdown"
    assert "latest" in stats, "Should have latest article info"
    assert len(stats["by_source"]) > 0, "Should have at least one source"


@pytest.mark.integration
def test_article_structure_in_db(mongo_store):
    """Test that articles have correct structure when retrieved from database.

    Args:
        mongo_store: MongoStore fixture for testing
    """
    # 1. Save article
    reader = RSSReader.from_source("yonhap_economy")
    articles = reader.fetch(limit=1)

    assert len(articles) > 0, "Should fetch at least one article"

    mongo_store.save_articles(articles)

    # 2. Retrieve article
    original = articles[0]
    retrieved = mongo_store.get_article_by_url(original.url)

    # 3. Verify structure
    assert retrieved is not None, "Article should be retrieved"
    assert "title" in retrieved, "Should have title"
    assert "content" in retrieved, "Should have content"
    assert "url" in retrieved, "Should have url"
    assert "source" in retrieved, "Should have source"
    assert "published_at" in retrieved, "Should have published_at"
    assert "crawled_at" in retrieved, "Should have crawled_at"
    assert "metadata" in retrieved, "Should have metadata"

    # Verify values match
    assert retrieved["title"] == original.title
    assert retrieved["url"] == original.url
    assert retrieved["source"] == original.source


@pytest.mark.integration
@pytest.mark.parametrize(
    "source_name",
    ["yonhap_economy", "etnews_today"],
)
def test_all_sources_to_mongo(source_name, mongo_store, sample_article_limit):
    """Test that all registered sources can be saved to MongoDB.

    Args:
        source_name: Source name in registry
        mongo_store: MongoStore fixture for testing
        sample_article_limit: Fixture providing article fetch limit
    """
    # 1. Fetch and save
    reader = RSSReader.from_source(source_name)
    articles = reader.fetch(limit=sample_article_limit)

    assert len(articles) > 0, f"{source_name} should fetch articles"

    result = mongo_store.save_articles(articles)

    # 2. Verify save
    assert result["saved"] > 0, f"{source_name} should save articles to MongoDB"

    # 3. Verify retrieval
    for article in articles:
        saved = mongo_store.get_article_by_url(article.url)
        assert saved is not None, f"{source_name} article should be retrievable"
