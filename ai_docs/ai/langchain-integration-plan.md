# LangChain & LangGraph Integration Plan

This document outlines the plan for integrating LangChain and LangGraph into the news-org-system to enable AI-powered features.

## Current State

**Dependencies Installed** (from `pyproject.toml`):
- `langchain==1.2.12`
- `langchain-core==1.2.18`
- `langchain-openai==1.1.11`
- `transformers>=5.3.0`
- `spacy>=3.8.11`

**Implementation Status**: None yet
- Dependencies are installed but no AI implementation exists
- Service layer is ready for extension with AIService
- MongoDB storage can accommodate AI-generated fields

## Planned AI Capabilities

### Phase 1: Basic NLP Features (Foundation)

**Goal**: Add fundamental NLP capabilities to enrich article metadata.

#### 1.1 Article Summarization

**Description**: Generate concise summaries of article content.

**Implementation**:
```python
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class SummarizationService:
    """Service for article summarization."""

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=openai_api_key,
            temperature=0.3
        )
        self.chain = self._create_chain()

    def _create_chain(self):
        prompt = PromptTemplate(
            input_variables=["content"],
            template="Summarize the following news article in 2-3 sentences:\n\n{content}\n\nSummary:"
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    def summarize(self, content: str) -> str:
        """Generate summary for article content."""
        result = self.chain.run(content=content)
        return result.strip()
```

**Storage**: Add `summary` field to article documents.
```python
{
    "title": "...",
    "content": "...",
    "summary": "AI-generated summary...",  # New field
    ...
}
```

**API**: New endpoint for summarization:
```python
@router.post("/articles/{article_id}/summarize")
async def summarize_article(article_id: str):
    """Generate summary for an article."""
    # Retrieve article
    # Generate summary
    # Update document with summary
    # Return summary
```

#### 1.2 Sentiment Analysis

**Description**: Classify article sentiment (positive, negative, neutral).

**Implementation**:
```python
from transformers import pipeline

class SentimentService:
    """Service for sentiment analysis."""

    def __init__(self):
        # Use local model (no API cost)
        self.classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )

    def analyze(self, text: str) -> Dict:
        """Analyze sentiment of text."""
        result = self.classifier(text[:512])  # Max 512 tokens
        return {
            "label": result[0]["label"],  # POSITIVE/NEGATIVE
            "score": result[0]["score"]   # Confidence
        }
```

**Storage**: Add `sentiment` field to article documents.
```python
{
    "sentiment": {
        "label": "POSITIVE",
        "score": 0.98
    }
}
```

#### 1.3 Entity Extraction (NER)

**Description**: Extract named entities (people, organizations, locations).

**Implementation**:
```python
import spacy

class EntityExtractionService:
    """Service for named entity recognition."""

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")  # or ko_core_news for Korean

    def extract(self, text: str) -> Dict:
        """Extract entities from text."""
        doc = self.nlp(text)

        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": []
        }

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["persons"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            # ... more entity types

        return entities
```

**Storage**: Add `entities` field to article documents.
```python
{
    "entities": {
        "persons": ["John Doe", "Jane Smith"],
        "organizations": ["Google", "Microsoft"],
        "locations": ["New York", "London"],
        "dates": ["2024-03-21"]
    }
}
```

#### 1.4 Topic Classification

**Description**: Classify articles into topics (e.g., technology, politics, finance).

**Implementation**:
```python
from transformers import pipeline

class TopicClassificationService:
    """Service for topic classification."""

    def __init__(self):
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        self.topics = [
            "technology", "politics", "economy", "sports",
            "entertainment", "health", "science"
        ]

    def classify(self, title: str, content: str) -> List[str]:
        """Classify article into topics."""
        text = f"{title}\n\n{content[:1000]}"  # Limit input
        result = self.classifier(text, self.topics)

        # Return top 3 topics with scores > 0.5
        return [
            {"topic": label, "score": score}
            for label, score in zip(result["labels"], result["scores"])
            if score > 0.5
  ][:3]
```

**Storage**: Add `topics` field to article documents.
```python
{
    "topics": [
        {"topic": "technology", "score": 0.92},
        {"topic": "economy", "score": 0.75}
    ]
}
```

### Phase 2: LangGraph Workflows (Advanced)

**Goal**: Implement multi-step AI workflows using LangGraph.

#### 2.1 Article Processing Pipeline

**Workflow**: Collection → Summarization → Entity Extraction → Sentiment → Storage

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class ArticleProcessingState(TypedDict):
    article: Dict
    summary: str
    entities: Dict
    sentiment: Dict
    topics: List[Dict]
    errors: List[str]

def create_processing_graph():
    """Create LangGraph workflow for article processing."""

    # Define nodes
    async def summarize(state: ArticleProcessingState) -> ArticleProcessingState:
        """Generate summary."""
        try:
            state["summary"] = summarization_service.summarize(
                state["article"]["content"]
            )
        except Exception as e:
            state["errors"].append(f"Summarization failed: {e}")
        return state

    async def extract_entities(state: ArticleProcessingState) -> ArticleProcessingState:
        """Extract entities."""
        try:
            state["entities"] = entity_service.extract(
                state["article"]["content"]
            )
        except Exception as e:
            state["errors"].append(f"Entity extraction failed: {e}")
        return state

    async def analyze_sentiment(state: ArticleProcessingState) -> ArticleProcessingState:
        """Analyze sentiment."""
        try:
            state["sentiment"] = sentiment_service.analyze(
                state["article"]["content"]
            )
        except Exception as e:
            state["errors"].append(f"Sentiment analysis failed: {e}")
        return state

    async def classify_topics(state: ArticleProcessingState) -> ArticleProcessingState:
        """Classify topics."""
        try:
            state["topics"] = topic_service.classify(
                state["article"]["title"],
                state["article"]["content"]
            )
        except Exception as e:
            state["errors"].append(f"Topic classification failed: {e}")
        return state

    async def save_results(state: ArticleProcessingState) -> ArticleProcessingState:
        """Save enriched article to database."""
        # Update article with AI-generated fields
        # Save to MongoDB
        return state

    # Build graph
    graph = StateGraph(ArticleProcessingState)

    # Add nodes
    graph.add_node("summarize", summarize)
    graph.add_node("entities", extract_entities)
    graph.add_node("sentiment", analyze_sentiment)
    graph.add_node("topics", classify_topics)
    graph.add_node("save", save_results)

    # Add edges (sequential execution)
    graph.set_entry_point("summarize")
    graph.add_edge("summarize", "entities")
    graph.add_edge("entities", "sentiment")
    graph.add_edge("sentiment", "topics")
    graph.add_edge("topics", "save")
    graph.add_edge("save", END)

    return graph.compile()

# Usage
async def process_article(article: Dict):
    """Process article through AI pipeline."""
    graph = create_processing_graph()
    state = ArticleProcessingState(
        article=article,
        summary="",
        entities={},
        sentiment={},
        topics=[],
        errors=[]
    )

    result = await graph.ainvoke(state)
    return result
```

#### 2.2 Cross-Article Synthesis

**Goal**: Analyze relationships between multiple articles.

**Use Cases**:
- Cluster related articles
- Identify trending topics across sources
- Detect contradictory information
- Generate news summaries from multiple sources

```python
from langgraph.graph import StateGraph

class SynthesisState(TypedDict):
    articles: List[Dict]
    clusters: Dict[str, List[Dict]]
    trending_topics: List[Dict]
    summary: str

def create_synthesis_graph():
    """Create workflow for cross-article analysis."""

    async def cluster_articles(state: SynthesisState) -> SynthesisState:
        """Cluster articles by similarity."""
        # Use embeddings + clustering
        articles = state["articles"]

        # Generate embeddings
        embeddings = embedding_service.embed_documents([
            f"{a['title']} {a['content'][:500]}"
            for a in articles
        ])

        # Cluster (e.g., K-means, DBSCAN)
        clusters = cluster_service.cluster(embeddings, articles)
        state["clusters"] = clusters

        return state

    async def extract_trends(state: SynthesisState) -> SynthesisState:
        """Extract trending topics."""
        all_topics = []
        for cluster_articles in state["clusters"].values():
            for article in cluster_articles:
                all_topics.extend(article.get("topics", []))

        # Aggregate and rank topics
        topic_counts = Counter([t["topic"] for t in all_topics])
        state["trending_topics"] = [
            {"topic": topic, "count": count}
            for topic, count in topic_counts.most_common(10)
        ]

        return state

    async def generate_summary(state: SynthesisState) -> SynthesisState:
        """Generate summary of multiple articles."""
        # Use LLM to synthesize information
        prompt = f"""
        Summarize the key points from these {len(state['articles'])} news articles.
        Identify the main themes and any consensus or disagreements.

        Articles:
        {format_articles(state['articles'])}
        """

        state["summary"] = llm_service.generate(prompt)
        return state

    # Build graph
    graph = StateGraph(SynthesisState)
    graph.add_node("cluster", cluster_articles)
    graph.add_node("trends", extract_trends)
    graph.add_node("summarize", generate_summary)

    graph.set_entry_point("cluster")
    graph.add_edge("cluster", "trends")
    graph.add_edge("trends", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()
```

### Phase 3: Agent Capabilities (Advanced)

**Goal**: Implement AI agents for intelligent querying and interaction.

#### 3.1 Natural Language Query Interface

**Description**: Query articles using natural language.

**Example**:
```
User: "Show me positive news about AI from the last week"
System: Converts to structured query and executes
```

**Implementation** (using LangChain Agents):
```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool

@tool
def search_articles(query: str, source: str = None, days: int = 7) -> List[Dict]:
    """Search articles with filters.

    Args:
        query: Search keyword
        source: Optional source filter
        days: Number of days to look back

    Returns:
        List of matching articles
    """
    from datetime import datetime, timedelta

    start_date = datetime.now() - timedelta(days=days)

    results = query_service.query_articles(
        keyword=query,
        source=source,
        start_date=start_date
    )

    return results["articles"]

@tool
def get_article_by_id(article_id: str) -> Dict:
    """Get article by ID.

    Args:
        article_id: MongoDB ObjectId

    Returns:
        Article details
    """
    return query_service.get_article_by_id(article_id)

@tool
def get_statistics(source: str = None) -> Dict:
    """Get collection statistics.

    Args:
        source: Optional source filter

    Returns:
        Statistics dictionary
    """
    if source:
        return stats_service.get_source_stats(source)
    return stats_service.get_overall_stats()

# Create agent
tools = [search_articles, get_article_by_id, get_statistics]

agent = create_openai_functions_agent(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    tools=tools,
    prompt=agent_prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# Use agent
response = await agent_executor.ainvoke({
    "input": "Show me positive news about AI from the last week"
})
```

#### 3.2 Multi-Source Correlation

**Description**: Correlate information across multiple sources.

**Use Cases**:
- Identify same story reported differently
- Detect bias in reporting
- Compare coverage across sources

```python
from langchain.chains import ConversationalRetrievalChain

class CorrelationAgent:
    """Agent for cross-source analysis."""

    def __init__(self):
        self.retriever = self._create_retriever()
        self.chain = self._create_chain()

    def _create_retriever(self):
        """Create vector store retriever."""
        # Use embeddings for semantic search
        embeddings = OpenAIEmbeddings()

        # Create vector store from articles
        texts = [f"{a['title']} {a['content']}" for a in articles]
        metadatas = [{"source": a["source"], "url": a["url"]} for a in articles]

        vectorstore = FAISS.from_texts(texts, embeddings, metadatas)
        return vectorstore.as_retriever()

    def _create_chain(self):
        """Create conversational chain."""
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            Based on the following news articles from different sources,
            answer the question. Identify similarities and differences in reporting.

            Articles:
            {context}

            Question: {question}

            Answer:
            """
        )

        return ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(),
            retriever=self.retriever,
            combine_docs_chain_kwargs={"prompt": prompt}
        )

    async def correlate(self, question: str):
        """Answer correlation question."""
        result = await self.chain.ainvoke({
            "question": question,
            "chat_history": []
        })
        return result["answer"]
```

#### 3.3 Trend Detection

**Description**: Detect emerging trends and anomalies.

```python
class TrendDetectionAgent:
    """Agent for detecting trends in news."""

    def __init__(self):
        self.entity_analyzer = EntityExtractionService()
        self.topic_classifier = TopicClassificationService()

    async def detect_trends(self, hours: int = 24) -> Dict:
        """Detect trending topics and entities."""
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(hours=hours)

        # Get recent articles
        articles = query_service.query_articles(
            start_date=cutoff
        )

        # Extract all entities and topics
        all_entities = []
        all_topics = []

        for article in articles["articles"]:
            entities = self.entity_analyzer.extract(article["content"])
            all_entities.extend(entities["organizations"])

            topics = self.topic_classifier.classify(
                article["title"],
                article["content"]
            )
            all_topics.extend(topics)

        # Identify trends (unusual frequency)
        entity_counts = Counter(all_entities)
        topic_counts = Counter([t["topic"] for t in all_topics])

        return {
            "trending_entities": entity_counts.most_common(10),
            "trending_topics": topic_counts.most_common(10),
            "analyzed_at": datetime.now().isoformat()
        }
```

## Integration Architecture

### Service Layer Extension

**New AIService**:
```python
# src/news_org_system/services/ai.py

class AIService:
    """Service for AI-powered article processing."""

    def __init__(
        self,
        store: MongoStore,
        openai_api_key: Optional[str] = None
    ):
        self.store = store
        self.summarizer = SummarizationService(openai_api_key)
        self.sentiment = SentimentService()
        self.entities = EntityExtractionService()
        self.topics = TopicClassificationService()
        self.graph = self._create_processing_graph()

    async def enrich_article(self, article_id: str) -> Dict:
        """Enrich article with AI-generated metadata."""
        # Retrieve article
        article = self.store.get_article_by_id(article_id)

        # Process through LangGraph workflow
        result = await self.graph.ainvoke({
            "article": article,
            "summary": "",
            "entities": {},
            "sentiment": {},
            "topics": [],
            "errors": []
        })

        # Update article in database
        self.store.articles_collection.update_one(
            {"_id": article["_id"]},
            {"$set": {
                "summary": result["summary"],
                "entities": result["entities"],
                "sentiment": result["sentiment"],
                "topics": result["topics"],
                "ai_enriched_at": datetime.now()
            }}
        )

        return result
```

### API Layer Extension

**New AI Endpoints**:
```python
# src/news_org_system/api/routes/ai.py

from fastapi import APIRouter, Depends, BackgroundTasks
from ..services import AIService
from ..dependencies import get_ai_service

router = APIRouter()

@router.post("/articles/{article_id}/enrich")
async def enrich_article(
    article_id: str,
    background_tasks: BackgroundTasks,
    service: AIService = Depends(get_ai_service)
):
    """Enrich article with AI-generated metadata."""
    # Run in background (async operation)
    background_tasks.add_task(service.enrich_article, article_id)

    return {
        "status": "enriching",
        "article_id": article_id,
        "message": "Article enrichment started in background"
    }

@router.get("/articles/{article_id}/summary")
async def get_article_summary(
    article_id: str,
    service: AIService = Depends(get_ai_service)
):
    """Get AI-generated summary for article."""
    article = service.store.get_article_by_id(article_id)

    if not article.get("summary"):
        # Generate summary on-demand
        summary = service.summarizer.summarize(article["content"])

        # Cache it
        service.store.articles_collection.update_one(
            {"_id": article["_id"]},
            {"$set": {"summary": summary}}
        )
    else:
        summary = article["summary"]

    return {"article_id": article_id, "summary": summary}

@router.post("/query/natural")
async def natural_language_query(
    query: str,
    service: AIService = Depends(get_ai_service)
):
    """Query articles using natural language."""
    result = await service.agent_executor.ainvoke({"input": query})
    return result
```

### Data Model Extensions

**Article Schema Updates**:
```python
class Article(BaseModel):
    # Existing fields
    url: str
    title: str
    content: str
    source: str
    published_at: datetime
    crawled_at: datetime
    metadata: Dict[str, Any] = {}

    # New AI-generated fields
    summary: Optional[str] = None
    sentiment: Optional[Dict[str, Any]] = None  # {label, score}
    entities: Optional[Dict[str, List[str]]] = None  # {persons, orgs, locations}
    topics: Optional[List[Dict[str, Any]]] = None  # [{topic, score}]
    ai_enriched_at: Optional[datetime] = None
```

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal**: Basic NLP features

**Tasks**:
1. Create `AIService` class structure
2. Implement `SummarizationService` with LangChain
3. Implement `SentimentService` with transformers
4. Implement `EntityExtractionService` with spaCy
5. Add API endpoints for each feature
6. Update MongoDB indexes for new fields
7. Write unit tests for each service
8. Documentation

**Deliverables**:
- Working summarization endpoint
- Working sentiment analysis endpoint
- Working entity extraction endpoint
- API documentation
- Test coverage > 80%

### Phase 2: LangGraph Workflows (Week 3-4)

**Goal**: Multi-step processing pipelines

**Tasks**:
1. Design article processing state schema
2. Implement LangGraph workflow for enrichment
3. Add background job processing (Celery/asyncio)
4. Create batch enrichment endpoint
5. Implement error handling and retries
6. Add monitoring and logging
7. Performance optimization

**Deliverables**:
- Working LangGraph workflow
- Batch enrichment API
- Error recovery mechanisms
- Performance metrics

### Phase 3: Agent Capabilities (Week 5-6)

**Goal**: Intelligent querying and analysis

**Tasks**:
1. Implement LangChain agent with tools
2. Create natural language query endpoint
3. Implement cross-article synthesis
4. Add trend detection agent
5. Create correlation analysis tools
6. User interface improvements

**Deliverables**:
- Natural language query interface
- Cross-source correlation analysis
- Trend detection and alerts
- Agent documentation

### Phase 4: Production Readiness (Week 7-8)

**Goal**: Production deployment

**Tasks**:
1. Performance optimization (caching, batching)
2. Cost management (OpenAI API usage)
3. Rate limiting and quotas
4. Monitoring and alerting
5. Disaster recovery
6. Security review
7. Load testing
8. Documentation completion

**Deliverables**:
- Production-ready AI features
- Monitoring dashboard
- Cost optimization
- Complete documentation

## Technical Considerations

### Performance Optimization

**Caching Strategy**:
```python
from functools import lru_cache

class CachedAIService:
    """AI service with caching."""

    @lru_cache(maxsize=1000)
    def summarize(self, content_hash: str, content: str) -> str:
        """Generate summary with caching."""
        # Use content hash as cache key
        return self._summarizer.summarize(content)
```

**Batch Processing**:
```python
async def enrich_batch(self, article_ids: List[str]) -> Dict:
    """Enrich multiple articles in batch."""
    # Process in parallel
    tasks = [self.enrich_article(aid) for aid in article_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        "successful": [r for r in results if not isinstance(r, Exception)],
        "failed": [r for r in results if isinstance(r, Exception)]
    }
```

### Cost Management

**OpenAI API Costs**:
- GPT-3.5-turbo: ~$0.002 per 1K tokens
- GPT-4: ~$0.03 per 1K tokens

**Cost Optimization**:
1. Use local models (transformers, spaCy) where possible
2. Cache results to avoid re-computation
3. Batch requests to reduce API calls
4. Use smaller models for prototyping
5. Set rate limits and quotas

**Budget Tracking**:
```python
class CostTrackingService:
    """Track AI processing costs."""

    def __init__(self):
        self.costs = {
            "openai_tokens": 0,
            "openai_cost_usd": 0.0
        }

    def track_api_call(self, model: str, tokens: int):
        """Track API call cost."""
        cost_per_1k = {
            "gpt-3.5-turbo": 0.002,
            "gpt-4": 0.03
        }

        cost = (tokens / 1000) * cost_per_1k[model]
        self.costs["openai_tokens"] += tokens
        self.costs["openai_cost_usd"] += cost
```

### Quality Validation

**Automated Quality Checks**:
```python
class QualityValidator:
    """Validate AI-generated content."""

    def validate_summary(self, content: str, summary: str) -> bool:
        """Check summary quality."""
        # Length check
        if len(summary) < 50 or len(summary) > len(content) // 3:
            return False

        # Content check (should contain key terms)
        content_words = set(content.lower().split())
        summary_words = set(summary.lower().split())

        overlap = len(content_words & summary_words) / len(summary_words)
        if overlap < 0.3:  # At least 30% word overlap
            return False

        return True

    def validate_sentiment(self, sentiment: Dict) -> bool:
        """Check sentiment confidence."""
        return sentiment.get("score", 0) > 0.7
```

### Error Handling

**Graceful Degradation**:
```python
async def enrich_with_fallback(self, article_id: str) -> Dict:
    """Enrich article with fallback on error."""
    result = {"article_id": article_id}

    try:
        result["summary"] = await self.summarizer.summarize(content)
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        result["summary"] = None  # Or use simple extractive summary

    try:
        result["sentiment"] = self.sentiment.analyze(content)
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        result["sentiment"] = None

    # Continue even if some features fail
    return result
```

### Fallback Strategies

**When API Fails**:
1. Use local models (transformers, spaCy)
2. Return partial results
3. Queue for retry
4. Notify monitoring system

**Example**:
```python
class RobustSummarizationService:
    """Summarization with multiple fallbacks."""

    def summarize(self, content: str) -> str:
        """Try multiple strategies."""
        # Strategy 1: OpenAI API (best quality)
        try:
            return self._openai_summarize(content)
        except Exception as e:
            logger.warning(f"OpenAI failed: {e}")

        # Strategy 2: Local model (slower but free)
        try:
            return self._local_summarize(content)
        except Exception as e:
            logger.warning(f"Local model failed: {e}")

        # Strategy 3: Extractive summary (fallback)
        return self._extractive_summary(content)
```

## Testing Strategy

### Unit Tests

```python
import pytest

def test_summarization_service():
    """Test summarization."""
    service = SummarizationService(api_key="test")
    content = "This is a test article..."
    summary = service.summarize(content)

    assert len(summary) > 0
    assert len(summary) < len(content)

def test_sentiment_service():
    """Test sentiment analysis."""
    service = SentimentService()

    positive = service.analyze("Great news today!")
    assert positive["label"] == "POSITIVE"
    assert positive["score"] > 0.5
```

### Integration Tests

```python
@pytest.mark.integration
async def test_enrichment_pipeline():
    """Test full enrichment pipeline."""
    service = AIService(store=store)

    result = await service.enrich_article(article_id)

    assert result["summary"]
    assert result["sentiment"]
    assert result["entities"]
    assert result["topics"]
```

### Performance Tests

```python
@pytest.mark.slow
async def test_batch_enrichment_performance():
    """Test batch enrichment performance."""
    service = AIService(store=store)

    start_time = time.time()
    await service.enrich_batch(article_ids[:100])
    duration = time.time() - start_time

    assert duration < 300  # Should complete in < 5 minutes
```

## Security Considerations

1. **API Key Management**: Store OpenAI API keys securely (environment variables, secrets manager)
2. **Content Filtering**: Prevent malicious content from being processed
3. **Rate Limiting**: Prevent abuse of AI endpoints
4. **Data Privacy**: Don't send sensitive data to external APIs
5. **Audit Logging**: Log all AI processing for compliance

## Monitoring and Metrics

**Key Metrics**:
- AI feature usage (summarization, sentiment, etc.)
- Processing time per feature
- API costs (OpenAI tokens, cost in USD)
- Error rates per feature
- Cache hit rates
- Quality scores (validation results)

**Dashboard**: Future Grafana dashboard for real-time monitoring
