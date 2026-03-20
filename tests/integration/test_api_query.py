from unittest.mock import patch

def test_get_articles(test_client):
    with patch("news_org_system.services.query.ArticleQueryService.query_articles") as mock_query:
        mock_query.return_value = {
            "articles": [{
                "id": "1",
                "title": "Test 1",
                "url": "http://test.com",
                "content": "Test content",
                "source": "test_source",
                "published_at": "2023-01-01T00:00:00",
                "crawled_at": "2023-01-01T01:00:00"
            }],
            "total": 1,
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        
        response = test_client.get("/api/v1/articles?page=1&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["articles"]) == 1
        assert data["total"] == 1
        assert data["page"] == 1

def test_get_article_by_id(test_client):
    with patch("news_org_system.services.query.ArticleQueryService.get_article_by_id") as mock_get:
        mock_get.return_value = {
            "id": "1",
            "title": "Test 1",
            "url": "http://test.com",
            "content": "Test content",
            "source": "test_source",
            "published_at": "2023-01-01T00:00:00",
            "crawled_at": "2023-01-01T01:00:00"
        }
        
        response = test_client.get("/api/v1/articles/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "1"
        assert data["title"] == "Test 1"

def test_get_article_not_found(test_client):
    with patch("news_org_system.services.query.ArticleQueryService.get_article_by_id") as mock_get:
        mock_get.return_value = None
        
        response = test_client.get("/api/v1/articles/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["error"].lower()

def test_validation_error(test_client):
    # page_size too large or invalid type
    response = test_client.get("/api/v1/articles?page_size=abc")
    assert response.status_code == 422
