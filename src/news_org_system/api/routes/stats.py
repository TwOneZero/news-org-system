"""Statistics endpoints for collection metrics."""

from fastapi import APIRouter, Depends, HTTPException, status

from ...services import StatisticsService
from ...storage import MongoStore
from ..dependencies import get_stats_service
from ..models.stats import StatisticsResponse, SourceStats, CollectionHistoryEntry

router = APIRouter()


@router.get(
    "/stats",
    response_model=StatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get overall statistics",
    description="Retrieve aggregate statistics about the news collection",
)
async def get_overall_stats(
    service: StatisticsService = Depends(get_stats_service),
):
    """Get overall collection statistics.

    Args:
        service: StatisticsService instance

    Returns:
        StatisticsResponse with overall statistics
    """
    stats = service.get_overall_stats()

    return StatisticsResponse(**stats)


@router.get(
    "/stats/{source_name}",
    response_model=SourceStats,
    status_code=status.HTTP_200_OK,
    summary="Get statistics for a specific source",
    description="Retrieve detailed statistics for a single news source",
)
async def get_source_stats(
    source_name: str,
    service: StatisticsService = Depends(get_stats_service),
):
    """Get statistics for a specific source.

    Args:
        source_name: Name of the source
        service: StatisticsService instance

    Returns:
        SourceStats with source-specific statistics

    Raises:
        HTTPException 404: If source not found
    """
    stats = service.get_source_stats(source_name)

    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_name}' not found in registry",
        )

    return SourceStats(**stats)


@router.get(
    "/stats/history",
    response_model=list[CollectionHistoryEntry],
    status_code=status.HTTP_200_OK,
    summary="Get collection history",
    description="Retrieve recent collection operation history",
)
async def get_collection_history(
    limit: int = 20,
    service: StatisticsService = Depends(get_stats_service),
):
    """Get recent collection history.

    Args:
        limit: Maximum number of history entries to return
        service: StatisticsService instance

    Returns:
        List of CollectionHistoryEntry
    """
    history = service.get_collection_history(limit=limit)

    return [CollectionHistoryEntry(**entry) for entry in history]
