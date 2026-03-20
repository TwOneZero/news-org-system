"""Statistics-related API models."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DateRange(BaseModel):
    """Date range for articles."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    oldest: Optional[datetime] = Field(None, description="Oldest article timestamp")
    newest: Optional[datetime] = Field(None, description="Newest article timestamp")


class SourceStats(BaseModel):
    """Statistics for a single source."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    source: str = Field(..., description="Source name")
    feed_url: str = Field(..., description="Feed URL")
    adapter_name: str = Field(..., description="Adapter name")
    total_articles: int = Field(..., description="Total articles from this source", ge=0)
    oldest_article: Optional[datetime] = Field(
        None, description="Oldest article timestamp"
    )
    newest_article: Optional[datetime] = Field(
        None, description="Newest article timestamp"
    )


class StatisticsResponse(BaseModel):
    """Response model for overall statistics."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    total_articles: int = Field(..., description="Total articles in database", ge=0)
    total_sources: int = Field(..., description="Number of configured sources", ge=0)
    by_source: Dict[str, int] = Field(
        ..., description="Article count per source"
    )
    date_range: DateRange = Field(..., description="Date range of all articles")
    last_collection: Optional[datetime] = Field(
        None, description="Last collection timestamp"
    )
    generated_at: str = Field(..., description="Statistics generation timestamp")


class CollectionHistoryEntry(BaseModel):
    """Single entry in collection history."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    timestamp: datetime = Field(..., description="Collection timestamp")
    source: str = Field(..., description="Source name")
    articles_collected: int = Field(..., description="Number of articles collected")
