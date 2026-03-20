"""Service for querying articles from storage."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..storage import MongoStore

logger = logging.getLogger(__name__)


class ArticleQueryService:
    """Service for querying and retrieving articles from storage.

    This service provides methods to query articles with various filters,
    pagination support, and single article retrieval.
    """

    def __init__(self, store: MongoStore):
        """Initialize the query service.

        Args:
            store: MongoStore instance for querying articles
        """
        self.store = store

    def query_articles(
        self,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """Query articles with filters and pagination.

        Args:
            source: Filter by source name
            start_date: Filter articles published after this date
            end_date: Filter articles published before this date
            keyword: Search keyword in title or content
            page: Page number (1-indexed)
            page_size: Number of articles per page (max 100)

        Returns:
            Dictionary with query results:
            {
                "articles": List[dict],
                "total": int,
                "page": int,
                "page_size": int,
                "total_pages": int
            }
        """
        # Enforce maximum page size
        max_page_size = 100
        effective_page_size = min(page_size, max_page_size)
        warning = None
        if page_size > max_page_size:
            warning = f"Page size reduced from {page_size} to maximum {max_page_size}"

        # Build query filters
        query = {}
        if source:
            query["source"] = source
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            if date_filter:
                query["published_at"] = date_filter

        # Apply keyword search (text search in title and content)
        if keyword:
            # Use MongoDB text search or regex as fallback
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"content": {"$regex": keyword, "$options": "i"}},
            ]

        # Calculate skip for pagination
        skip = (page - 1) * effective_page_size

        # Get total count
        total = self.store.articles_collection.count_documents(query)

        # Calculate total pages
        total_pages = (total + effective_page_size - 1) // effective_page_size

        # Execute query with pagination
        cursor = (
            self.store.articles_collection.find(query)
            .sort("published_at", -1)
            .skip(skip)
            .limit(effective_page_size)
        )

        articles = list(cursor)

        # Convert MongoDB _id to string for JSON serialization
        for article in articles:
            if "_id" in article:
                article["id"] = str(article.pop("_id"))

        result = {
            "articles": articles,
            "total": total,
            "page": page,
            "page_size": effective_page_size,
            "total_pages": total_pages,
        }

        if warning:
            result["warning"] = warning

        logger.info(f"Queried {len(articles)} articles (page {page}/{total_pages})")

        return result

    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Get a single article by its MongoDB ID.

        Args:
            article_id: MongoDB ObjectId as string

        Returns:
            Article dictionary or None if not found
        """
        from bson import ObjectId

        try:
            article = self.store.articles_collection.find_one(
                {"_id": ObjectId(article_id)}
            )
            if article and "_id" in article:
                article["id"] = str(article.pop("_id"))
            return article
        except Exception as e:
            logger.error(f"Error retrieving article {article_id}: {e}")
            return None

    def get_article_by_url(self, url: str) -> Optional[Dict]:
        """Get a single article by its URL.

        Args:
            url: Article URL

        Returns:
            Article dictionary or None if not found
        """
        article = self.store.get_article_by_url(url)
        if article and "_id" in article:
            article["id"] = str(article.pop("_id"))
        return article

    def get_recent_articles(
        self,
        source: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Get recent articles.

        Args:
            source: Filter by source name (optional)
            limit: Maximum number of articles to return

        Returns:
            List of article dictionaries
        """
        articles = self.store.get_articles(source=source, limit=limit)

        # Convert MongoDB _id to string
        for article in articles:
            if "_id" in article:
                article["id"] = str(article.pop("_id"))

        return articles
