# news-org-system

한국 및 글로벌 뉴스 수집 파이프라인 시스템 - RSS 피드 기반 뉴스 수집, REST API, 그리고 AI 기능을 통한 뉴스 정보 가공 시스템입니다.

## System Overview

RSS/Atom 피드에서 뉴스를 수집하고, FastAPI REST API를 통해 제공하며, LangChain/LangGraph를 통해 AI 기반 뉴스 분석 기능을 제공하는 시스템입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                     Clients                                 │
│  CLI Commands | REST API | Future: AI Agent Interface       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
│  - CollectionService: News collection orchestration         │
│  - QueryService: Article retrieval & filtering              │
│  - StatisticsService: Data aggregation                      │
│  - Future: AIService: LangChain/LangGraph integration       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │   Readers       │  │        Storage (MongoDB)          │  │
│  │  - RSSReader    │  │  - URL-based deduplication       │  │
│  │  - Adapters     │  │  - Indexing & querying           │  │
│  │  - Registry     │  │  - Statistics aggregation        │  │
│  └─────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Principles

### 1. Layered Architecture
명확한 관심사 분리를 통해 각 계층이 독립적으로 evolve 할 수 있습니다.

- **API Layer**: HTTP 처리, 요청/응답 검증 (@ai_docs/architecture/layers.md)
- **Service Layer**: 비즈니스 로직 오케스트레이션
- **Data Layer**: RSS 파싱 및 MongoDB 저장

### 2. Adapter Pattern
사이트별 파싱 로직을 독립적인 어댑터로 분리하여 새로운 뉴스 소스 추가를 쉽게 만듭니다.

- `BaseRSSAdapter`: 추상 인터페이스
- `DefaultRSSAdapter`: 표준 RSS/Atom 처리
- 사이트별 어댑터: Yonhap, Maeli, ETnews
- @ai_docs/architecture/adapter-pattern.md

### 3. Registry Pattern
피드 URL과 어댑터를 중앙에서 관리하여 설정을 쉽게 확장할 수 있습니다.

- `FEED_REGISTRY`: 소스명 → 피드 설정 매핑
- `ADAPTER_REGISTRY`: 어댑터명 → 어댑터 클래스 매핑
- @src/news_org_system/readers/registry.py

### 4. Dependency Injection
FastAPI의 의존성 주입 시스템을 통해 테스트 가능하고 유연한 코드를 만듭니다.

- 서비스 팩토리 함수
- 싱글톤 MongoStore
- 테스트 시 모의 객체 주입

### 5. Type Safety
Pydantic 모델을 통해 데이터 검증과 타입 안전성을 보장합니다.

- 도메인 모델 (내부)
- API DTO 모델 (외부)
- 자동 검증 및 직렬화

## Architectural Evolution

### Initial State (CLI-only)
```
CLI Commands → Readers + Storage
```

### Current State (FastAPI Integration, commit b071203)
```
CLI Commands ┐
             ├─→ Service Layer → Readers + Storage
API Routes  ┘
```

**Key Changes**:
- 서비스 레이어 추출: 비즈니스 로직을 CLI와 API가 공유
- FastAPI 도입: 타입 안전한 REST API, 자동 OpenAPI 문서
- DTO 분리: API 모델과 도메인 모델의 독립적 evolve
- 의존성 주입: 테스트 가능한 아키텍처

**Design Decisions**: @ai_docs/architecture/design-decisions.md

## Future Plans: LangChain/LangGraph Integration

### Current State
- LangChain 의존성 설치됨 (langchain, langchain-openai, transformers)
- AI 구현은 없지만 서비스 레이어는 확장 준비됨

### Planned Capabilities
1. **Article Summarization** (LangChain chains)
2. **Sentiment Analysis** (transformers)
3. **Entity Extraction** (spaCy NER)
4. **Topic Classification** (zero-shot classification)
5. **Cross-Article Synthesis** (LangGraph workflows)

### Integration Architecture
```
Service Layer
  └─ AIService (new)
      ├─ SummarizationService
      ├─ SentimentService
      ├─ EntityExtractionService
      └─ LangGraph workflows
```

**Implementation Plan**: @ai_docs/ai/langchain-integration-plan.md

## Key Design Patterns

| Pattern | Purpose | Location |
|---------|---------|----------|
| **Service Layer** | 비즈니스 로직 분리 | @src/news_org_system/services/ |
| **Adapter** | 사이트별 파싱 | @src/news_org_system/readers/adapters/ |
| **Registry** | 중앙 설정 관리 | @src/news_org_system/readers/registry.py |
| **Repository** | 데이터 접근 추상화 | @src/news_org_system/storage/mongo_store.py |
| **Factory** | 서비스/앱 인스턴스 생성 | @src/news_org_system/api/main.py |

## Project Structure

```
src/news_org_system/
├── api/              # FastAPI REST API
│   ├── main.py       # 애플리케이션 팩토리
│   ├── dependencies.py  # 의존성 주입
│   ├── models/       # API DTO (Pydantic)
│   └── routes/       # API 엔드포인트
├── services/         # 비즈니스 로직 서비스 레이어
│   ├── collection.py # 뉴스 수집 오케스트레이션
│   ├── query.py      # 기사 조회 및 필터링
│   └── stats.py      # 통계 집계
├── readers/          # RSS 피드 파싱
│   ├── adapters/     # 사이트별 어댑터
│   ├── rss_reader.py
│   └── registry.py   # 피드/어댑터 레지스트리
└── storage/          # MongoDB 저장소
    └── mongo_store.py
```

**Detailed Layer Architecture**: @ai_docs/architecture/layers.md

## Extension Points

### Adding New RSS Sources
새로운 뉴스 소스를 추가하는 방법:

1. 표준 RSS 피드: `default` 어댑터 사용
2. 커스텀 파싱 필요: 새 어댑터 생성

```python
# @src/news_org_system/readers/registry.py
FEED_REGISTRY["my_source"] = RSSFeedConfig(
    source_name="my_source",
    feed_url="https://example.com/rss.xml",
    adapter_name="default",  # or custom adapter
    language="ko",
)
```

**Complete Guide**: @ai_docs/development/adding-sources.md

### Extending Service Layer
새로운 서비스를 추가하는 방법:

1. 서비스 클래스 생성 (MongoStore 주입)
2. 의존성 주입 함수 추가
3. API 라우트 생성

**Complete Guide**: @ai_docs/development/service-extension.md

### Adding API Endpoints
새로운 API 엔드포인트 추가:

1. Pydantic 모델 생성 (api/models/)
2. 라우트 핸들러 생성 (api/routes/)
3. 메인 앱에 라우터 등록

**API Reference**: @ai_docs/api/endpoint-reference.md

## Technology Stack

### Core
- **Python**: 3.12+
- **FastAPI**: REST API 프레임워크
- **Pydantic**: 데이터 검증
- **MongoDB**: 문서 저장소

### RSS Processing
- **feedparser**: RSS/Atom 피드 파싱
- **newspaper4k**: 웹 스크래핑 (fallback)
- **BeautifulSoup4**: HTML 처리

### AI/ML (Future)
- **LangChain**: LLM 프레임워크
- **LangGraph**: 워크플로우 오케스트레이션
- **transformers**: 로컬 NLP 모델
- **spaCy**: 개체명 인식 (NER)

**Full Dependencies**: @pyproject.toml

## API Usage

### Starting the API Server

```bash
# Using installed command
news-org-api

# Or with uvicorn
uvicorn news_org_system.api.main:app --reload
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**Quick Start**: @README.api.md
**Full Reference**: @ai_docs/api/endpoint-reference.md

## CLI Usage

### Collection Commands

```bash
# Collect from all sources
news-org collect --days-back 1 --limit 50

# Collect from specific source
news-org collect --source yonhap_economy --limit 100

# View statistics
news-org stats

# Run as daemon (hourly collection)
news-org daemon --interval 3600
```

## Development Workflow

### Environment Setup

```bash
# Install dependencies
pip install -e .

# Run API server
news-org-api

# Run CLI
news-org collect

# Run tests
pytest
```

### Testing

```bash
# Unit tests (fast, no network)
pytest -m unit

# Integration tests (real RSS feeds, network access)
pytest -m integration

# All tests with coverage
pytest --cov=news_org_system --cov-report=term-missing
```

### Deployment Guide

Production 배포를 위한 가이드:

**Complete Guide**: @ai_docs/operations/deployment.md

## Historical Context

### Git Commits
- **b071203**: FastAPI REST API 서비스 레이어 추가
- **c25f956**: Merge #3 - FastAPI 기능 병합

### Design Documents
- **FastAPI Migration**: @openspec/changes/archive/2026-03-20-add-fastapi-service-layer/design.md

## Configuration

### Environment Variables

```bash
# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=news_org
MONGO_COLLECTION=articles

# API Server
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Example**: @.env.example

## Available Sources

| Source | Description | Feed URL | Adapter |
|--------|-------------|----------|---------|
| `yonhap_economy` | 연합뉴스 TV 경제 | Yonhap RSS | yonhap |
| `maeil_management` | 매일경제 매니지먼트 | Maeil RSS | maeil |
| `etnews_today` | 전자신문 오늘 | ETnews RSS | etnews |

## Documentation Structure

```
├── CLAUDE.md                    # 시스템 설계 및 아키텍처 개요 (이 파일)
├── README.api.md                # API 빠른 시작
├── ai_docs/
│   ├── architecture/
│   │   ├── layers.md            # 계층형 아키텍처 상세
│   │   ├── design-decisions.md  # 아키텍처 결정사항
│   │   └── adapter-pattern.md   # 어댑터 패턴 가이드
│   ├── development/
│   │   ├── adding-sources.md    # RSS 피드 추가 가이드
│   │   └── service-extension.md # 서비스 레이어 확장
│   ├── api/
│   │   └── endpoint-reference.md    # API 엔드포인트 레퍼런스
│   ├── ai/
│   │   └── langchain-integration-plan.md  # AI 통합 계획
│   └── operations/
│       └── deployment.md        # 배포 및 운영 가이드
└── openspec/
    └── changes/
        └── archive/
            └── 2026-03-20-add-fastapi-service-layer/
                └── design.md    # FastAPI 설계 문서
```

## Key Files

| File | Purpose |
|------|---------|
| @src/news_org_system/news_api.py | CLI 메인 오케스트레이션 |
| @src/news_org_system/api/main.py | FastAPI 애플리케이션 팩토리 |
| @src/news_org_system/services/collection.py | 뉴스 수집 서비스 |
| @src/news_org_system/readers/registry.py | 피드/어댑터 레지스트리 |
| @src/news_org_system/storage/mongo_store.py | MongoDB 저장소 |

## Architecture Decisions Summary

1. **Service Layer Extraction**: API/CLI 코드 공유, 테스트 가능성
2. **FastAPI Framework**: 타입 안전성, 자동 문서화
3. **Dependency Injection**: 테스트 용이성, 명확한 의존성
4. **DTO Separation**: API/도메인 모델 독립적 evolve
5. **Sync Services**: 간단한 구현, 필요시 async로 마이그레이션 가능

**Full Decisions**: @ai_docs/architecture/design-decisions.md

---

**Last Updated**: 2026-03-21
**Architecture Version**: FastAPI Service Layer (v0.1.0)
**Next Milestone**: LangChain/LangGraph Integration (Phase 1)
