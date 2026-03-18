# News Organization System

한국 및 글로벌 뉴스 수집 파이프라인 시스템

다양한 뉴스 소스(연합뉴스, 매일경제, ETnews 등)에서 기사를 자동 수집하여 MongoDB에 저장하는 파이프라인 시스템입니다.

## 주요 기능

- **다양한 뉴스 소스 수집**: 연합뉴스, 매일경제, ETnews 등 주요 뉴스 매체의 RSS 피드 자동 수집
- **전체 기사 본문 추출**: newspaper4k 및 beautifulsoup 를 활용한 기사 내용추출
- **중복 제거**: URL 기반 중복 기사 자동 필터링
- **스케줄링**: 매일 지정된 시간에 자동 수집 (9시, 18시)
- **데몬 모드**: 백그라운드에서 지속적인 수집 서비스 실행
- **CLI 인터페이스**: 간편한 명령줄 도구 제공

## 기술 스택

- **Python**: 3.12+
- **데이터 수집**:
  - feedparser (RSS/Atom 피드)
  - beautifulsoup (커스텀 파싱)
  - newspaper4k (기사 본문 추출)
- **데이터베이스**: MongoDB 4.16+
- **스케줄링**: apscheduler
- **의존성 관리**: uv

## 설치

### 사전 요구사항

- Python 3.12 이상
- MongoDB 4.16 이상 (로컬 또는 MongoDB Atlas)

### 1. 저장소 복제

```bash
git clone https://github.com/twonezero/news-org-system.git
cd news-org-system
```

### 2. 가상 환경 설정

```bash
# uv를 사용하는 경우 (권장)
uv venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows

# pip를 사용하는 경우
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows
```

### 3. 의존성 설치

```bash
# uv를 사용하는 경우 (권장)
uv pip install -e .

# pip를 사용하는 경우
pip install -e .
```

### 4. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 환경 변수를 설정합니다:

```bash
# MongoDB 연결 URI
MONGO_URI=mongodb://localhost:27017/
# 또는 MongoDB Atlas를 사용하는 경우
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

## 사용 방법

### 일회성 뉴스 수집

```bash
uv run news-org collect
```

### 데이터베이스 통계 확인

```bash
uv run news-org stats
```

### 데몬 모드로 실행 (매일 9시, 18시 자동 수집)

```bash
uv run news-org daemon
```

### 직접 실행

```bash
python src/news_api.py collect
python src/news_api.py stats
python src/news_api.py daemon
```

## 프로젝트 구조

```text
news-org-system/
├── src/
│   ├── readers/
│   │   ├── __init__.py
│   │   ├── base_reader.py    # BaseReader 추상 클래스
│   │   ├── rss_reader.py     # RSSReader 구현
│   │   └── registry.py       # RSS 피드/어댑터 레지스트리
│   ├── storage/
│   │   ├── __init__.py
│   │   └── mongo_store.py    # MongoStore 구현
│   └── news_api.py           # 메인 CLI 및 파이프라인
├── test/
│   ├── __init__.py
│   └── test_news_pipeline.py # 파이프라인 테스트
├── test_script               # 라이브러리 로직 테스트 스크립트
├── .env.example              # 환경 변수 템플릿
├── .env                      # 환경 변수 (직접 생성 필요)
├── pyproject.toml            # 프로젝트 설정
└── README.md                 # 이 파일
```

## 아키텍처

### 데이터 수집 흐름

1. **NewsCollectionPipeline**이 모든 리더를 초기화
2. 각 리더(RSSReader)가 데이터 소스에서 기사 수집
3. 수집된 기사를 MongoStore에 저장 (URL 기반 중복 제거)
4. 수집 통계 집계 및 출력

### 지원하는 뉴스 소스

- **연합뉴스**: 경제 뉴스
- **매일경제**: 경영/경제 뉴스
- **ETnews**: IT/과학 뉴스

## 설정

### 스케줄 시간 변경

`src/news_api.py`의 `NewsCollectionPipeline`에서 스케줄 시간을 수정할 수 있습니다:

```python
# 기본값: 매일 9시, 18시
scheduler.add_job(collect_job, 'cron', hour=9, minute=0)
scheduler.add_job(collect_job, 'cron', hour=18, minute=0)
```

## 테스트

```bash
# pytest 실행
uv run pytest

# 특정 테스트 파일 실행
uv run pytest test/test_news_pipeline.py

# 상세 출력
uv run pytest -v
```

## 추후 개발 계획

- [ ] 더 많은 뉴스 소스 추가
- [ ] 스케쥴링 및 데이터 분류 업데이트
- [ ] 웹 대시보드 구현
- [ ] AI 기반 뉴스 요약 및 분류
- [ ] 알림 시스템 (이메일, Slack 등)
- [ ] 한국어 외 다국어 지원
- [ ] DART 공시정보 수집 (재개발 예정)
