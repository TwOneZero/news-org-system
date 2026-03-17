"""Feed and adapter registry for RSS readers."""

from typing import Dict, Type, Optional

from .adapters.base import BaseRSSAdapter
from .adapters.default_adapter import DefaultRSSAdapter
from .adapters.yonhap_adapter import YonhapAdapter
from .adapters.maeil_adapter import MaeliAdapter
from .adapters.etnews_adapter import ETnewsAdapter
from .models.rss_config import RSSFeedConfig
from .models.site_config import SiteConfig


# Adapter registry - maps adapter names to adapter classes
ADAPTER_REGISTRY: Dict[str, Type[BaseRSSAdapter]] = {
    "default": DefaultRSSAdapter,
    "yonhap": YonhapAdapter,
    "maeil": MaeliAdapter,
    "etnews": ETnewsAdapter,
}


# Feed registry - maps source names to feed configurations
FEED_REGISTRY: Dict[str, RSSFeedConfig] = {
    "yonhap_economy": RSSFeedConfig(
        source_name="yonhap_economy",
        feed_url="https://www.yonhapnewstv.co.kr/category/news/economy/feed",
        adapter_name="yonhap",
        language="ko",
    ),
    "maeil_management": RSSFeedConfig(
        source_name="maeil_management",
        feed_url="https://www.mk.co.kr/rss/50100032/",
        adapter_name="maeil",
        language="ko",
    ),
    "etnews_today": RSSFeedConfig(
        source_name="etnews_today",
        feed_url="https://rss.etnews.com/Section901.xml",
        adapter_name="etnews",
        language="ko",
    ),
}


def get_adapter(
    adapter_name: str, config: Optional[SiteConfig] = None
) -> BaseRSSAdapter:
    """Get an adapter instance by name.

    Args:
        adapter_name: Name of the adapter (e.g., 'yonhap', 'maeil', 'etnews')
        config: Site configuration for the adapter

    Returns:
        Instantiated adapter object

    Example:
        >>> adapter = get_adapter("yonhap", SiteConfig())
        >>> content = adapter.extract_content(entry)
    """
    adapter_class = ADAPTER_REGISTRY.get(adapter_name, DefaultRSSAdapter)
    site_config = config or SiteConfig()
    return adapter_class(site_config)


def get_feed_config(source_name: str) -> Optional[RSSFeedConfig]:
    """Get feed configuration by source name.

    Args:
        source_name: Name of the news source

    Returns:
        RSSFeedConfig if found, None otherwise

    Example:
        >>> config = get_feed_config("yonhap_economy")
        >>> print(config.feed_url)
    """
    return FEED_REGISTRY.get(source_name)


def register_adapter(name: str, adapter_class: Type[BaseRSSAdapter]) -> None:
    """Register a new adapter.

    Allows dynamic registration of custom adapters at runtime.

    Args:
        name: Name for the adapter
        adapter_class: Adapter class to register

    Example:
        >>> class MyAdapter(DefaultRSSAdapter):
        ...     pass
        >>> register_adapter("my_source", MyAdapter)
    """
    ADAPTER_REGISTRY[name] = adapter_class


def register_feed(config: RSSFeedConfig) -> None:
    """Register a new feed configuration.

    Allows dynamic registration of custom feeds at runtime.

    Args:
        config: RSSFeedConfig object with feed details

    Example:
        >>> config = RSSFeedConfig(
        ...     source_name="my_source",
        ...     feed_url="https://example.com/rss",
        ...     adapter_name="default"
        ... )
        >>> register_feed(config)
    """
    FEED_REGISTRY[config.source_name] = config


def list_feeds() -> Dict[str, RSSFeedConfig]:
    """List all registered feeds.

    Returns:
        Dictionary mapping source names to feed configurations

    Example:
        >>> feeds = list_feeds()
        >>> for name, config in feeds.items():
        ...     print(f"{name}: {config.feed_url}")
    """
    return FEED_REGISTRY.copy()


def list_adapters() -> Dict[str, Type[BaseRSSAdapter]]:
    """List all registered adapters.

    Returns:
        Dictionary mapping adapter names to adapter classes

    Example:
        >>> adapters = list_adapters()
        >>> for name, adapter_class in adapters.items():
        ...     print(f"{name}: {adapter_class.__name__}")
    """
    return ADAPTER_REGISTRY.copy()
