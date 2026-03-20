"""Query endpoints for retrieving articles."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...services import ArticleQueryService
from ...storage import MongoStore
from ..dependencies import get_query_service
from ..models.articles import ArticleResponse, ArticleListResponse

router = APIRouter()


@router.get(
    "/articles",
    response_model=ArticleListResponse,
    status_code=status.HTTP_200_OK,
    summary="Query articles with filters",
    description="Retrieve articles with optional filtering and pagination",
)
async def query_articles(
    source: str = Query(None, description="Filter by source name"),
    start_date: datetime = Query(None, description="Filter articles after this date"),
    end_date: datetime = Query(None, description="Filter articles before this date"),
    keyword: str = Query(None, description="Search keyword in title or content"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of articles per page"),
    service: ArticleQueryService = Depends(get_query_service),
):
    """Query articles with filters and pagination.

    Args:
        source: Optional source name filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        keyword: Optional keyword search
        page: Page number (1-indexed)
        page_size: Articles per page (max 100)
        service: ArticleQueryService instance

    Returns:
        ArticleListResponse with paginated results
    """
    result = service.query_articles(
        source=source,
        start_date=start_date,
        end_date=end_date,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    # Convert articles to ArticleResponse models
    articles = [ArticleResponse(**article) for article in result["articles"]]

    return ArticleListResponse(
        articles=articles,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
        warning=result.get("warning"),
    )


@router.get(
    "/articles/{article_id}",
    response_model=ArticleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single article",
    description="Retrieve a single article by its ID",
)
async def get_article(
    article_id: str,
    service: ArticleQueryService = Depends(get_query_service),
):
    """Get a single article by ID.

    Args:
        article_id: MongoDB ObjectId of the article
        service: ArticleQueryService instance

    Returns:
        ArticleResponse

    Raises:
        HTTPException 404: If article not found
    """
    article = service.get_article_by_id(article_id)

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id '{article_id}' not found",
        )

    return ArticleResponse(**article)
