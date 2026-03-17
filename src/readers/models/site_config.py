"""Site-specific configuration for RSS parsing and web scraping."""

from pydantic import BaseModel, Field


class SiteConfig(BaseModel):
    """Configuration for site-specific content extraction.

    Used by adapters to configure behavior for web scraping fallback
    and site-specific parsing logic.
    """

    language: str = "ko"
    browser_user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36",
        description="User agent string for HTTP requests",
    )
    request_timeout: int = Field(default=15, ge=1, le=300)
    memoize_articles: bool = False
    min_content_length: int = Field(
        default=300, ge=0, description="Minimum content length to use RSS content directly"
    )
