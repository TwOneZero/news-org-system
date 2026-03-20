import pytest
from unittest.mock import MagicMock
from datetime import datetime

from news_org_system.services.stats import StatisticsService
from news_org_system.storage.mongo_store import MongoStore

@pytest.fixture
def mock_store():
    store = MagicMock(spec=MongoStore)
    store.articles_collection = MagicMock()
    return store

@pytest.fixture
def mock_registry():
    feed_config_mock = MagicMock()
    feed_config_mock.feed_url = "http://test.com/rss"
    feed_config_mock.adapter_name = "test_adapter"
    return {"test_source": feed_config_mock}

def test_stats_service_init(mock_store, mock_registry):
    service = StatisticsService(store=mock_store, registry=mock_registry)
    assert service.store == mock_store
    assert service.registry == mock_registry

def test_get_overall_stats(mock_store, mock_registry):
    service = StatisticsService(store=mock_store, registry=mock_registry)
    
    mock_store.get_stats.return_value = {
        "total": 100,
        "by_source": {"test_source": 100}
    }
    
    # Mock oldest, newest, last_collected
    mock_store.articles_collection.find_one.side_effect = [
        {"published_at": datetime(2023, 1, 1)},  # oldest
        {"published_at": datetime(2023, 1, 31)}, # newest
        {"crawled_at": datetime(2023, 2, 1)}     # last_collected
    ]
    
    result = service.get_overall_stats()
    
    assert result["total_articles"] == 100
    assert result["total_sources"] == 1
    assert result["by_source"]["test_source"] == 100
    assert result["date_range"]["oldest"] == datetime(2023, 1, 1)
    assert result["date_range"]["newest"] == datetime(2023, 1, 31)
    assert result["last_collection"] == datetime(2023, 2, 1)

def test_get_source_stats_exists(mock_store, mock_registry):
    service = StatisticsService(store=mock_store, registry=mock_registry)
    
    mock_store.articles_collection.count_documents.return_value = 50
    mock_store.articles_collection.find_one.side_effect = [
        {"published_at": datetime(2023, 1, 1)},  # oldest
        {"published_at": datetime(2023, 1, 31)}  # newest
    ]
    
    result = service.get_source_stats("test_source")
    
    assert result["source"] == "test_source"
    assert result["total_articles"] == 50
    assert result["oldest_article"] == datetime(2023, 1, 1)
    assert result["newest_article"] == datetime(2023, 1, 31)
    assert result["feed_url"] == "http://test.com/rss"
    assert result["adapter_name"] == "test_adapter"

def test_get_source_stats_not_found(mock_store, mock_registry):
    service = StatisticsService(store=mock_store, registry=mock_registry)
    result = service.get_source_stats("unknown_source")
    assert result is None

def test_get_all_sources_summary(mock_store, mock_registry):
    service = StatisticsService(store=mock_store, registry=mock_registry)
    
    # Add another source to registry
    mock_registry["source_2"] = MagicMock()
    
    # Mock get_source_stats instead of internal DB calls
    service.get_source_stats = MagicMock(side_effect=[
        {"source": "test_source", "total_articles": 10},
        {"source": "source_2", "total_articles": 20}
    ])
    
    result = service.get_all_sources_summary()
    
    assert len(result) == 2
    assert result[0]["source"] == "source_2" # sorted descending
    assert result[0]["total_articles"] == 20
    assert result[1]["source"] == "test_source"
