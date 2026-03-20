import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from news_org_system.services.collection import NewsCollectionService
from news_org_system.readers.base_reader import Article
from news_org_system.storage.mongo_store import MongoStore

@pytest.fixture
def mock_store():
    store = MagicMock(spec=MongoStore)
    store.save_articles.return_value = {"saved": 2, "skipped": 0, "errors": []}
    return store

@pytest.fixture
def mock_registry():
    return {"test_source": MagicMock(), "error_source": MagicMock()}

def test_collection_service_init(mock_store, mock_registry):
    service = NewsCollectionService(store=mock_store, registry=mock_registry)
    assert service.store == mock_store
    assert service.registry == mock_registry

@patch("news_org_system.services.collection.RSSReader")
def test_collect_all_success(mock_rss_reader, mock_store, mock_registry):
    # Setup mock reader
    mock_reader_instance = MagicMock()
    mock_article = Article(title="Test", url="http://test.com", content="Test", source="test_source", published_at=datetime.now(), crawled_at=datetime.now())
    mock_reader_instance.fetch.return_value = [mock_article, mock_article]
    mock_rss_reader.from_source.return_value = mock_reader_instance

    service = NewsCollectionService(store=mock_store, registry={"test_source": MagicMock()})
    
    result = service.collect_all(limit=10)
    
    assert "total_fetched" in result
    assert result["total_fetched"] == 2
    assert result["total_saved"] == 2
    assert "test_source" in result["sources"]
    assert result["sources"]["test_source"]["status"] == "success"
    
    mock_reader_instance.fetch.assert_called_once()
    mock_store.save_articles.assert_called_once()

@patch("news_org_system.services.collection.RSSReader")
def test_collect_all_with_error(mock_rss_reader, mock_store):
    mock_reader_success = MagicMock()
    mock_reader_success.fetch.return_value = [MagicMock()]
    
    mock_reader_error = MagicMock()
    mock_reader_error.fetch.side_effect = Exception("Fetch error")
    
    def mock_from_source(source_name):
        if source_name == "success_source":
            return mock_reader_success
        return mock_reader_error
        
    mock_rss_reader.from_source.side_effect = mock_from_source

    service = NewsCollectionService(store=mock_store, registry={"success_source": MagicMock(), "error_source": MagicMock()})
    
    result = service.collect_all()
    
    assert result["sources"]["success_source"]["status"] == "success"
    assert result["sources"]["error_source"]["status"] == "error"
    assert "Fetch error" in result["sources"]["error_source"]["error"]

@patch("news_org_system.services.collection.RSSReader")
def test_collect_from_source_success(mock_rss_reader, mock_store):
    mock_reader_instance = MagicMock()
    mock_reader_instance.fetch.return_value = [MagicMock(), MagicMock()]
    mock_rss_reader.from_source.return_value = mock_reader_instance
    
    service = NewsCollectionService(store=mock_store, registry={"test_source": MagicMock()})
    result = service.collect_from_source("test_source", limit=5)
    
    assert result["fetched"] == 2
    assert result["saved"] == 2
    assert result["status"] == "success"
    mock_store.save_articles.assert_called_once()

def test_collect_from_source_not_found(mock_store):
    service = NewsCollectionService(store=mock_store, registry={})
    
    with pytest.raises(ValueError, match="Source 'unknown' not found"):
        service.collect_from_source("unknown")
