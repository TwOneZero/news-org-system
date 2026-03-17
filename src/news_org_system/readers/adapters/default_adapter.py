"""Default RSS adapter for standard RSS/Atom feeds."""

from datetime import datetime
from newspaper import Article as NewspaperArticle
from bs4 import BeautifulSoup

from .base import BaseRSSAdapter


class DefaultRSSAdapter(BaseRSSAdapter):
    """Default RSS/Atom feed parser.

    Handles standard RSS/Atom feeds with generic content extraction.
    Most news sites follow standard RSS format, so this adapter
    works for the majority of cases.
    """

    def extract_content(self, entry) -> str:
        """Extract article content using multi-stage fallback strategy.

        Priority:
        1. content:encoded tag - highest quality from RSS
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

        # If RSS content is long enough, use it directly
        if rss_content and len(self._strip_html(rss_content)) >= self.config.min_content_length:
            # Strip HTML tags if content contains HTML
            if "<" in rss_content and ">" in rss_content:
                return self._strip_html(rss_content)
            return rss_content

        # RSS content is too short or missing - try web scraping
        url = entry.get("link")
        if url:
            try:
                # Configure and download article
                article = NewspaperArticle(url)
                article.config.language = self.config.language
                article.config.browser_user_agent = self.config.browser_user_agent
                article.config.request_timeout = self.config.request_timeout
                article.config.memoize_articles = self.config.memoize_articles

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

    def parse_date(self, entry) -> datetime:
        """Parse publication date from feed entry.

        Tries various date fields in order of preference:
        1. published_parsed
        2. updated_parsed
        3. Current time as fallback

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
