# news-org-system

한국 및 글로벌 뉴스 수집 파이프라인 시스템

## 프로젝트 개요

다양한 뉴스 소스(연합뉴스, 매일경제, BBC 등)와 한국 공시정보(DART)에서 기사와 공시 자료를 자동 수집하여 MongoDB에 저장하는 파이프라인 시스템입니다.

## 핵심 컴포넌트

### [news_api.py](src/news_api.py)

- **NewsCollectionPipeline**: 메인 오케스트레이션 클래스
  - CLI 인터페이스 제공 (`collect`, `stats`, `daemon` 명령)
  - 모든 리더와 스토리지 초기화 및 조정
  - 스케줄링 (매일 9시, 18시) 및 데몬 모드 지원

### [src/readers/](src/readers/)

- **BaseReader**: 추상 베이스 클래스 - 모든 리더의 인터페이스 정의
  - `Article` 데이터 모델 (title, content, url, published_at, source)
- **RSSReader**: RSS/Atom 피드 수집
  - 연합뉴스(뉴스스탠드, 경제), 매일경제(경영/경제), BBC 지원
  - newspaper4k를 통한 전체 기사 본문 추출
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
3. **중복 방지**: URL 기반 인덱싱으로 중복 저장 방지
4. **예외 처리**: 포괄적인 에러 핸들링과 보고
5. **확장성**: 향후 AI/ML 기능 통합을 위한 준비 (langchain 의존성)

## 프로젝트 구조

```text
news-org-system/
├── src/
│   ├── readers/         # 데이터 소스 리더
│   ├── storage/         # MongoDB 저장소
│   └── news_api.py      # 메인 CLI 및 파이프라인
├── test_script          # test script for library logic
├── test/                # pytest folder
└── .env.example         # 환경 변수 템플릿
```
