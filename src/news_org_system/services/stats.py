"""Service for collection statistics."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..readers.registry import FEED_REGISTRY
from ..storage import MongoStore

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for providing collection statistics.

    This service provides aggregate and per-source statistics about
    collected articles.
    """

    def __init__(self, store: MongoStore, registry: Optional[Dict] = None):
        """Initialize the statistics service.

        Args:
            store: MongoStore instance for querying statistics
            registry: Feed registry (defaults to FEED_REGISTRY)
        """
        self.store = store
        self.registry = registry or FEED_REGISTRY

    def get_overall_stats(self) -> Dict:
        """Get overall collection statistics.

        Returns:
            Dictionary with overall statistics:
            {
                "total_articles": int,
                "total_sources": int,
                "by_source": Dict[str, int],
                "date_range": {
                    "oldest": Optional[datetime],
                    "newest": Optional[datetime]
                },
                "last_collection": Optional[datetime]
            }
        """
        # Get base statistics from store
        base_stats = self.store.get_stats()

        # Get date range
        oldest = self.store.articles_collection.find_one(sort=[("published_at", 1)])
        newest = self.store.articles_collection.find_one(sort=[("published_at", -1)])

        date_range = {
            "oldest": oldest.get("published_at") if oldest else None,
            "newest": newest.get("published_at") if newest else None,
        }

        # Get last collection timestamp (most recent crawled_at)
        last_collected = self.store.articles_collection.find_one(
            sort=[("crawled_at", -1)]
        )
        last_collection = last_collected.get("crawled_at") if last_collected else None

        return {
            "total_articles": base_stats["total"],
            "total_sources": len(self.registry),
            "by_source": base_stats["by_source"],
            "date_range": date_range,
            "last_collection": last_collection,
            "generated_at": datetime.now().isoformat(),
        }

    def get_source_stats(self, source_name: str) -> Optional[Dict]:
        """Get statistics for a specific source.

        Args:
            source_name: Name of the source

        Returns:
            Dictionary with source statistics or None if source not found
        """
        if source_name not in self.registry:
            logger.warning(f"Source '{source_name}' not found in registry")
            return None

        # Count articles for this source
        count = self.store.articles_collection.count_documents(
            {"source": source_name}
        )

        # Get date range for this source
        oldest = self.store.articles_collection.find_one(
            {"source": source_name}, sort=[("published_at", 1)]
        )
        newest = self.store.articles_collection.find_one(
            {"source": source_name}, sort=[("published_at", -1)]
        )

        # Get feed config
        feed_config = self.registry[source_name]

        return {
            "source": source_name,
            "feed_url": feed_config.feed_url,
            "adapter_name": feed_config.adapter_name,
            "total_articles": count,
            "oldest_article": oldest.get("published_at") if oldest else None,
            "newest_article": newest.get("published_at") if newest else None,
        }

    def get_all_sources_summary(self) -> List[Dict]:
        """Get summary statistics for all sources.

        Returns:
            List of source statistics dictionaries
        """
        summaries = []

        for source_name in self.registry.keys():
            stats = self.get_source_stats(source_name)
            if stats:
                summaries.append(stats)

        # Sort by article count descending
        summaries.sort(key=lambda x: x["total_articles"], reverse=True)

        return summaries

    def get_collection_history(
        self, limit: int = 20
    ) -> List[Dict]:
        """Get recent collection history.

        Note: This is a simplified implementation. For a production system,
        you would want to store collection operations in a separate collection.

        Args:
            limit: Maximum number of history entries to return

        Returns:
            List of recent collection operations (grouped by crawl timestamp)
        """
        # Group articles by crawl timestamp and source
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "crawled_at": "$crawled_at",
                        "source": "$source",
                    },
                    "count": {"$sum": 1},
                }
            },
            {"sort": {"_id.crawled_at": -1}},
            {"limit": limit},
        ]

        results = list(self.store.articles_collection.aggregate(pipeline))

        history = []
        for result in results:
            history.append(
                {
                    "timestamp": result["_id"]["crawled_at"],
                    "source": result["_id"]["source"],
                    "articles_collected": result["count"],
                }
            )

        return history
