from unittest.mock import patch
from datetime import datetime

def test_get_overall_stats(test_client):
    with patch("news_org_system.services.stats.StatisticsService.get_overall_stats") as mock_stats:
        mock_stats.return_value = {
            "total_articles": 100,
            "total_sources": 5,
            "by_source": {"test_source": 100},
            "date_range": {
                "oldest": datetime(2023, 1, 1).isoformat(),
                "newest": datetime(2023, 1, 31).isoformat()
            },
            "last_collection": datetime(2023, 2, 1).isoformat(),
            "generated_at": datetime.now().isoformat()
        }
        
        response = test_client.get("/api/v1/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_articles"] == 100
        assert data["total_sources"] == 5

def test_get_source_stats(test_client):
    with patch("news_org_system.services.stats.StatisticsService.get_source_stats") as mock_stats:
        mock_stats.return_value = {
            "source": "test_source",
            "feed_url": "http://test.com",
            "adapter_name": "test_adapter",
            "total_articles": 50,
            "oldest_article": datetime(2023, 1, 1).isoformat(),
            "newest_article": datetime(2023, 1, 31).isoformat()
        }
        
        response = test_client.get("/api/v1/stats/test_source")
        
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "test_source"
        assert data["total_articles"] == 50

def test_get_source_stats_not_found(test_client):
    with patch("news_org_system.services.stats.StatisticsService.get_source_stats") as mock_stats:
        mock_stats.return_value = None
        
        response = test_client.get("/api/v1/stats/unknown")
        
        assert response.status_code == 404
        assert "not found" in response.json()["error"].lower()
