"""Collection endpoints for triggering news collection."""

from fastapi import APIRouter, Depends, HTTPException, status

from ...services import NewsCollectionService
from ...storage import MongoStore
from ..dependencies import get_collection_service
from ..models.collection import (
    CollectionRequest,
    CollectionResponse,
    SingleSourceCollectionResponse,
    SourceSummary,
)

router = APIRouter()


@router.post(
    "/collect",
    response_model=CollectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Collect articles from all feeds",
    description="Trigger news collection from all configured RSS feeds",
)
async def collect_all(
    request: CollectionRequest = None,
    service: NewsCollectionService = Depends(get_collection_service),
):
    """Collect articles from all configured feeds.

    Args:
        request: Collection parameters (days_back, limit)
        service: NewsCollectionService instance

    Returns:
        CollectionResponse with results from all sources
    """
    if request is None:
        request = CollectionRequest()

    result = service.collect_all(
        days_back=request.days_back,
        limit=request.limit,
    )

    # Convert source results to SourceSummary models
    sources = {}
    for source_name, source_result in result["sources"].items():
        sources[source_name] = SourceSummary(**source_result)

    return CollectionResponse(
        timestamp=result["timestamp"],
        start_date=result["start_date"],
        end_date=result["end_date"],
        total_fetched=result["total_fetched"],
        total_saved=result["total_saved"],
        sources=sources,
    )


@router.post(
    "/collect/{source_name}",
    response_model=SingleSourceCollectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Collect articles from a specific feed",
    description="Trigger news collection from a single RSS feed",
)
async def collect_from_source(
    source_name: str,
    request: CollectionRequest = None,
    service: NewsCollectionService = Depends(get_collection_service),
):
    """Collect articles from a specific feed.

    Args:
        source_name: Name of the feed to collect from
        request: Collection parameters (days_back, limit)
        service: NewsCollectionService instance

    Returns:
        SingleSourceCollectionResponse with results

    Raises:
        HTTPException 404: If source_name is not found
        HTTPException 500: If collection fails
    """
    if request is None:
        request = CollectionRequest()

    try:
        result = service.collect_from_source(
            source_name=source_name,
            days_back=request.days_back,
            limit=request.limit,
        )

        if result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Collection failed"),
            )

        return SingleSourceCollectionResponse(**result)

    except ValueError as e:
        # Source not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Collection failed: {str(e)}",
        )
