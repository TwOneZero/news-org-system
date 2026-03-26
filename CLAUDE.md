## 1. Project Overview

뉴스 RSS 기반 수집 → MongoDB 저장 → API 제공 → (향후) AI Agent 기반 분석 시스템

핵심 기능:

- RSS/Atom 뉴스 수집
- 기사 저장 및 조회
- 통계 집계
- (Planned) 기업 기반 뉴스 분석 / 감성 분석 / Agentic Search

---

## 2. OpenSpec Usage (Source of Truth)

### 역할 분리 (매우 중요)

- **정확한 요구사항 / 기능 정의**
→ `openspec/specs/`
- **진행 중 작업 (change 단위)**
→ `openspec/changes/<change-id>/`
- **이 파일(CLAUDE.md)**
→ 작업 규칙 / 개발 방식 / 실행 방법

---

### 작업 규칙

- 기능 수정 전 필요 시:
    - 관련 `openspec/specs/` 먼저 읽기
- 진행 중 작업:
    - `openspec/changes/<id>/proposal.md`
    - `design.md`, `tasks.md`, `specs/` 확인
- 수동 코드 수정 후:
    - change 문서 반드시 동기화
    - (`design.md`, `tasks.md`, spec delta)

---

### 권장 워크플로우

```bash
# 작업 시작
/opsx:new
# 구현 진행
/opsx:continue <change-id>
# 수동 수정 후
/opsx-sync-manual <change-id>
# 검증
/opsx:verify <change-id>
# spec merge 검토
/opsx:sync <change-id>
# 완료
archive
```

---

### 규칙

- CLAUDE.md는 spec source가 아니다
- 기능 정의는 항상 OpenSpec 기준
- spec과 코드가 다르면 spec을 먼저 확인

---

## 3. Run & Execution

### API 서버 실행

```
uv run news-org-api
```

또는

```
uvicorn news_org_system.api.main:app--reload
```

---

### CLI

```bash
# 전체 수집
news-org collect
# 특정 소스
news-org collect--source yonhap_economy
# 통계
news-org stats
# 데몬
news-org daemon
```

---

## 4. Testing

```bash
# 전체 테스트
pytest
# unit
pytest -m unit
# integration
pytest -m integration
# coverage
pytest --cov=news_org_system
```

---

## 5. Development Pattern

### Architecture

Layered Architecture

```
API → Service → Data
```

---

### 핵심 패턴

- Service Layer: 비즈니스 로직 분리
- Adapter Pattern: RSS 사이트별 파싱
- Registry Pattern: 피드/어댑터 관리
- Dependency Injection: FastAPI 기반 DI
- Repository: Mongo 접근 추상화

---

### 코드 규칙

- 문자열 대신 Enum 사용 (`SourceName`, `AdapterName`)
- API 모델(Pydantic)과 내부 도메인 모델 분리
- 서비스는 I/O 없이 pure하게 유지
- Mongo 접근은 storage 레이어에서만 수행

**Enum Usage Examples:**

```python
# Import constants
from news_org_system.readers.constants import SourceName, AdapterName

# Using source names in code
source = SourceName.YONHAP_ECONOMY  # Type-safe, IDE autocomplete
print(source)  # "yonhap_economy" - converts to string automatically

# Get feed URL for a source
url = SourceName.get_url(SourceName.YONHAP_ECONOMY)
# Returns: "https://www.yonhapnewstv.co.kr/category/news/economy/feed"

# Using adapter names
adapter = AdapterName.YONHAP  # Instead of "yonhap"

# Benefits:
# - Compile-time type checking
# - IDE autocomplete support
# - Single source of truth
# - Prevents typos
```

---

## 6. Domain Knowledge

### 6.1 News RSS Pipeline

Flow:

```
RSS Feed → Adapter → Article Parse → Mongo 저장 → API 제공
```

핵심 요소:

- RSS는 source마다 구조 다름 → Adapter 필요
- URL 기반 deduplication
- fallback: newspaper4k / bs4

---

### 6.2 확장 방향 (중요)

현재:

- 단순 수집 + 조회

목표:

- 기업 단위 뉴스 aggregation
- 시간 기반 감성 분석
- RAG 기반 검색

---

### 6.3 Agentic Search 구조 (미래 설계)

예상 구조:

```
User Query
  ↓
Agent
  ↓
(1) 기업 추출
(2) 기간 파싱
  ↓
Mongo Query / Vector Search
  ↓
LLM Summary + Sentiment
```

---

## 7. Extension Rules

### RSS 추가

1. `SourceName` enum에 새 소스 추가 (`src/news_org_system/readers/constants.py`):

```python
class SourceName(str, Enum):
    # 기존 소스들...
    YONHAP_ECONOMY = "yonhap_economy"
    YONHAP_ECONOMY_URL = "https://www.yonhapnewstv.co.kr/category/news/economy/feed"

    # 새 소스 추가
    MY_NEW_SOURCE = "my_new_source"
    MY_NEW_SOURCE_URL = "https://example.com/rss.xml"
```

2. `AdapterName` enum에 어댑터 추가 (필요시):

```python
class AdapterName(str, Enum):
    DEFAULT = "default"
    YONHAP = "yonhap"
    # ...
    MY_ADAPTER = "my_adapter"  # 새 어댑터
```

3. `registry.py`에 피드 등록:

```python
from .constants import SourceName, AdapterName

FEED_REGISTRY: Dict[str, RSSFeedConfig] = {
    # 기존 피드들...
    SourceName.MY_NEW_SOURCE: RSSFeedConfig(
        source_name=SourceName.MY_NEW_SOURCE,
        feed_url=SourceName.MY_NEW_SOURCE_URL,
        adapter_name=AdapterName.DEFAULT,
        language="ko",
    ),
}
```

4. 필요시 adapter 작성 (`src/news_org_system/readers/adapters/my_adapter.py`)

---

### 서비스 추가

1. service 클래스 생성
2. DI 등록
3. API 연결

---

### API 추가

1. Pydantic 모델 정의
2. route 생성
3. router 등록

---

## 8. Environment

```
MONGO_URI
MONGO_DATABASE
MONGO_COLLECTION
API_HOST
API_PORT
CORS_ORIGINS
```

---

## 9. Important Principles

- 코드보다 spec이 우선
- 수동 수정 후 반드시 OpenSpec sync
- change 단위로 작업 관리
- CLAUDE.md는 운영 문서 (spec 아님)

---

## 10. One-line Rules

- “기능은 OpenSpec에서 정의한다”
- “코드 수정 후 spec을 따라오게 한다”
- “CLAUDE.md는 행동 규칙만 가진다”