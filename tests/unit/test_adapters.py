"""Unit tests for RSS adapter classes.

Tests BaseRSSAdapter, DefaultRSSAdapter, YonhapAdapter, MaeliAdapter,
and ETnewsAdapter for correct content extraction, date parsing, and
metadata generation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from src.readers.adapters.base import BaseRSSAdapter
from src.readers.adapters.default_adapter import DefaultRSSAdapter
from src.readers.adapters.yonhap_adapter import YonhapAdapter
from src.readers.adapters.maeil_adapter import MaeliAdapter
from src.readers.adapters.etnews_adapter import ETnewsAdapter
from src.readers.models.site_config import SiteConfig


class TestBaseRSSAdapter:
    """Tests for BaseRSSAdapter abstract base class."""

    def test_base_adapter_is_abstract(self):
        """Test that BaseRSSAdapter cannot be instantiated directly."""
        config = SiteConfig()
        with pytest.raises(TypeError):
            BaseRSSAdapter(config)

    def test_concrete_adapter_instantiation(self):
        """Test that concrete adapters can be instantiated."""
        config = SiteConfig()

        # All concrete adapters should be instantiable
        DefaultRSSAdapter(config)
        YonhapAdapter(config)
        MaeliAdapter(config)
        ETnewsAdapter(config)

    def test_adapter_has_config(self):
        """Test that adapter stores config correctly."""
        config = SiteConfig(language="en", request_timeout=30)
        adapter = DefaultRSSAdapter(config)

        assert adapter.config == config
        assert adapter.config.language == "en"
        assert adapter.config.request_timeout == 30


class MockFeedParserDict:
    """Mock FeedParserDict for testing."""

    def __init__(self, **kwargs):
        self._data = kwargs

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def has_key(self, key):
        return key in self._data


class TestDefaultRSSAdapter:
    """Tests for DefaultRSSAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create a DefaultRSSAdapter instance for testing."""
        return DefaultRSSAdapter(SiteConfig())

    def test_extract_content_with_content_encoded(self, adapter):
        """Test extracting content from content:encoded tag."""
        entry = MockFeedParserDict(
            content=[Mock(value="<p>This is <strong>HTML</strong> content</p>")],
            summary="Short summary",
        )

        content = adapter.extract_content(entry)

        assert "This is HTML content" in content
        assert "<p>" not in content
        assert "<strong>" not in content

    def test_extract_content_with_long_summary(self, adapter):
        """Test extracting content from long summary tag."""
        long_summary = "<p>" + "This is a long summary. " * 20 + "</p>"

        entry = MockFeedParserDict(
            content=None,
            summary=long_summary,
        )

        content = adapter.extract_content(entry)

        assert len(content) > 300  # min_content_length default
        assert "This is a long summary" in content
        assert "<p>" not in content

    def test_extract_content_with_short_summary(self, adapter):
        """Test that short summary falls back to empty string when web scraping fails."""
        entry = MockFeedParserDict(
            content=None,
            summary="Short summary",
            link=None,  # No URL for web scraping
        )

        content = adapter.extract_content(entry)

        # Should return the short summary as fallback
        assert "Short summary" in content

    def test_extract_content_with_description(self, adapter):
        """Test extracting content from description tag."""
        long_description = "<p>" + "Description text. " * 20 + "</p>"

        entry = MockFeedParserDict(
            content=None,
            summary=None,
            description=long_description,
        )

        content = adapter.extract_content(entry)

        assert len(content) > 300
        assert "Description text" in content

    def test_extract_content_no_content(self, adapter):
        """Test extracting content when no content is available."""
        entry = MockFeedParserDict(
            content=None,
            summary=None,
            description=None,
        )

        content = adapter.extract_content(entry)

        assert content == ""

    def test_strip_html(self, adapter):
        """Test HTML stripping functionality."""
        html = "<div><p>Hello</p><p>World</p></div>"
        text = adapter._strip_html(html)

        assert "<div>" not in text
        assert "<p>" not in text
        assert "Hello World" in text

    def test_strip_html_preserves_text(self, adapter):
        """Test that HTML stripping preserves text content."""
        html = "<h1>Title</h1><p>This is <strong>important</strong> text.</p>"
        text = adapter._strip_html(html)

        assert "Title" in text
        assert "This is" in text
        assert "important" in text
        assert "text" in text
        assert "<h1>" not in text
        assert "<strong>" not in text

    def test_parse_date_with_published_parsed(self, adapter):
        """Test parsing date from published_parsed field."""
        time_struct = (2024, 3, 15, 10, 30, 0, 0, 0, 0)
        entry = MockFeedParserDict(
            published_parsed=time_struct,
        )

        date = adapter.parse_date(entry)

        assert date == datetime(2024, 3, 15, 10, 30, 0)

    def test_parse_date_with_updated_parsed(self, adapter):
        """Test parsing date from updated_parsed field."""
        time_struct = (2024, 3, 15, 10, 30, 0, 0, 0, 0)
        entry = MockFeedParserDict(
            published_parsed=None,
            updated_parsed=time_struct,
        )

        date = adapter.parse_date(entry)

        assert date == datetime(2024, 3, 15, 10, 30, 0)

    def test_parse_date_no_date_field(self, adapter):
        """Test parsing date when no date field is present."""
        entry = MockFeedParserDict(
            published_parsed=None,
            updated_parsed=None,
        )

        date = adapter.parse_date(entry)

        # Should return current time
        assert isinstance(date, datetime)
        assert (datetime.now() - date).total_seconds() < 5  # Within 5 seconds

    def test_get_metadata_basic(self, adapter):
        """Test extracting basic metadata."""
        entry = MockFeedParserDict(
            author="John Doe",
            summary="Article summary",
            tags=[Mock(term="economy"), Mock(term="technology")],
        )

        metadata = adapter.get_metadata(entry)

        assert metadata["author"] == "John Doe"
        assert metadata["summary"] == "Article summary"
        assert "economy" in metadata["tags"]
        assert "technology" in metadata["tags"]

    def test_get_metadata_empty(self, adapter):
        """Test extracting metadata when fields are missing."""
        entry = MockFeedParserDict()

        metadata = adapter.get_metadata(entry)

        assert metadata["author"] == ""
        assert metadata["summary"] == ""
        assert metadata["tags"] == []


class TestYonhapAdapter:
    """Tests for YonhapAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create a YonhapAdapter instance for testing."""
        return YonhapAdapter(SiteConfig())

    def test_yonhap_adapter_inherits_default(self, adapter):
        """Test that YonhapAdapter inherits DefaultRSSAdapter methods."""
        entry = MockFeedParserDict(
            content=[Mock(value="<p>Yonhap content</p>")],
        )

        content = adapter.extract_content(entry)
        assert "Yonhap content" in content


class TestMaeliAdapter:
    """Tests for MaeliAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create a MaeliAdapter instance for testing."""
        return MaeliAdapter(SiteConfig())

    def test_maeli_adapter_inherits_default(self, adapter):
        """Test that MaeliAdapter inherits DefaultRSSAdapter methods."""
        entry = MockFeedParserDict(
            content=[Mock(value="<p>Maeil content</p>")],
        )

        content = adapter.extract_content(entry)
        assert "Maeil content" in content


class TestETnewsAdapter:
    """Tests for ETnewsAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create an ETnewsAdapter instance for testing."""
        return ETnewsAdapter(SiteConfig())

    def test_etnews_adapter_inherits_default(self, adapter):
        """Test that ETnewsAdapter inherits DefaultRSSAdapter methods."""
        entry = MockFeedParserDict(
            content=[Mock(value="<p>ETnews content</p>")],
        )

        content = adapter.extract_content(entry)
        assert "ETnews content" in content


class TestAdapterConfigIntegration:
    """Tests for adapter configuration integration."""

    def test_adapter_uses_config_language(self):
        """Test that adapter respects language config."""
        config = SiteConfig(language="en")
        adapter = DefaultRSSAdapter(config)

        assert adapter.config.language == "en"

    def test_adapter_uses_config_timeout(self):
        """Test that adapter respects timeout config."""
        config = SiteConfig(request_timeout=30)
        adapter = DefaultRSSAdapter(config)

        assert adapter.config.request_timeout == 30

    def test_adapter_uses_config_user_agent(self):
        """Test that adapter respects user agent config."""
        custom_ua = "TestBot/1.0"
        config = SiteConfig(browser_user_agent=custom_ua)
        adapter = DefaultRSSAdapter(config)

        assert adapter.config.browser_user_agent == custom_ua

    def test_adapter_uses_min_content_length(self):
        """Test that adapter respects min_content_length config."""
        config = SiteConfig(min_content_length=500)
        adapter = DefaultRSSAdapter(config)

        assert adapter.config.min_content_length == 500
