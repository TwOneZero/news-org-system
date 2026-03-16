"""RSS feed reader for news articles."""

import feedparser
from datetime import datetime
from typing import List, Optional
from newspaper import Article as NewspaperArticle
from bs4 import BeautifulSoup

from .base_reader import BaseReader, Article


class RSSReader(BaseReader):
    """Reader for RSS/Atom news feeds.

    Supports multiple Korean news sources including Yonhap, Maeil
    """

    # RSS feed URLs for popular Korean news sources
    # 연합뉴스 (경제), 매일경제 (기업/경영), bbc
    FEED_URLS = {
        "yonhap_economy": "https://www.yonhapnewstv.co.kr/category/news/economy/feed",
        "maeil_management": "https://www.mk.co.kr/rss/50100032/",
        "bbc": "https://feeds.bbci.co.uk/news/rss.xml",
    }

    def __init__(self, source_name: str = "rss", feed_url: Optional[str] = None):
        """Initialize the RSS reader.

        Args:
            source_name: Name identifier for this source
            feed_url: Custom RSS feed URL (if not using predefined feeds)
        """
        super().__init__(source_name)
        self.feed_url = feed_url

    def fetch(
        self,
        limit: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Article]:
        """Fetch articles from RSS feed.

        Args:
            limit: Maximum number of articles to fetch
            start_date: Filter articles published after this date
            end_date: Filter articles published before this date

        Returns:
            List of Article objects with full content extracted
        """
        articles = []

        # Determine which feed(s) to fetch
        feeds_to_fetch = (
            [self.feed_url] if self.feed_url else list(self.FEED_URLS.values())
        )

        for feed_url in feeds_to_fetch:
            if not feed_url:
                continue

            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    # Apply date filters
                    published_date = self._parse_date(entry)
                    if start_date and published_date < start_date:
                        continue
                    if end_date and published_date > end_date:
                        continue

                    # Extract full article content
                    url = entry.get("link")
                    if not url:
                        continue

                    content = self._extract_content(entry)

                    article = Article(
                        source=self.source_name,
                        url=url,
                        title=entry.get("title", ""),
                        content=content,
                        published_at=published_date,
                        crawled_at=datetime.now(),
                        metadata={
                            "author": entry.get("author", ""),
                            "tags": [tag.term for tag in entry.get("tags", [])],
                            "summary": entry.get("summary", ""),
                            "feed_url": feed_url,
                        },
                    )
                    articles.append(article)

                    # Check limit
                    if limit and len(articles) >= limit:
                        break

            except Exception as e:
                print(f"Error fetching feed {feed_url}: {e}")
                continue

        return articles

    def _parse_date(self, entry) -> datetime:
        """Parse publication date from feed entry.

        Args:
            entry: Feedparser entry object

        Returns:
            datetime object
        """
        # Try various date fields
        date_fields = ["published_parsed", "updated_parsed"]
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                time_struct = getattr(entry, field)
                return datetime(*time_struct[:6])

        # Default to current time if no date found
        return datetime.now()

    def _extract_content(self, entry) -> str:
        """Extract article content from RSS feed or fallback to web scraping.

        Priority:
        1. content:encoded tag (entry.content) - highest quality from RSS
        2. summary/description tag - fallback RSS fields
        3. Web scraping (newspaper4k) - last resort

        Args:
            entry: Feedparser entry object

        Returns:
            Extracted article text
        """
        # Try content:encoded (usually best quality, clean content)
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].value
            # Strip HTML tags if content contains HTML
            if "<" in content and ">" in content:
                return self._strip_html(content)
            return content

        # Check summary/description for length - if too short, will fallback to web scraping
        rss_content = None
        if hasattr(entry, "summary") and entry.summary:
            rss_content = entry.summary
        elif hasattr(entry, "description") and entry.description:
            rss_content = entry.description

        # If RSS content is long enough (300+ chars), use it directly
        MIN_CONTENT_LENGTH = 300
        if rss_content and len(self._strip_html(rss_content)) >= MIN_CONTENT_LENGTH:
            # Strip HTML tags if content contains HTML
            if "<" in rss_content and ">" in rss_content:
                return self._strip_html(rss_content)
            return rss_content

        # RSS content is too short or missing - will try web scraping below

        # Try web scraping for short or missing RSS content
        url = entry.get("link")
        if url:
            try:
                # Identify source from URL
                if "mk.co.kr" in url:
                    source = "maeil"
                elif "bbc.co" in url:
                    source = "bbc"
                else:
                    source = "default"

                # Site-specific configuration for better extraction
                site_configs = {
                    "maeil": {
                        "language": "ko",
                        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "request_timeout": 30,
                        "memoize_articles": False,
                    },
                    "bbc": {
                        "language": "en",
                        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "request_timeout": 20,
                    },
                    "default": {
                        "language": "en",
                        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "request_timeout": 15,
                    },
                }

                config = site_configs.get(source, site_configs["default"])

                # Configure and download article
                article = NewspaperArticle(url)
                article.config.language = config["language"]
                article.config.browser_user_agent = config["browser_user_agent"]
                article.config.request_timeout = config["request_timeout"]

                # Apply optional settings
                if "memoize_articles" in config:
                    article.config.memoize_articles = config["memoize_articles"]

                article.download()
                article.parse()

                # Validate extracted content
                if not article.text or len(article.text.strip()) < 100:
                    raise ValueError(
                        f"Extracted content too short: {len(article.text) if article.text else 0} chars"
                    )

                # Remove RSS summary if duplicated in extracted text
                extracted_text = article.text
                if rss_content and rss_content in extracted_text:
                    extracted_text = extracted_text.replace(rss_content, "").strip()

                return extracted_text

            except Exception as e:
                error_msg = f"newspaper4k extraction failed for {url}: {str(e)}"
                print(error_msg)

                # Specific error handling
                if "404" in str(e):
                    print("  → Article not found (404)")
                elif "timeout" in str(e).lower() or "timed out" in str(e).lower():
                    print("  → Request timeout")
                elif "too short" in str(e).lower():
                    print("  → Content validation failed")
                else:
                    print(f"  → Error type: {type(e).__name__}")

        # Final fallback: return RSS content even if short (better than nothing)
        if rss_content:
            if "<" in rss_content and ">" in rss_content:
                return self._strip_html(rss_content)
            return rss_content

        return ""

    def _strip_html(self, html: str) -> str:
        """Strip HTML tags and return plain text.

        Args:
            html: HTML content string

        Returns:
            Plain text with HTML tags removed
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator=" ", strip=True)
        except Exception as e:
            print(f"Error stripping HTML: {e}")
            return html
