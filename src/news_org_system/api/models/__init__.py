"""API models for request/response DTOs."""

from .articles import (
    ArticleListResponse,
    ArticleResponse,
)
from .collection import (
    CollectionRequest,
    CollectionResponse,
    SourceSummary,
)
from .common import ErrorResponse
from .stats import (
    SourceStats,
    StatisticsResponse,
)

__all__ = [
    "ArticleResponse",
    "ArticleListResponse",
    "CollectionRequest",
    "CollectionResponse",
    "SourceSummary",
    "ErrorResponse",
    "StatisticsResponse",
    "SourceStats",
]
