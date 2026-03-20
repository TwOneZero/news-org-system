"""Collection-related API models."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CollectionRequest(BaseModel):
    """Request model for triggering collection."""

    days_back: int = Field(
        default=1,
        ge=1,
        le=30,
        description="Number of days to look back for articles"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum articles to collect per source"
    )


class SourceSummary(BaseModel):
    """Summary of collection results for a single source."""

    source: str = Field(..., description="Source name")
    fetched: int = Field(..., description="Number of articles fetched", ge=0)
    saved: int = Field(..., description="Number of new articles saved", ge=0)
    skipped: int = Field(..., description="Number of duplicate articles skipped", ge=0)
    status: str = Field(..., description="Collection status: success or error")
    error: Optional[str] = Field(None, description="Error message if status is error")


class CollectionResponse(BaseModel):
    """Response model for collection operation."""

    timestamp: str = Field(..., description="Operation timestamp")
    start_date: str = Field(..., description="Collection start date (ISO format)")
    end_date: str = Field(..., description="Collection end date (ISO format)")
    total_fetched: int = Field(..., description="Total articles fetched", ge=0)
    total_saved: int = Field(..., description="Total new articles saved", ge=0)
    sources: Dict[str, SourceSummary] = Field(
        ..., description="Per-source collection results"
    )


class SingleSourceCollectionResponse(BaseModel):
    """Response model for single source collection."""

    source: str = Field(..., description="Source name")
    timestamp: str = Field(..., description="Operation timestamp")
    start_date: str = Field(..., description="Collection start date (ISO format)")
    end_date: str = Field(..., description="Collection end date (ISO format)")
    fetched: int = Field(..., description="Number of articles fetched", ge=0)
    saved: int = Field(..., description="Number of new articles saved", ge=0)
    skipped: int = Field(..., description="Number of duplicate articles skipped", ge=0)
    status: str = Field(..., description="Collection status: success or error")
    error: Optional[str] = Field(None, description="Error message if status is error")
