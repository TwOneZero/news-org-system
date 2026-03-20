"""Service layer for news collection system.

This module provides business logic services that can be used by both CLI and API layers.
"""

from .collection import NewsCollectionService
from .query import ArticleQueryService
from .stats import StatisticsService

__all__ = ["NewsCollectionService", "ArticleQueryService", "StatisticsService"]
