"""FastAPI dependency functions for request handlers."""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status

from ..services import (
    NewsCollectionService,
    ArticleQueryService,
    StatisticsService,
)
from ..storage import MongoStore

logger = logging.getLogger(__name__)

# Module-level singleton for MongoStore
_store: Optional[MongoStore] = None


def get_store() -> MongoStore:
    """Get the singleton MongoStore instance."""
    global _store
    if _store is None:
        logger.info("Initializing MongoStore singleton")
        _store = MongoStore()
        logger.info(f"MongoStore initialized: database={_store.db.name}")
    return _store


def get_collection_service(
    store: MongoStore = Depends(get_store)
) -> NewsCollectionService:
    """Get NewsCollectionService instance for collection operations."""
    return NewsCollectionService(store=store)


def get_query_service(
    store: MongoStore = Depends(get_store)
) -> ArticleQueryService:
    """Get ArticleQueryService instance for query operations."""
    return ArticleQueryService(store=store)


def get_stats_service(
    store: MongoStore = Depends(get_store)
) -> StatisticsService:
    """Get StatisticsService instance for statistics operations."""
    return StatisticsService(store=store)
