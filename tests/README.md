# Test Suite Guide

This directory contains the formal pytest test suite for news-org-system.

## Test Structure

```text
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── integration/             # Integration tests (real RSS feeds, network access)
│   ├── __init__.py
│   └── test_rss_feeds.py    # RSS feed extraction tests
└── unit/                    # Unit tests (fast, no network)
    ├── __init__.py
    └── test_readers.py      # Reader unit tests (future)
```

## Test Categories

### Integration Tests (`tests/integration/`)

- **Purpose**: Test real-world functionality with external dependencies
- **Characteristics**: Slower, requires network access, tests real RSS feeds
- **Examples**: RSS feed extraction, content quality validation
- **Marker**: `@pytest.mark.integration`

### Unit Tests (`tests/unit/`)

- **Purpose**: Test individual components in isolation
- **Characteristics**: Fast, no network, use mocks
- **Examples**: Data model validation, helper functions
- **Marker**: `@pytest.mark.unit`

## Running Tests

### Installation

First, install the development dependencies:

```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Using pip
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/integration/test_rss_feeds.py

# Run specific test function
pytest tests/integration/test_rss_feeds.py::test_maeil_fetch_success

# Run with detailed output (print statements)
pytest -v -s
```

### Running by Category

```bash
# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Run only slow tests
pytest -m slow

# Exclude integration tests
pytest -m "not integration"
```

### Coverage Reporting

```bash
# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View report in browser
```

### Advanced Usage

```bash
# Run tests in parallel (faster)
# Note: requires pytest-xdist
pytest -n auto

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run tests with matching pattern
pytest -k "maeil"

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb
```

## Test Fixtures

### Available Fixtures

Located in [`conftest.py`](conftest.py):

- **`rss_reader_maeil`**: RSSReader configured for Maeil Business News
- **`rss_reader_bbc`**: RSSReader configured for BBC
- **`rss_reader_yonhap`**: RSSReader configured for Yonhap News
- **`validate_article_quality`**: Quality validation helper function
- **`sample_article_limit`**: Default article fetch limit (3)
- **`quality_thresholds`**: Quality threshold values

### Using Fixtures

Fixtures are automatically injected into test functions:

```python
def test_example(rss_reader_maeil, validate_article_quality):
    articles = rss_reader_maeil.fetch(limit=3)
    result = validate_article_quality(articles[0])
    assert result["is_valid"]
```

## Test Markers

Tests are marked to categorize and enable selective execution:

- **`@pytest.mark.integration`**: Integration tests with real external services
- **`@pytest.mark.unit`**: Fast unit tests without external dependencies
- **`@pytest.mark.slow`**: Tests that take longer to execute

### Listing Available Markers

```bash
pytest --markers
```

## Writing New Tests

### Integration Test Template

```python
import pytest
from src.readers.base_reader import Article

@pytest.mark.integration
def test_new_source_fetch_success(rss_reader_new_source):
    """Test that new source can be fetched successfully."""
    articles = rss_reader_new_source.fetch(limit=3)

    assert len(articles) > 0, "Should fetch at least one article"
    assert all(isinstance(a, Article) for a in articles)
```

### Unit Test Template

```python
import pytest
from src.readers.base_reader import Article

@pytest.mark.unit
def test_article_model_validation():
    """Test Article model validation."""
    article = Article(
        source="test",
        url="https://example.com",
        title="Test Article",
        content="Test content",
        published_at=datetime.now(),
        crawled_at=datetime.now()
    )

    assert article.title == "Test Article"
    assert article.source == "test"
```

## Test Configuration

Pytest configuration is defined in [`pyproject.toml`](../pyproject.toml):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "integration: marks tests as integration tests (real RSS feeds, network access)",
    "unit: marks tests as unit tests (fast, no network)",
    "slow: marks tests as slow (network calls, large datasets)"
]
addopts = "-v --strict-markers --tb=short --cov=src --cov-report=term-missing"
```

## Continuous Integration

These tests are designed to work well with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest -m unit  # Fast unit tests for every commit

- name: Run integration tests
  run: |
    pytest -m integration  # Slower integration tests
```

## Troubleshooting

### Import Errors

If you see import errors like `ModuleNotFoundError: No module named 'src'`:

```bash
# Install the package in development mode
uv pip install -e .
```

### Network Tests Failing

If integration tests fail due to network issues:

```bash
# Run only unit tests
pytest -m unit

# Or skip network tests
pytest -m "not integration"
```

### Missing Fixtures

If you see `fixture 'xyz' not found` errors:

- Ensure [`conftest.py`](conftest.py) exists in the `tests/` directory
- Check that fixture names are spelled correctly
- Verify pytest is discovering tests from the correct directory

## Legacy Test Scripts

The `test_script/` directory contains legacy debugging scripts:

- [`test_script/test_rss_extraction.py`](../test_script/test_rss_extraction.py): Manual RSS feed testing
- `test_script/debug_rss_feed.py`: Feed debugging utilities
- `test_script/check_content_quality.py`: Database quality checks

**Note**: These scripts are deprecated and kept for debugging purposes only. Use the pytest test suite for formal testing.

## Best Practices

1. **Use descriptive test names**: `test_maeil_fetch_success` is better than `test_1`
2. **Add docstrings**: Explain what the test validates and why
3. **Use fixtures**: Share setup code through fixtures in `conftest.py`
4. **Mark tests appropriately**: Use `@pytest.mark.integration` or `@pytest.mark.unit`
5. **Keep tests independent**: Each test should be able to run in isolation
6. **Use assertions**: Prefer `assert` statements over print statements
7. **Test edge cases**: Don't just test the happy path

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures Guide](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Parametrize Guide](https://docs.pytest.org/en/stable/parametrize.html)
