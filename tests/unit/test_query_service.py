import pytest
from unittest.mock import MagicMock
from datetime import datetime
from bson import ObjectId

from news_org_system.services.query import ArticleQueryService
from news_org_system.storage.mongo_store import MongoStore

@pytest.fixture
def mock_store():
    store = MagicMock(spec=MongoStore)
    store.articles_collection = MagicMock()
    return store

def test_query_service_init(mock_store):
    service = ArticleQueryService(store=mock_store)
    assert service.store == mock_store

def test_query_articles_basic(mock_store):
    service = ArticleQueryService(store=mock_store)
    
    # Mock total count
    mock_store.articles_collection.count_documents.return_value = 5
    
    # Mock cursor
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    
    # Return 2 articles
    article1_id = ObjectId()
    article2_id = ObjectId()
    mock_cursor.__iter__.return_value = [
        {"_id": article1_id, "title": "Article 1"},
        {"_id": article2_id, "title": "Article 2"}
    ]
    
    mock_store.articles_collection.find.return_value = mock_cursor
    
    result = service.query_articles(page=1, page_size=2)
    
    assert result["total"] == 5
    assert result["page"] == 1
    assert result["page_size"] == 2
    assert result["total_pages"] == 3
    assert len(result["articles"]) == 2
    assert "id" in result["articles"][0]
    assert "_id" not in result["articles"][0]
    
    mock_store.articles_collection.find.assert_called_once_with({})
    mock_cursor.limit.assert_called_once_with(2)

def test_query_articles_with_filters(mock_store):
    service = ArticleQueryService(store=mock_store)
    
    mock_store.articles_collection.count_documents.return_value = 0
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.__iter__.return_value = []
    mock_store.articles_collection.find.return_value = mock_cursor
    
    start_dt = datetime(2023, 1, 1)
    end_dt = datetime(2023, 1, 31)
    
    service.query_articles(
        source="test_source",
        start_date=start_dt,
        end_date=end_dt,
        keyword="tech",
        page=2,
        page_size=10
    )
    
    # Check that find was called with correct filter
    call_args = mock_store.articles_collection.find.call_args[0][0]
    assert call_args["source"] == "test_source"
    assert call_args["published_at"]["$gte"] == start_dt
    assert call_args["published_at"]["$lte"] == end_dt
    assert "$or" in call_args
    assert len(call_args["$or"]) == 2
    
    # Check skip and limit
    mock_cursor.skip.assert_called_once_with(10)
    mock_cursor.limit.assert_called_once_with(10)

def test_get_article_by_id(mock_store):
    service = ArticleQueryService(store=mock_store)
    
    obj_id = ObjectId()
    mock_store.articles_collection.find_one.return_value = {"_id": obj_id, "title": "Test"}
    
    result = service.get_article_by_id(str(obj_id))
    
    assert result["title"] == "Test"
    assert result["id"] == str(obj_id)
    assert "_id" not in result
