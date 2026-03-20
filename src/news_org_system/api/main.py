"""FastAPI application for news collection system."""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ..readers.registry import FEED_REGISTRY
from .routes import collection, query, stats, health
from . import dependencies

load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting News Collection System API")
    store = dependencies.get_store()
    logger.info(f"MongoDB connected: {store.db.name}")
    yield
    # Shutdown
    logger.info("Shutting down News Collection System API")
    dependencies._store = None


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        lifespan=lifespan,
        title="News Collection System API",
        description="REST API for collecting and querying news articles from RSS feeds",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:8000"
        ).split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health.router, tags=["Health"])
    app.include_router(collection.router, prefix="/api/v1", tags=["Collection"])
    app.include_router(query.router, prefix="/api/v1", tags=["Query"])
    app.include_router(stats.router, prefix="/api/v1", tags=["Statistics"])

    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "detail": None,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "status_code": 500,
            },
        )

    return app


# Create app instance for importing
app = create_app()


def run_server(
    host: str = None,
    port: int = None,
    reload: bool = False,
):
    """Run the FastAPI server.

    Args:
        host: Host to bind to (defaults to API_HOST env var or 0.0.0.0)
        port: Port to bind to (defaults to API_PORT env var or 8000)
        reload: Enable auto-reload for development
    """
    import uvicorn

    host = host or os.getenv("API_HOST", "0.0.0.0")
    port = port or int(os.getenv("API_PORT", "8000"))

    uvicorn.run(
        "news_org_system.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()


def main():
    """Main entry point for the API server.

    This can be called from the command line entry point.
    """
    run_server()
