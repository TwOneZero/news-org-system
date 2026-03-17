"""Unit tests for Pydantic models.

Tests RSSFeedConfig, SiteConfig, and RSSItem models for validation,
type safety, and correct behavior.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.readers.models.rss_config import RSSFeedConfig, RSSItem
from src.readers.models.site_config import SiteConfig


class TestRSSFeedConfig:
    """Tests for RSSFeedConfig model."""

    def test_valid_config(self):
        """Test creating a valid RSSFeedConfig."""
        config = RSSFeedConfig(
            source_name="test_source",
            feed_url="https://example.com/rss.xml",
            adapter_name="default",
            language="en",
        )

        assert config.source_name == "test_source"
        assert str(config.feed_url) == "https://example.com/rss.xml"
        assert config.adapter_name == "default"
        assert config.language == "en"
        assert config.enabled is True  # Default value

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = RSSFeedConfig(
            source_name="test",
            feed_url="https://example.com/rss.xml",
        )

        assert config.adapter_name == "default"
        assert config.enabled is True
        assert config.language == "ko"

    def test_invalid_url(self):
        """Test that invalid URLs are rejected."""
        with pytest.raises(ValidationError):
            RSSFeedConfig(
                source_name="test",
                feed_url="not-a-valid-url",
            )

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            RSSFeedConfig(source_name="test")

        with pytest.raises(ValidationError):
            RSSFeedConfig(feed_url="https://example.com/rss.xml")

    def test_feed_url_types(self):
        """Test that various valid URL types are accepted."""
        urls = [
            "https://example.com/rss.xml",
            "http://example.com/feed",
            "https://example.com/news/economy/feed",
        ]

        for url in urls:
            config = RSSFeedConfig(
                source_name="test",
                feed_url=url,
            )
            assert str(config.feed_url) == url

    def test_enabled_flag(self):
        """Test enabled flag can be set to False."""
        config = RSSFeedConfig(
            source_name="test",
            feed_url="https://example.com/rss.xml",
            enabled=False,
        )

        assert config.enabled is False

    def test_language_validation(self):
        """Test language field accepts various language codes."""
        languages = ["ko", "en", "ja", "zh", "fr", "de", "es"]

        for lang in languages:
            config = RSSFeedConfig(
                source_name="test",
                feed_url="https://example.com/rss.xml",
                language=lang,
            )
            assert config.language == lang


class TestSiteConfig:
    """Tests for SiteConfig model."""

    def test_default_config(self):
        """Test creating SiteConfig with defaults."""
        config = SiteConfig()

        assert config.language == "ko"
        assert "Mozilla" in config.browser_user_agent
        assert config.request_timeout == 15
        assert config.memoize_articles is False
        assert config.min_content_length == 300

    def test_custom_config(self):
        """Test creating SiteConfig with custom values."""
        config = SiteConfig(
            language="en",
            request_timeout=30,
            memoize_articles=True,
            min_content_length=500,
        )

        assert config.language == "en"
        assert config.request_timeout == 30
        assert config.memoize_articles is True
        assert config.min_content_length == 500

    def test_custom_user_agent(self):
        """Test setting custom user agent."""
        custom_ua = "MyCustomBot/1.0"
        config = SiteConfig(browser_user_agent=custom_ua)

        assert config.browser_user_agent == custom_ua

    def test_timeout_validation(self):
        """Test timeout accepts positive integers."""
        timeouts = [5, 10, 15, 30, 60, 120]

        for timeout in timeouts:
            config = SiteConfig(request_timeout=timeout)
            assert config.request_timeout == timeout


class TestRSSItem:
    """Tests for RSSItem model."""

    def test_valid_item(self):
        """Test creating a valid RSSItem."""
        item = RSSItem(
            title="Test Article",
            link="https://example.com/article1",  # Using alias
            content="This is the article content.",
            published_at=datetime.now(),
            author="John Doe",
        )

        assert item.title == "Test Article"
        assert item.url == "https://example.com/article1"
        assert item.content == "This is the article content."
        assert item.author == "John Doe"
        assert item.tags == []  # Default empty list

    def test_item_with_tags(self):
        """Test creating RSSItem with tags."""
        tags = ["economy", "technology", "ai"]
        item = RSSItem(
            title="Test Article",
            link="https://example.com/article1",  # Using alias
            content="Content here",
            published_at=datetime.now(),
            tags=tags,
        )

        assert item.tags == tags
        assert len(item.tags) == 3

    def test_item_with_summary(self):
        """Test creating RSSItem with summary."""
        item = RSSItem(
            title="Test Article",
            link="https://example.com/article1",  # Using alias
            content="Full content here",
            published_at=datetime.now(),
            summary="Brief summary",
        )

        assert item.summary == "Brief summary"

    def test_optional_fields(self):
        """Test that optional fields default to None."""
        item = RSSItem(
            title="Test Article",
            link="https://example.com/article1",  # Using alias
            content="Content",
            published_at=datetime.now(),
        )

        assert item.author is None
        assert item.summary is None
        assert item.tags == []

    def test_alias_for_url_field(self):
        """Test that 'link' alias works for URL field."""
        item = RSSItem(
            title="Test Article",
            link="https://example.com/article1",  # Using alias
            content="Content",
            published_at=datetime.now(),
        )

        assert item.url == "https://example.com/article1"

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        # Missing title
        with pytest.raises(ValidationError):
            RSSItem(
                url="https://example.com/article1",
                content="Content",
                published_at=datetime.now(),
            )

        # Missing url
        with pytest.raises(ValidationError):
            RSSItem(
                title="Test Article",
                content="Content",
                published_at=datetime.now(),
            )

        # Missing content
        with pytest.raises(ValidationError):
            RSSItem(
                title="Test Article",
                url="https://example.com/article1",
                published_at=datetime.now(),
            )

        # Missing published_at
        with pytest.raises(ValidationError):
            RSSItem(
                title="Test Article",
                url="https://example.com/article1",
                content="Content",
            )

    def test_datetime_field(self):
        """Test that datetime field accepts datetime objects."""
        now = datetime.now()
        item = RSSItem(
            title="Test Article",
            link="https://example.com/article1",  # Using alias
            content="Content",
            published_at=now,
        )

        assert item.published_at == now
        assert isinstance(item.published_at, datetime)
