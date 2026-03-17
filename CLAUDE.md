# news-org-system

한국 및 글로벌 뉴스 수집 파이프라인 시스템

## 프로젝트 개요

다양한 뉴스 소스(연합뉴스, 매일경제, ETnews 등)와 한국 공시정보(DART)에서 기사와 공시 자료를 자동 수집하여 MongoDB에 저장하는 파이프라인 시스템입니다.

## 핵심 컴포넌트

### [news_api.py](src/news_api.py)

- **NewsCollectionPipeline**: 메인 오케스트레이션 클래스
  - CLI 인터페이스 제공 (`collect`, `stats`, `daemon` 명령)
  - 모든 리더와 스토리지 초기화 및 조정
  - 스케줄링 (매일 9시, 18시) 및 데몬 모드 지원

### [src/readers/](src/readers/)

#### 모듈 구조

- **BaseReader**: 추상 베이스 클래스 - 모든 리더의 인터페이스 정의
  - `Article` 데이터 모델 (title, content, url, published_at, source)

#### RSS Reader (어댑터 패턴)

- **RSSReader**: 어댑터 패턴 기반 RSS/Atom 피드 수집
  - `from_source()` 클래스 메서드로 레지스트리에서 피드 설정 로드
  - 사이트별 파서 어댑터를 통한 유연한 컨텐츠 추출
  - 연합뉴스(경제), 매일경제(경영/경제), ETnews 지원
  - newspaper4k를 통한 전체 기사 본문 추출

#### 모델 (Pydantic)

- **RSSFeedConfig**: RSS 피드 설정 (source_name, feed_url, adapter_name, language)
- **RSSItem**: 표준화된 RSS 아이템 필드
- **SiteConfig**: 사이트별 크롤링 설정 (언어, user_agent, timeout 등)

#### 어댑터 ([adapters/](src/readers/adapters/))

- **BaseRSSAdapter**: 추상 어댑터 베이스 클래스
- **DefaultRSSAdapter**: 표준 RSS/Atom 파서 (대부분의 사이트에 사용)
- **YonhapAdapter**: 연합뉴스 전용 파서
- **MaeliAdapter**: 매일경제 전용 파서
- **ETnewsAdapter**: ETnews 전용 파서

#### 레지스트리 ([registry.py](src/readers/registry.py))

- **FEED_REGISTRY**: 등록된 RSS 피드 설정들
- **ADAPTER_REGISTRY**: 등록된 어댑터 클래스들
- `get_adapter()`, `get_feed_config()`, `register_feed()` 등의 헬퍼 함수

#### DART Reader

- **DARTReader**: 한국 공시정보 수집
  - dart-fss 라이브러리 사용
  - 기업 코드 조회 및 공시 문서 검색/수집

### [src/storage/](src/storage/)

- **MongoStore**: MongoDB 기반 영구 저장소
  - URL 기반 중복 제거
  - 날짜/소스 기반 효율적인 인덱싱
  - 통계 집계 기능

## 기술 스택

**데이터 수집**: feedparser, newspaper4k, dart-fss
**데이터 모델링**: pydantic
**저장소**: pymongo (MongoDB)
**스케줄링**: apscheduler
**NLP/ML**: spacy, transformers (FinBERT - 연구용)

## 설정 요구사항

### 필수 환경 변수 (`.env`)

```bash
MONGO_URI=mongo_db_atlas_uri
DART_API_KEY=your_dart_api_key_here  # https://opendart.fss.or.kr/ 에서 무료 발급
```

### 의존성

- Python 3.12+
- MongoDB 4.16+
- 가상 환경 권장

## 사용 패턴

```bash
# 일회성 수집
uv run news_org collect

# 데이터베이스 통계 확인
uv run news-org stats

# 스케줄된 데몬으로 실행 (매일 9시, 18시)
uv run news-org daemon
```

## 아키텍처 원칙

1. **모듈형 리더 설계**: 새로운 데이터 소스 추가가 용이한 플러그인 아키텍처
2. **추상화 계층**: BaseReader를 통한 일관된 인터페이스 보장
3. **어댑터 패턴**: 사이트별 파서를 독립적인 어댑터 클래스로 분리하여 확장성 확보
4. **중앙 설정 관리**: 레지스트리 패턴으로 피드 URL과 어댑터를 중앙에서 관리
5. **타입 안전성**: Pydantic 모델로 데이터 검증 및 타입 안전성 확보
6. **중복 방지**: URL 기반 인덱싱으로 중복 저장 방지
7. **예외 처리**: 포괄적인 에러 핸들링과 보고
8. **확장성**: 향후 AI/ML 기능 통합을 위한 준비 (langchain 의존성)

## 프로젝트 구조

```text
news-org-system/
├── src/
│   ├── readers/
│   │   ├── models/      # Pydantic 데이터 모델 (RSSFeedConfig, SiteConfig)
│   │   ├── adapters/    # 사이트별 파서 어댑터
│   │   ├── base_reader.py
│   │   ├── rss_reader.py
│   │   ├── dart_reader.py
│   │   └── registry.py  # 피드/어댑터 레지스트리
│   ├── storage/         # MongoDB 저장소
│   └── news_api.py      # 메인 CLI 및 파이프라인
├── test_script          # test script for library logic
├── test/                # pytest folder
└── .env.example         # 환경 변수 템플릿
```

## 새로운 뉴스 소스 추가 방법

어댑터 패턴과 레지스트리 시스템을 통해 새로운 뉴스 소스를 쉽게 추가할 수 있습니다.

### 방법 1: 기존 어댑터 사용 (대부분의 경우)

대부분의 표준 RSS/Atom 피드는 `DefaultAdapter`로 처리 가능합니다:

```python
# src/readers/registry.py
from .models.rss_config import RSSFeedConfig

# 새 피드 등록
FEED_REGISTRY["my_source"] = RSSFeedConfig(
    source_name="my_source",
    feed_url="https://example.com/rss.xml",
    adapter_name="default",  # 기본 어댑터 사용
    language="ko",
)
```

### 방법 2: 커스텀 어댑터 생성 (사이트 특화 로직 필요 시)

비표준 RSS 구조나 특별한 처리가 필요한 경우:

```python
# src/readers/adapters/my_source_adapter.py
from .default_adapter import DefaultRSSAdapter

class MySourceAdapter(DefaultRSSAdapter):
    """사이트 특화 로직이 필요할 때만 커스텀 어댑터 생성"""

    def extract_content(self, entry) -> str:
        # 사이트 특화 컨텐츠 추출 로직
        content = super().extract_content(entry)

        # 추가 처리가 필요한 경우
        # 예: 특정 태그 제거, 이미지 처리 등
        return content
```

```python
# src/readers/registry.py
from .adapters.my_source_adapter import MySourceAdapter

# 어댑터 등록
ADAPTER_REGISTRY["my_source"] = MySourceAdapter

# 피드 등록
FEED_REGISTRY["my_source"] = RSSFeedConfig(
    source_name="my_source",
    feed_url="https://example.com/rss.xml",
    adapter_name="my_source",
)
```

### 사용 예시

```python
# 레지스트리에서 로드
from src.readers import RSSReader

reader = RSSReader.from_source("my_source")
articles = reader.fetch(limit=10)

# 또는 직접 초기화
reader = RSSReader(
    source_name="my_source",
    feed_url="https://example.com/rss.xml",
    adapter_name="default"
)
articles = reader.fetch(limit=10)
```
