"""Article-related API models."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ArticleResponse(BaseModel):
    """Response model for a single article."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    id: Optional[str] = Field(None, description="MongoDB document ID")
    source: str = Field(..., description="News source name")
    url: str = Field(..., description="Article URL")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    published_at: datetime = Field(..., description="Publication timestamp")
    crawled_at: datetime = Field(..., description="Crawl timestamp")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")


class ArticleListResponse(BaseModel):
    """Response model for paginated article list."""

    articles: List[ArticleResponse] = Field(
        ..., description="List of articles"
    )
    total: int = Field(..., description="Total number of matching articles", ge=0)
    page: int = Field(..., description="Current page number", ge=1)
    page_size: int = Field(..., description="Number of articles per page", ge=1, le=100)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
    warning: Optional[str] = Field(None, description="Warning message if applicable")
