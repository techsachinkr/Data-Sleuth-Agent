from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Intelligence Gathering API",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with service status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Intelligence Gathering API",
        "version": "1.0.0",
        "components": {
            "database": "not_configured",
            "redis": "not_configured",
            "llm_providers": "configured",
            "memory_manager": "active"
        },
        "uptime": "runtime_dependent"
    }