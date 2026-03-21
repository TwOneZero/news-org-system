# AI Documentation

This directory contains detailed documentation for the news-org-system, organized by topic.

## Documentation Structure

### Architecture (@architecture/)

Design and architecture documentation for the system.

- **[layers.md](architecture/layers.md)** - Complete guide to the layered architecture
  - API Layer: FastAPI structure, routes, dependency injection
  - Service Layer: Business logic orchestration
  - Data Layer: Readers and storage
  - Inter-layer communication patterns
  - Testing strategies per layer

- **[design-decisions.md](architecture/design-decisions.md)** - Architectural decision records
  - Service layer extraction rationale
  - FastAPI framework selection
  - Dependency injection pattern
  - DTO separation strategy
  - Sync vs async trade-offs
  - Historical context from commit b071203

- **[adapter-pattern.md](architecture/adapter-pattern.md)** - Adapter pattern guide
  - BaseRSSAdapter interface
  - Adapter implementation examples
  - Creating custom adapters
  - Common edge cases and error handling
  - Best practices

### Development (@development/)

Guides for extending and modifying the system.

- **[adding-sources.md](development/adding-sources.md)** - Adding new RSS feeds
  - Feed registry configuration
  - Choosing or creating adapters
  - Testing new sources
  - Common pitfalls and solutions
  - Complete examples

- **[service-extension.md](development/service-extension.md)** - Extending the service layer
  - Creating new services
  - Dependency injection patterns
  - Common patterns (pagination, filtering, batch processing)
  - Testing services
  - Integrating with API and CLI

### API (@api/)

API documentation and reference.

- **[endpoint-reference.md](api/endpoint-reference.md)** - Complete API endpoint reference
  - All endpoints with request/response formats
  - Query parameters and filters
  - Error responses and status codes
  - Usage examples (curl, Python, JavaScript)
  - Authentication and CORS configuration
  - Integration examples

### AI (@ai/)

AI and machine learning integration plans.

- **[langchain-integration-plan.md](ai/langchain-integration-plan.md)** - LangChain/LangGraph integration design
  - Current state (dependencies ready, no implementation)
  - Planned AI capabilities (summarization, sentiment, entities)
  - LangGraph workflow design
  - Agent capabilities (natural language queries)
  - Implementation roadmap (4 phases)
  - Technical considerations (cost, performance, quality)

### Operations (@operations/)

Deployment and operations guides.

- **[deployment.md](operations/deployment.md)** - Deployment and operations guide
  - Environment setup and configuration
  - Running CLI and API modes
  - MongoDB configuration and indexing
  - Monitoring and logging
  - Scaling considerations
  - Backup and recovery procedures
  - Production checklist

## Quick Reference

### For System Design
Start with @CLAUDE.md for system overview, then dive into:
- @ai_docs/architecture/layers.md - Layer architecture details
- @ai_docs/architecture/design-decisions.md - Architectural decisions

### For Adding Features
- New RSS sources: @ai_docs/development/adding-sources.md
- New services: @ai_docs/development/service-extension.md
- New API endpoints: @ai_docs/api/endpoint-reference.md

### For AI Integration
- Complete plan: @ai_docs/ai/langchain-integration-plan.md
- Service patterns: @ai_docs/development/service-extension.md

### For Deployment
- Production deployment: @ai_docs/operations/deployment.md
- API usage: @README.api.md

## Conventions

### File Linking
Use `@` symbol to link to project files:
- `@src/news_org_system/services/collection.py`
- `@README.api.md`
- `@.env.example`

### Section Linking
Use Markdown anchors for internal links:
- `#api-endpoints` for sections within the same file
- `@ai_docs/architecture/layers.md#api-layer` for cross-file links

### Code Examples
All code examples are tested and ready to run:
- Python examples include necessary imports
- Bash commands can be copied directly
- Configuration examples are complete

## Contributing

When adding new documentation:

1. **Choose the right location**: Architecture, Development, API, AI, or Operations
2. **Follow existing patterns**: Use similar structure and formatting
3. **Include examples**: Code examples for clarity
4. **Cross-reference**: Link to related documentation
5. **Update index**: Add new files to this README

## Maintenance

### Regular Updates
- Update architecture docs after structural changes
- Keep API docs in sync with code changes
- Refresh AI plans as implementation progresses
- Review deployment docs for accuracy

### Version Control
Documentation is version-controlled with the codebase. Historical context is preserved through git commits and references to design documents.

## Related Documentation

- **Project Root**: @CLAUDE.md (system design overview)
- **API Quick Start**: @README.api.md
- **Dependencies**: @pyproject.toml
- **Configuration**: @.env.example
- **Design History**: @openspec/changes/archive/2026-03-20-add-fastapi-service-layer/design.md

---

**Last Updated**: 2026-03-21
**Documentation Version**: 0.1.0
