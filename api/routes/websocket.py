# api/routes/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
import logging
import json
from datetime import datetime
from typing import Dict, Any

from models.schemas import WebSocketMessage

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time investigation updates"""
    await websocket.accept()
    
    # Get websocket manager from app state
    websocket_manager = websocket.application.state.websocket_manager
    
    try:
        # Register connection
        await websocket_manager.connect(session_id, websocket)
        
        # Send welcome message
        welcome_msg = WebSocketMessage(
            type="connection",
            data={"message": f"Connected to investigation {session_id}"}
        )
        await websocket.send_text(welcome_msg.model_dump_json())
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                
                # Echo back for demo (in real implementation, process the message)
                response_msg = WebSocketMessage(
                    type="response",
                    data={"echo": message_data, "received_at": datetime.now().isoformat()}
                )
                await websocket.send_text(response_msg.model_dump_json())
                
            except json.JSONDecodeError:
                error_msg = WebSocketMessage(
                    type="error",
                    data={"message": "Invalid JSON format"}
                )
                await websocket.send_text(error_msg.model_dump_json())
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        await websocket_manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        await websocket_manager.disconnect(session_id)