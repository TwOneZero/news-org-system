"""News and Disclosure Data Collection Pipeline.

This module provides a comprehensive pipeline for collecting Korean and global news
along with Korean corporate disclosures from DART.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from .storage import MongoStore
from .readers import RSSReader, DARTReader


# Load environment variables
load_dotenv()


class NewsCollectionPipeline:
    """Main pipeline for collecting news and disclosure data."""

    def __init__(
        self,
        mongo_uri: str = None,
        database_name: str = "news_org",
    ):
        """Initialize the pipeline.

        Args:
            mongo_uri: MongoDB connection URI (defaults to MONGO_URI env variable)
            database_name: Name of the MongoDB database
        """
        # Initialize MongoDB storage
        self.mongo_uri = mongo_uri or os.getenv(
            "MONGO_URI", "mongodb://localhost:27017"
        )
        self.storage = MongoStore(
            connection_string=self.mongo_uri,
            database_name=database_name,
        )

        # Initialize readers using registry system
        # RSSReader.from_source() creates readers from registered feed configurations
        self.readers = {
            "yonhap_economy": RSSReader.from_source("yonhap_economy"),
            "maeil_management": RSSReader.from_source("maeil_management"),
            "etnews_today": RSSReader.from_source("etnews_today"),
        }

        # Add DART reader if API key is available
        dart_api_key = os.getenv("DART_API_KEY")
        if dart_api_key:
            try:
                self.readers["dart"] = DARTReader(source_name="dart")
            except Exception as e:
                print(f"Warning: Could not initialize DART reader: {e}")

    def collect_all(self, days_back: int = 1, limit: int = 10) -> dict:
        """Collect articles from all configured sources.

        Args:
            days_back: Number of days to look back for articles
            limit: Maximum articles per source

        Returns:
            Dictionary with collection statistics
        """
        start_date = datetime.now() - timedelta(days=days_back)
        end_date = datetime.now()

        results = {
            "timestamp": datetime.now().isoformat(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "sources": {},
        }

        total_saved = 0

        for source_name, reader in self.readers.items():
            print(f"\n{'=' * 60}")
            print(f"Collecting from: {source_name}")
            print(f"{'=' * 60}")

            try:
                # Fetch articles
                articles = reader.fetch(
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                )

                print(f"Fetched {len(articles)} articles")

                # Save to MongoDB
                saved = self.storage.save_articles(articles)
                total_saved += saved

                results["sources"][source_name] = {
                    "fetched": len(articles),
                    "saved": saved,
                }

                print(f"Saved {saved} new articles to database")

            except Exception as e:
                print(f"Error collecting from {source_name}: {e}")
                results["sources"][source_name] = {
                    "error": str(e),
                }

        results["total_saved"] = total_saved
        return results

    def get_stats(self) -> dict:
        """Get statistics about stored articles.

        Returns:
            Dictionary with statistics
        """
        return self.storage.get_stats()

    def get_recent_articles(self, source: str = None, limit: int = 10) -> list:
        """Get recent articles from storage.

        Args:
            source: Filter by source name (optional)
            limit: Maximum number of articles to return

        Returns:
            List of article dictionaries
        """
        return self.storage.get_articles(source=source, limit=limit)


def run_scheduled_job():
    """Run the collection pipeline as a scheduled job."""
    print(f"\n{'#' * 60}")
    print(f"Starting scheduled collection: {datetime.now().isoformat()}")
    print(f"{'#' * 60}\n")

    pipeline = NewsCollectionPipeline()
    results = pipeline.collect_all(days_back=1, limit=50)

    print(f"\n{'#' * 60}")
    print("Collection Summary")
    print(f"{'#' * 60}")
    print(f"Total new articles saved: {results['total_saved']}")
    for source, stats in results["sources"].items():
        if "error" in stats:
            print(f"  {source}: ERROR - {stats['error']}")
        else:
            print(f"  {source}: {stats['saved']}/{stats['fetched']} saved")


def main():
    """Main entry point."""
    import sys

    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "collect":
            # Run collection once
            pipeline = NewsCollectionPipeline()
            results = pipeline.collect_all(days_back=1, limit=10)

            print(f"\n{'=' * 60}")
            print("Collection Complete")
            print(f"{'=' * 60}")
            print(f"Total new articles saved: {results['total_saved']}")

            for source, stats in results["sources"].items():
                if "error" in stats:
                    print(f"  {source}: ERROR - {stats['error']}")
                else:
                    print(f"  {source}: {stats['saved']}/{stats['fetched']} saved")

        elif command == "stats":
            # Show statistics
            pipeline = NewsCollectionPipeline()
            stats = pipeline.get_stats()

            print(f"\n{'=' * 60}")
            print("Database Statistics")
            print(f"{'=' * 60}")
            print(f"Total articles: {stats['total_articles']}")
            print("\nBy source:")
            for source, count in stats["by_source"].items():
                print(f"  {source}: {count}")

            if stats["latest_article"]:
                print("\nLatest article:")
                print(f"  Source: {stats['latest_article']['source']}")
                print(f"  Title: {stats['latest_article']['title']}")
                print(f"  Date: {stats['latest_article']['published_at']}")

        elif command == "schedule":
            # Run as scheduled job
            run_scheduled_job()

        elif command == "daemon":
            # Run as daemon with scheduler
            scheduler = BlockingScheduler()

            # Schedule job to run daily at 9 AM and 6 PM
            scheduler.add_job(
                run_scheduled_job,
                CronTrigger(hour="9,18", minute="0"),
                id="daily_collection",
                name="Daily news and disclosure collection",
                replace_existing=True,
            )

            print(f"\n{'=' * 60}")
            print("Starting News Collection Daemon")
            print(f"{'=' * 60}")
            print("Scheduled jobs:")
            for job in scheduler.get_jobs():
                print(f"  - {job.name} (ID: {job.id})")
                print(f"    Next run: {job.next_run_time}")
            print("\nPress Ctrl+C to stop...")

            try:
                scheduler.start()
            except (KeyboardInterrupt, SystemExit):
                print("\nShutting down scheduler...")
                scheduler.shutdown()

        else:
            print(f"Unknown command: {command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """Print usage instructions."""
    print("""
News and Disclosure Collection Pipeline

Usage:
  python news_api.py <command>

Commands:
  collect   - Run collection once and exit
  stats     - Show database statistics
  schedule  - Run scheduled job once
  daemon    - Run as daemon with continuous scheduling

Environment Variables:
  MONGO_URI        - MongoDB connection URI (default: mongodb://localhost:27017)
  DART_API_KEY     - DART API key (get free at https://opendart.fss.or.kr/)

Examples:
  # Collect articles once
  python news_api.py collect

  # Show statistics
  python news_api.py stats

  # Run as daemon (schedules: 9 AM and 6 PM daily)
  python news_api.py daemon

Setup:
  1. Copy .env.example to .env
  2. Set DART_API_KEY in .env
  3. Ensure MongoDB is running
  4. Run: python news_api.py collect
""")


if __name__ == "__main__":
    main()
