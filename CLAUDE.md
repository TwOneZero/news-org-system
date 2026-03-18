# news-org-system

한국 및 글로벌 뉴스 수집 파이프라인 시스템

## 프로젝트 컨셉

RSS/Atom 피드 기반 뉴스 수집 파이프라인으로, 어댑터 패턴을 통해 다양한 뉴스 소스를 유연하게 확장할 수 있는 시스템입니다.

## 아키텍처 원칙

1. **어댑터 패턴**: 사이트별 파서를 독립적인 어댑터 클래스로 분리
2. **레지스트리 패턴**: 피드 URL과 어댑터를 중앙에서 관리
3. **추상화 계층**: BaseReader를 통한 일관된 인터페이스 보장
4. **타입 안전성**: Pydantic 모델로 데이터 검증
5. **중복 방지**: URL 기반 인덱싱으로 중복 저장 방지

## 핵심 컴포넌트

### [news_api.py](src/news_org_system/news_api.py)
CLI 인터페이스 (`collect`, `stats`, `daemon` 명령)와 스케줄링을 담당하는 메인 오케스트레이션 클래스

### [src/readers/](src/news_org_system/readers/)

- **BaseReader**: 추상 베이스 클래스, `Article` 데이터 모델 정의
- **RSSReader**: 어댑터 패턴 기반 RSS/Atom 피드 수집
- **registry.py**: 피드/어댑터 레지스트리

### [adapters/](src/news_org_system/readers/adapters/)
사이트별 파서 어댑터 (Default, Yonhap, Maeli, ETnews)

### [src/storage/](src/news_org_system/storage/)
MongoStore - URL 기반 중복 제거, 인덱싱, 통계 집계

## 새로운 뉴스 소스 추가

```python
# src/readers/registry.py
FEED_REGISTRY["my_source"] = RSSFeedConfig(
    source_name="my_source",
    feed_url="https://example.com/rss.xml",
    adapter_name="default",  # 또는 커스텀 어댑터
    language="ko",
)
```

## 기술 스택

- Python 3.12+
- MongoDB 4.16+
- feedparser, newspaper4k, pydantic, pymongo, apscheduler

## 환경 변수 (.env.example)

```bash
MONGO_URI=mongodb://localhost:27017
```

## 추후 개발 계획

### 향후 로드맵

1. **FastAPI 웹 서비스**: REST API 엔드포인트 구현
2. **LangGraph 감성 분석**: 뉴스와 공시 자료를 조합한 종합 감성 분석 워크플로우
3. **웹 대시보드**: 종목별 감성 트렌드 시각화

---

**참고**: 현재는 RSS 뉴스 기사 수집 기능만 활성화되어 있습니다.
