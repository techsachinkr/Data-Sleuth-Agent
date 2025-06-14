# services/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List
import logging
import json
from datetime import datetime

from models.schemas import WebSocketMessage

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """Connect a WebSocket for a session"""
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connected for session {session_id}")
    
    async def disconnect(self, session_id: str, websocket: WebSocket = None):
        """Disconnect a specific WebSocket or all for a session"""
        if session_id in self.active_connections:
            if websocket:
                try:
                    self.active_connections[session_id].remove(websocket)
                except ValueError:
                    pass
            else:
                # Disconnect all for this session
                self.active_connections[session_id] = []
            
            # Clean up empty sessions
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def disconnect_all(self):
        """Disconnect all WebSocket connections"""
        for session_id in list(self.active_connections.keys()):
            connections = self.active_connections[session_id].copy()
            for websocket in connections:
                try:
                    await websocket.close()
                except Exception as e:
                    logger.error(f"Error closing WebSocket: {e}")
        
        self.active_connections.clear()
        logger.info("All WebSocket connections closed")
    
    async def send_personal_message(self, message: str, session_id: str):
        """Send a message to all connections for a specific session"""
        if session_id in self.active_connections:
            connections = self.active_connections[session_id].copy()
            for websocket in connections:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to WebSocket: {e}")
                    # Remove failed connection
                    await self.disconnect(session_id, websocket)
    
    async def broadcast_message(self, message: str):
        """Broadcast a message to all connected clients"""
        for session_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, session_id)
    
    async def send_investigation_update(self, session_id: str, update_type: str, data: Dict):
        """Send investigation update to session"""
        message = WebSocketMessage(
            type=update_type,
            data=data,
            timestamp=datetime.now()
        )
        await self.send_personal_message(message.model_dump_json(), session_id)