# api/routes/intelligence.py
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any, Optional, List
import logging
from pydantic import ValidationError

from models.schemas import (
    IntelligenceQueryRequest, 
    InvestigationState, 
    IntelligenceReport
)
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    agent_name: str
    message: str
    timestamp: Optional[datetime] = None

@router.post("/intelligence/investigate", response_model=InvestigationState)
async def start_investigation(
    request: IntelligenceQueryRequest,
    app_request: Request
) -> InvestigationState:
    """Start a new intelligence investigation using the complete agent pipeline"""
    try:
        intelligence_service = app_request.app.state.intelligence_service
        state = await intelligence_service.start_investigation(request)
        return state
    except Exception as e:
        logger.error(f"Error starting investigation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/intelligence/{session_id}/respond", response_model=InvestigationState)
async def respond_to_investigation(
    session_id: str,
    response: Dict[str, str],
    app_request: Request
) -> InvestigationState:
    """Respond to questions in an ongoing investigation using Retrieval & Pivot Agent collaboration"""
    try:
        intelligence_service = app_request.app.state.intelligence_service
        user_response = response.get("response", "")
        
        if not user_response:
            raise HTTPException(status_code=400, detail="Response cannot be empty")
        
        state = await intelligence_service.process_response(session_id, user_response)
        return state
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/{session_id}", response_model=InvestigationState)
async def get_investigation_status(
    session_id: str,
    app_request: Request
) -> InvestigationState:
    """Get current status of an investigation"""
    try:
        intelligence_service = app_request.app.state.intelligence_service
        
        state = intelligence_service.get_investigation_state(session_id)
        if not state:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        return state
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting investigation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/{session_id}/report", response_model=IntelligenceReport)
async def generate_intelligence_report(
    session_id: str,
    app_request: Request
) -> IntelligenceReport:
    """Generate a comprehensive intelligence report using Synthesis & Reporting Agent"""
    try:
        intelligence_service = app_request.app.state.intelligence_service
        
        state = intelligence_service.get_investigation_state(session_id)
        if not state:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        # Use the new synthesis agent to generate the report
        report = await intelligence_service.generate_report(session_id)
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating comprehensive intelligence report: {str(e)}")

@router.get("/intelligence/{session_id}/summary")
async def get_investigation_summary(
    session_id: str,
    app_request: Request
) -> Dict[str, Any]:
    """Get a summary of the investigation progress"""
    try:
        intelligence_service = app_request.app.state.intelligence_service
        summary = await intelligence_service.get_investigation_summary(session_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting investigation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/intelligence/{session_id}")
async def close_investigation(
    session_id: str,
    app_request: Request
) -> Dict[str, str]:
    """Close an investigation and clean up resources"""
    try:
        intelligence_service = app_request.app.state.intelligence_service
        
        state = intelligence_service.get_investigation_state(session_id)
        if state:
            del intelligence_service.active_investigations[session_id]
            logger.info(f"Investigation {session_id} closed")
            return {"message": "Investigation closed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Investigation not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing investigation: {e}")
        raise HTTPException(status_code=500, detail=str(e))