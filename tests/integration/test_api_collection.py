from unittest.mock import patch

def test_collect_all(test_client):
    with patch("news_org_system.api.routes.collection.get_collection_service") as mock_get_service:
        # Dependency override is already active, but we can also patch the service directly if needed.
        # However, it's cleaner to patch the service returned by the dependency.
        pass
    
    # We will patch NewsCollectionService methods instead
    with patch("news_org_system.services.collection.NewsCollectionService.collect_all") as mock_collect:
        mock_collect.return_value = {
            "timestamp": "2023-01-01T00:00:00",
            "start_date": "2023-01-01T00:00:00",
            "end_date": "2023-01-01T01:00:00",
            "total_fetched": 10,
            "total_saved": 5,
            "sources": {"test": {"source": "test", "fetched": 10, "saved": 5, "skipped": 0, "status": "success"}}
        }
        
        response = test_client.post("/api/v1/collect", json={"days_back": 2, "limit": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_fetched"] == 10
        assert data["total_saved"] == 5
        mock_collect.assert_called_once()

def test_collect_from_source(test_client):
    with patch("news_org_system.services.collection.NewsCollectionService.collect_from_source") as mock_collect:
        mock_collect.return_value = {
            "source": "test_source",
            "fetched": 5,
            "saved": 5,
            "skipped": 0,
            "status": "success",
            "timestamp": "2023-01-01T00:00:00",
            "start_date": "2023-01-01T00:00:00",
            "end_date": "2023-01-01T01:00:00"
        }
        
        response = test_client.post("/api/v1/collect/test_source", json={"days_back": 1, "limit": 5})
        print("RESPONSE URL:", response.url)
        print("RESPONSE CONTENT:", response.content)
        assert response.status_code == 200
        data = response.json()
        assert data["fetched"] == 5
        assert data["status"] == "success"
        mock_collect.assert_called_once_with(source_name="test_source", days_back=1, limit=5)

def test_collect_from_source_not_found(test_client):
    with patch("news_org_system.services.collection.NewsCollectionService.collect_from_source") as mock_collect:
        mock_collect.side_effect = ValueError("Source 'unknown' not found")
        
        response = test_client.post("/api/v1/collect/unknown")
        
        assert response.status_code == 404
        assert "not found" in response.json()["error"].lower()
