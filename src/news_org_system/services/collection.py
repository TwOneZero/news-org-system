"""Service for collecting news articles from RSS feeds."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..readers import RSSReader
from ..readers.registry import FEED_REGISTRY
from ..storage import MongoStore

logger = logging.getLogger(__name__)


class NewsCollectionService:
    """Service for collecting news articles from configured RSS feeds.

    This service provides methods to collect articles from all configured feeds
    or from a specific feed. It handles errors gracefully and provides detailed
    collection results.
    """

    def __init__(self, store: MongoStore, registry: Optional[Dict] = None):
        """Initialize the collection service.

        Args:
            store: MongoStore instance for persisting articles
            registry: Feed registry (defaults to FEED_REGISTRY)
        """
        self.store = store
        self.registry = registry or FEED_REGISTRY
        self._readers: Optional[Dict[str, RSSReader]] = None

    @property
    def readers(self) -> Dict[str, RSSReader]:
        """Lazy-load RSS readers for all configured feeds.

        Returns:
            Dictionary mapping source names to RSSReader instances
        """
        if self._readers is None:
            self._readers = {}
            for source_name in self.registry.keys():
                try:
                    self._readers[source_name] = RSSReader.from_source(source_name)
                except Exception as e:
                    logger.warning(f"Failed to create reader for {source_name}: {e}")
        return self._readers

    def collect_all(
        self,
        days_back: int = 1,
        limit: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """Collect articles from all configured feeds.

        Args:
            days_back: Number of days to look back (used if start_date not provided)
            limit: Maximum articles per source
            start_date: Start date for collection (optional)
            end_date: End date for collection (optional)

        Returns:
            Dictionary with collection results:
            {
                "timestamp": str,
                "total_fetched": int,
                "total_saved": int,
                "sources": {
                    "source_name": {
                        "fetched": int,
                        "saved": int,
                        "skipped": int
                    }
                }
            }
        """
        if start_date is None:
            from datetime import timedelta

            start_date = datetime.now() - timedelta(days=days_back)
        if end_date is None:
            end_date = datetime.now()

        results = {
            "timestamp": datetime.now().isoformat(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_fetched": 0,
            "total_saved": 0,
            "sources": {},
        }

        for source_name, reader in self.readers.items():
            try:
                # Fetch articles
                articles = reader.fetch(
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                )

                results["total_fetched"] += len(articles)

                # Save to storage
                save_result = self.store.save_articles(articles)

                results["sources"][source_name] = {
                    "fetched": len(articles),
                    "saved": save_result.get("saved", 0),
                    "skipped": save_result.get("skipped", 0),
                    "status": "success",
                }
                results["total_saved"] += save_result.get("saved", 0)

                logger.info(
                    f"Collected {save_result.get('saved', 0)} articles from {source_name}"
                )

            except Exception as e:
                logger.error(f"Error collecting from {source_name}: {e}")
                results["sources"][source_name] = {
                    "fetched": 0,
                    "saved": 0,
                    "skipped": 0,
                    "status": "error",
                    "error": str(e),
                }

        return results

    def collect_from_source(
        self,
        source_name: str,
        days_back: int = 1,
        limit: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """Collect articles from a specific feed.

        Args:
            source_name: Name of the feed to collect from
            days_back: Number of days to look back (used if start_date not provided)
            limit: Maximum articles to collect
            start_date: Start date for collection (optional)
            end_date: End date for collection (optional)

        Returns:
            Dictionary with collection results

        Raises:
            ValueError: If source_name is not found in registry
        """
        if source_name not in self.registry:
            raise ValueError(
                f"Source '{source_name}' not found in registry. "
                f"Available sources: {list(self.registry.keys())}"
            )

        if start_date is None:
            from datetime import timedelta

            start_date = datetime.now() - timedelta(days=days_back)
        if end_date is None:
            end_date = datetime.now()

        # Get or create reader for this source
        if source_name not in self.readers:
            try:
                self._readers[source_name] = RSSReader.from_source(source_name)
            except Exception as e:
                raise RuntimeError(f"Failed to create reader for {source_name}: {e}")

        reader = self.readers[source_name]

        try:
            # Fetch articles
            articles = reader.fetch(
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            )

            # Save to storage
            save_result = self.store.save_articles(articles)

            result = {
                "source": source_name,
                "timestamp": datetime.now().isoformat(),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "fetched": len(articles),
                "saved": save_result.get("saved", 0),
                "skipped": save_result.get("skipped", 0),
                "status": "success",
            }

            logger.info(
                f"Collected {save_result.get('saved', 0)} articles from {source_name}"
            )

            return result

        except Exception as e:
            logger.error(f"Error collecting from {source_name}: {e}")
            return {
                "source": source_name,
                "timestamp": datetime.now().isoformat(),
                "fetched": 0,
                "saved": 0,
                "skipped": 0,
                "status": "error",
                "error": str(e),
            }

    def list_sources(self) -> List[Dict[str, str]]:
        """List all configured feed sources.

        Returns:
            List of dictionaries with source information:
            [
                {
                    "source_name": str,
                    "feed_url": str,
                    "adapter_name": str
                }
            ]
        """
        sources = []
        for source_name, config in self.registry.items():
            sources.append(
                {
                    "source_name": source_name,
                    "feed_url": config.feed_url,
                    "adapter_name": config.adapter_name,
                }
            )
        return sources
