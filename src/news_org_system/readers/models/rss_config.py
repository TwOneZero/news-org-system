"""RSS feed configuration models using Pydantic."""

from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List
from datetime import datetime


class RSSItem(BaseModel):
    """Common RSS item fields with validation.

    Represents a standardized article/item from RSS/Atom feeds.
    Uses Field aliases to map from different feed formats.
    """

    title: str
    url: str = Field(alias="link")
    content: str
    published_at: datetime
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    summary: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL is not empty."""
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        return v.strip()

    @field_validator("title", "content")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class RSSFeedConfig(BaseModel):
    """Configuration for a single RSS feed.

    Attributes:
        source_name: Unique identifier for this news source
        feed_url: URL of the RSS/Atom feed
        adapter_name: Name of the adapter to use for parsing
        enabled: Whether this feed is active
        language: Content language for NLP/processing
    """

    source_name: str
    feed_url: HttpUrl
    adapter_name: str = "default"
    enabled: bool = True
    language: str = "ko"

    @field_validator("source_name")
    @classmethod
    def validate_source_name(cls, v: str) -> str:
        """Validate source name is not empty and is alphanumeric with underscores."""
        if not v or not v.strip():
            raise ValueError("source_name cannot be empty")
        if not v.replace("_", "").isalnum():
            raise ValueError(
                "source_name must be alphanumeric with underscores only"
            )
        return v.strip()
