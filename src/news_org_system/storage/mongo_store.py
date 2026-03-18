"""MongoDB storage for collected articles"""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError

from ..readers.base_reader import Article


class MongoStore:
    """MongoDB storage for articles

    Provides methods to store, retrieve, and manage collected data.
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        database_name: str = "news_org",
        articles_collection: str = "articles",
    ):
        """Initialize MongoDB connection.

        Args:
            connection_string: MongoDB connection URI (defaults to MONGO_URI env variable)
            database_name: Name of the database
            articles_collection: Name of the collection for news articles
        """
        self.connection_string = connection_string or os.getenv(
            "MONGO_URI", "mongodb://localhost:27017"
        )
        self.database_name = database_name
        self.articles_collection_name = articles_collection

        # Initialize MongoDB client
        self.client = MongoClient(self.connection_string)
        self.db = self.client[database_name]

        # Create collection reference
        self.articles_collection = self.db[articles_collection]

        # Create indexes for efficient querying
        self._create_indexes()

    def _create_indexes(self):
        """Create indexes for both collections."""
        try:
            # Articles collection indexes
            self.articles_collection.create_index("url", unique=True)
            self.articles_collection.create_index([("published_at", ASCENDING)])
            self.articles_collection.create_index("source")
            self.articles_collection.create_index(
                [("source", ASCENDING), ("published_at", ASCENDING)]
            )
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")

    def save_articles(self, articles: List[Article]) -> dict:
        """Save articles to MongoDB.

        Args:
            articles: List of Article objects to save

        Returns:
            Dictionary with save statistics:
            {
                "saved": int,
                "skipped": int
            }
        """
        results = {
            "saved": 0,
            "skipped": 0,
        }

        for article in articles:
            try:
                # Convert Article to dict
                article_dict = article.to_dict()

                # Handle datetime serialization
                if isinstance(article_dict["published_at"], datetime):
                    article_dict["published_at"] = article_dict["published_at"]
                if isinstance(article_dict["crawled_at"], datetime):
                    article_dict["crawled_at"] = article_dict["crawled_at"]

                # Insert to database
                self.articles_collection.insert_one(article_dict)
                results["saved"] += 1

            except DuplicateKeyError:
                # Article with this URL already exists, skip
                results["skipped"] += 1
                continue
            except Exception as e:
                print(f"Error saving article {article.url}: {e}")
                continue

        return results

    def get_articles(
        self,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[dict]:
        """Retrieve articles from database.

        Args:
            source: Filter by source (e.g., 'yonhap')
            start_date: Filter articles published after this date
            end_date: Filter articles published before this date
            limit: Maximum number of articles to return

        Returns:
            List of article dictionaries
        """
        query = {}

        # Build query filters
        if source:
            query["source"] = source
        if start_date:
            query["published_at"] = {"$gte": start_date}
        if end_date:
            query["published_at"] = {"$lte": end_date}

        # Execute query
        cursor = (
            self.articles_collection.find(query).sort("published_at", -1).limit(limit)
        )

        return list(cursor)

    def get_article_by_url(self, url: str) -> Optional[dict]:
        """Get a single article by its URL.

        Args:
            url: Article URL

        Returns:
            Article dictionary or None if not found
        """
        return self.articles_collection.find_one({"url": url})

    def delete_old_articles(self, days: int = 30) -> int:
        """Delete articles older than specified days.

        Args:
            days: Number of days to keep articles

        Returns:
            Number of articles deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        result = self.articles_collection.delete_many(
            {"published_at": {"$lt": cutoff_date}}
        )
        return result.deleted_count

    def get_stats(self) -> dict:
        """Get statistics about articles.

        Returns:
            Dictionary with statistics:
            {
                "total": int,
                "by_source": dict,
                "latest": dict
            }
        """
        # Count articles by source
        pipeline = [{"$group": {"_id": "$source", "count": {"$sum": 1}}}]
        source_counts = {
            doc["_id"]: doc["count"]
            for doc in self.articles_collection.aggregate(pipeline)
        }

        return {
            "total": self.articles_collection.count_documents({}),
            "by_source": source_counts,
            "latest": self.articles_collection.find_one(sort=[("published_at", -1)]),
        }

        """Close MongoDB connection."""
        self.client.close()
