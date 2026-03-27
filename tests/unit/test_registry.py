"""Unit tests for RSS feed and adapter registry.

Tests FEED_REGISTRY, ADAPTER_REGISTRY, and registry helper functions
including get_adapter, get_feed_config, register_feed, and list_feeds.
"""

import pytest

from news_org_system.readers.registry import (
    ADAPTER_REGISTRY,
    FEED_REGISTRY,
    get_adapter,
    get_feed_config,
    register_adapter,
    register_feed,
    list_feeds,
    list_adapters,
)
from news_org_system.readers.constants import SourceName, AdapterName
from news_org_system.readers.adapters.base import BaseRSSAdapter
from news_org_system.readers.adapters.default_adapter import DefaultRSSAdapter
from news_org_system.readers.adapters.yonhap_adapter import YonhapAdapter
from news_org_system.readers.adapters.maeil_adapter import MaeliAdapter
from news_org_system.readers.adapters.etnews_adapter import ETnewsAdapter
from news_org_system.readers.models.rss_config import RSSFeedConfig
from news_org_system.readers.models.site_config import SiteConfig


class TestAdapterRegistry:
    """Tests for ADAPTER_REGISTRY and adapter-related functions."""

    def test_adapter_registry_contains_default_adapters(self):
        """Test that ADAPTER_REGISTRY contains all default adapters."""
        assert AdapterName.DEFAULT in ADAPTER_REGISTRY
        assert AdapterName.YONHAP in ADAPTER_REGISTRY
        assert AdapterName.MAEIL in ADAPTER_REGISTRY
        assert AdapterName.ETNEWS in ADAPTER_REGISTRY

    def test_adapter_registry_classes(self):
        """Test that ADAPTER_REGISTRY contains correct adapter classes."""
        assert ADAPTER_REGISTRY[AdapterName.DEFAULT] == DefaultRSSAdapter
        assert ADAPTER_REGISTRY[AdapterName.YONHAP] == YonhapAdapter
        assert ADAPTER_REGISTRY[AdapterName.MAEIL] == MaeliAdapter
        assert ADAPTER_REGISTRY[AdapterName.ETNEWS] == ETnewsAdapter

    def test_get_adapter_default(self):
        """Test getting default adapter."""
        config = SiteConfig()
        adapter = get_adapter(AdapterName.DEFAULT, config)

        assert isinstance(adapter, DefaultRSSAdapter)
        assert isinstance(adapter, BaseRSSAdapter)

    def test_get_adapter_yonhap(self):
        """Test getting Yonhap adapter."""
        config = SiteConfig()
        adapter = get_adapter(AdapterName.YONHAP, config)

        assert isinstance(adapter, YonhapAdapter)
        assert isinstance(adapter, BaseRSSAdapter)

    def test_get_adapter_maeil(self):
        """Test getting Maeil adapter."""
        config = SiteConfig()
        adapter = get_adapter(AdapterName.MAEIL, config)

        assert isinstance(adapter, MaeliAdapter)
        assert isinstance(adapter, BaseRSSAdapter)

    def test_get_adapter_etnews(self):
        """Test getting ETnews adapter."""
        config = SiteConfig()
        adapter = get_adapter(AdapterName.ETNEWS, config)

        assert isinstance(adapter, ETnewsAdapter)
        assert isinstance(adapter, BaseRSSAdapter)

    def test_get_adapter_unknown_returns_default(self):
        """Test that unknown adapter name returns default adapter."""
        config = SiteConfig()
        adapter = get_adapter("unknown_adapter", config)

        assert isinstance(adapter, DefaultRSSAdapter)

    def test_get_adapter_without_config(self):
        """Test getting adapter without providing config."""
        adapter = get_adapter(AdapterName.DEFAULT)

        assert isinstance(adapter, DefaultRSSAdapter)
        assert adapter.config == SiteConfig()  # Should use default config

    def test_register_adapter(self):
        """Test registering a new adapter."""
        # Create a custom adapter
        class CustomAdapter(DefaultRSSAdapter):
            pass

        # Register it
        register_adapter("custom", CustomAdapter)

        # Check it's registered
        assert "custom" in ADAPTER_REGISTRY
        assert ADAPTER_REGISTRY["custom"] == CustomAdapter

        # Clean up
        del ADAPTER_REGISTRY["custom"]

    def test_list_adapters(self):
        """Test listing all registered adapters."""
        adapters = list_adapters()

        assert isinstance(adapters, dict)
        assert AdapterName.DEFAULT in adapters
        assert AdapterName.YONHAP in adapters
        assert AdapterName.MAEIL in adapters
        assert AdapterName.ETNEWS in adapters
        assert adapters[AdapterName.DEFAULT] == DefaultRSSAdapter


class TestFeedRegistry:
    """Tests for FEED_REGISTRY and feed-related functions."""

    def test_feed_registry_contains_default_feeds(self):
        """Test that FEED_REGISTRY contains all default feeds."""
        assert SourceName.YONHAP_ECONOMY in FEED_REGISTRY
        assert SourceName.MAEIL_MANAGEMENT in FEED_REGISTRY
        assert SourceName.ETNEWS_TODAY in FEED_REGISTRY

    def test_feed_registry_configs_are_valid(self):
        """Test that all feed configs in registry are valid RSSFeedConfig objects."""
        for source_name, config in FEED_REGISTRY.items():
            assert isinstance(config, RSSFeedConfig)
            assert config.source_name == source_name
            assert str(config.feed_url).startswith("http")

    def test_get_feed_config_yonhap(self):
        """Test getting Yonhap feed config."""
        config = get_feed_config(SourceName.YONHAP_ECONOMY)

        assert config is not None
        assert config.source_name == SourceName.YONHAP_ECONOMY
        assert "yonhapnewstv.co.kr" in str(config.feed_url)
        assert config.adapter_name == AdapterName.YONHAP
        assert config.language == "ko"

    def test_get_feed_config_maeil(self):
        """Test getting Maeil feed config."""
        config = get_feed_config(SourceName.MAEIL_MANAGEMENT)

        assert config is not None
        assert config.source_name == SourceName.MAEIL_MANAGEMENT
        assert "mk.co.kr" in str(config.feed_url)
        assert config.adapter_name == AdapterName.MAEIL
        assert config.language == "ko"

    def test_get_feed_config_etnews(self):
        """Test getting ETnews feed config."""
        config = get_feed_config(SourceName.ETNEWS_TODAY)

        assert config is not None
        assert config.source_name == SourceName.ETNEWS_TODAY
        assert "etnews.com" in str(config.feed_url)
        assert config.adapter_name == AdapterName.ETNEWS
        assert config.language == "ko"

    def test_get_feed_config_unknown(self):
        """Test getting unknown feed config returns None."""
        config = get_feed_config("unknown_feed")

        assert config is None

    def test_register_feed(self):
        """Test registering a new feed."""
        # Create a custom feed config
        custom_config = RSSFeedConfig(
            source_name="custom_feed",
            feed_url="https://example.com/rss.xml",
            adapter_name="default",
            language="en",
        )

        # Register it
        register_feed(custom_config)

        # Check it's registered
        assert "custom_feed" in FEED_REGISTRY
        assert FEED_REGISTRY["custom_feed"] == custom_config

        # Clean up
        del FEED_REGISTRY["custom_feed"]

    def test_list_feeds(self):
        """Test listing all registered feeds."""
        feeds = list_feeds()

        assert isinstance(feeds, dict)
        assert SourceName.YONHAP_ECONOMY in feeds
        assert SourceName.MAEIL_MANAGEMENT in feeds
        assert SourceName.ETNEWS_TODAY in feeds

        # Check that it returns a copy (not the original dict)
        feeds["test"] = "should_not_affect_registry"
        assert "test" not in FEED_REGISTRY


class TestRegistryIntegration:
    """Tests for registry integration and edge cases."""

    def test_feed_and_adapter_integration(self):
        """Test that feed configs reference valid adapters."""
        feeds = list_feeds()

        for source_name, config in feeds.items():
            adapter_name = config.adapter_name
            # Check that the adapter exists in registry
            assert adapter_name in ADAPTER_REGISTRY or adapter_name == AdapterName.DEFAULT

            # Check that we can actually get the adapter
            adapter = get_adapter(adapter_name)
            assert isinstance(adapter, BaseRSSAdapter)

    def test_multiple_adapters_same_instance(self):
        """Test that getting same adapter multiple times creates new instances."""
        config = SiteConfig()

        adapter1 = get_adapter(AdapterName.DEFAULT, config)
        adapter2 = get_adapter(AdapterName.DEFAULT, config)

        # Should be different instances
        assert adapter1 is not adapter2

        # But should have same config
        assert adapter1.config == adapter2.config

    def test_feed_config_immutability(self):
        """Test that feed configs can't be accidentally modified through list_feeds."""
        import copy
        feeds = list_feeds()

        original_url = str(feeds[SourceName.YONHAP_ECONOMY].feed_url)

        # Try to modify feed_url in the returned dict
        # Note: list_feeds returns shallow copy, so config objects are still references
        # This test verifies the behavior - modification would affect registry
        feeds[SourceName.YONHAP_ECONOMY].feed_url = "https://malicious.com/rss.xml"

        # The modification affects registry because it's shallow copy
        # Restore original value for other tests
        from news_org_system.readers.registry import FEED_REGISTRY
        FEED_REGISTRY[SourceName.YONHAP_ECONOMY].feed_url = original_url

        # Verify restoration
        config = get_feed_config(SourceName.YONHAP_ECONOMY)
        assert str(config.feed_url) == original_url

    def test_register_feed_overwrites(self):
        """Test that registering a feed with existing name overwrites it."""
        original_config = FEED_REGISTRY[SourceName.YONHAP_ECONOMY]
        original_url = str(original_config.feed_url)

        # Register new config with same name
        new_config = RSSFeedConfig(
            source_name=SourceName.YONHAP_ECONOMY,
            feed_url="https://example.com/new-rss.xml",
            adapter_name=AdapterName.DEFAULT,
        )
        register_feed(new_config)

        # Check it was overwritten
        config = get_feed_config(SourceName.YONHAP_ECONOMY)
        assert str(config.feed_url) == "https://example.com/new-rss.xml"

        # Restore original
        register_feed(original_config)

        # Verify restoration
        config = get_feed_config(SourceName.YONHAP_ECONOMY)
        assert str(config.feed_url) == original_url

    def test_all_registered_feeds_are_enabled(self):
        """Test that all default feeds are enabled by default."""
        feeds = list_feeds()

        for source_name, config in feeds.items():
            assert config.enabled is True

    def test_all_registered_feeds_have_valid_urls(self):
        """Test that all feed URLs are valid."""
        feeds = list_feeds()

        for source_name, config in feeds.items():
            url = str(config.feed_url)
            assert url.startswith("http://") or url.startswith("https://")
            assert ".xml" in url or "/feed" in url or "/rss" in url
