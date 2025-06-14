from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, List
import json
import os,sys
sys.path.append(os.getcwd())
from api.routes import intelligence, health, websocket
from core.config import get_settings
from core.logging_config import setup_logging
from services.intelligence_service import IntelligenceService
from services.websocket_manager import WebSocketManager

# Initialize settings and logging
settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

# Global service instances
intelligence_service = None
websocket_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global intelligence_service, websocket_manager
    
    # Startup
    logger.info("Starting Intelligence Gathering Service...")
    intelligence_service = IntelligenceService()
    websocket_manager = WebSocketManager()
    
    # Make services available to routes
    app.state.intelligence_service = intelligence_service
    app.state.websocket_manager = websocket_manager
    
    yield
    
    # Shutdown
    logger.info("Shutting down Intelligence Gathering Service...")
    if websocket_manager:
        await websocket_manager.disconnect_all()

# Create FastAPI app
app = FastAPI(
    title="Intelligence Gathering API",
    description="Advanced AI-powered intelligence gathering system with multi-agent architecture",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(intelligence.router, prefix="/api/v1", tags=["Intelligence"])
app.include_router(websocket.router, prefix="/api/v1", tags=["WebSocket"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )