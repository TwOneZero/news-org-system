"""Health check endpoint."""

from datetime import datetime
from fastapi import APIRouter, Depends

from ...storage import MongoStore
from ..dependencies import get_store

router = APIRouter()


@router.get("/health", status_code=200)
async def health_check(store: MongoStore = Depends(get_store)):
    """Health check endpoint.

    Returns the health status of the API and its dependencies.
    """
    # Check MongoDB connection
    mongo_status = "disconnected"
    try:
        store.client.admin.command('ping')
        mongo_status = "connected"
    except Exception:
        pass

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mongodb": mongo_status,
        },
    }
