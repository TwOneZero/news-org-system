"""MongoDB storage for collected articles and disclosures."""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

from ..readers.base_reader import Article


class MongoStore:
    """MongoDB storage for articles and disclosures.

    Provides methods to store, retrieve, and manage collected data.
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        database_name: str = "news_org",
        collection_name: str = "articles",
    ):
        """Initialize MongoDB connection.

        Args:
            connection_string: MongoDB connection URI (defaults to MONGO_URI env variable)
            database_name: Name of the database
            collection_name: Name of the collection
        """
        self.connection_string = connection_string or os.getenv(
            "MONGO_URI", "mongodb://localhost:27017"
        )
        self.database_name = database_name
        self.collection_name = collection_name

        # Initialize MongoDB client
        self.client = MongoClient(self.connection_string)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

        # Create indexes for efficient querying
        self._create_indexes()

    def _create_indexes(self):
        """Create indexes for efficient queries."""
        try:
            # Unique index on URL to prevent duplicates
            self.collection.create_index("url", unique=True)

            # Index for date-based queries
            self.collection.create_index([("published_at", ASCENDING)])

            # Index for source-based queries
            self.collection.create_index("source")

            # Index for compound queries
            self.collection.create_index(
                [("source", ASCENDING), ("published_at", ASCENDING)]
            )

        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")

    def save_articles(self, articles: List[Article]) -> int:
        """Save articles to MongoDB.

        Args:
            articles: List of Article objects to save

        Returns:
            Number of articles successfully saved
        """
        saved_count = 0

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
                self.collection.insert_one(article_dict)
                saved_count += 1

            except DuplicateKeyError:
                # Article with this URL already exists, skip
                continue
            except Exception as e:
                print(f"Error saving article {article.url}: {e}")
                continue

        return saved_count

    def get_articles(
        self,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[dict]:
        """Retrieve articles from MongoDB.

        Args:
            source: Filter by source (e.g., 'yonhap', 'dart')
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
        cursor = self.collection.find(query).sort("published_at", -1).limit(limit)

        return list(cursor)

    def get_article_by_url(self, url: str) -> Optional[dict]:
        """Get a single article by its URL.

        Args:
            url: Article URL

        Returns:
            Article dictionary or None if not found
        """
        return self.collection.find_one({"url": url})

    def delete_old_articles(self, days: int = 30) -> int:
        """Delete articles older than specified days.

        Args:
            days: Number of days to keep articles

        Returns:
            Number of articles deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        result = self.collection.delete_many({"published_at": {"$lt": cutoff_date}})
        return result.deleted_count

    def get_stats(self) -> dict:
        """Get statistics about stored articles.

        Returns:
            Dictionary with statistics
        """
        pipeline = [{"$group": {"_id": "$source", "count": {"$sum": 1}}}]

        source_counts = {
            doc["_id"]: doc["count"] for doc in self.collection.aggregate(pipeline)
        }

        return {
            "total_articles": self.collection.count_documents({}),
            "by_source": source_counts,
            "latest_article": self.collection.find_one(sort=[("published_at", -1)]),
        }

    def close(self):
        """Close MongoDB connection."""
        self.client.close()
