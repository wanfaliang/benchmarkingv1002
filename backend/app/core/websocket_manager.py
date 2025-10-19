"""WebSocket connection manager for real-time updates"""
from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store connections by analysis_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store connections by user_id for broadcasting
        self.user_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, analysis_id: str, user_id: str):
        """Accept and register a new WebSocket connection"""
        # await websocket.accept()
        
        # Add to analysis-specific connections
        if analysis_id not in self.active_connections:
            self.active_connections[analysis_id] = set()
        self.active_connections[analysis_id].add(websocket)
        
        # Add to user-specific connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        print(f"WebSocket connected: analysis={analysis_id}, user={user_id}")
    
    def disconnect(self, websocket: WebSocket, analysis_id: str, user_id: str):
        """Remove a WebSocket connection"""
        # Remove from analysis connections
        if analysis_id in self.active_connections:
            self.active_connections[analysis_id].discard(websocket)
            if not self.active_connections[analysis_id]:
                del self.active_connections[analysis_id]
        
        # Remove from user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        print(f"WebSocket disconnected: analysis={analysis_id}, user={user_id}")
    
    async def send_analysis_update(self, analysis_id: str, message: dict):
        """Send update to all connections watching a specific analysis"""
        if analysis_id not in self.active_connections:
            return
        
        # Add timestamp to message
        message['timestamp'] = datetime.utcnow().isoformat()
        
        # Send to all connected clients for this analysis
        disconnected = set()
        for connection in self.active_connections[analysis_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections[analysis_id].discard(connection)
    
    async def send_user_update(self, user_id: str, message: dict):
        """Send update to all connections for a specific user"""
        if user_id not in self.user_connections:
            return
        
        message['timestamp'] = datetime.utcnow().isoformat()
        
        disconnected = set()
        for connection in self.user_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)
        
        for connection in disconnected:
            self.user_connections[user_id].discard(connection)
    
    async def broadcast_progress(
        self, 
        analysis_id: str,
        progress: int,
        message: str,
        status: str = None,
        phase: str = None,
        metadata: dict = None
    ):
        """Broadcast progress update for an analysis"""
        update = {
            'type': 'progress',
            'analysis_id': analysis_id,
            'progress': progress,
            'message': message,
            'status': status,
            'phase': phase,
            'metadata': metadata or {}
        }
        await self.send_analysis_update(analysis_id, update)
    
    async def broadcast_section_update(
        self,
        analysis_id: str,
        section_number: int,
        section_name: str,
        status: str,
        error_message: str = None
    ):
        """Broadcast section generation update"""
        update = {
            'type': 'section_update',
            'analysis_id': analysis_id,
            'section': {
                'number': section_number,
                'name': section_name,
                'status': status,
                'error_message': error_message
            }
        }
        await self.send_analysis_update(analysis_id, update)
    
    async def broadcast_error(self, analysis_id: str, error: str):
        """Broadcast error to all connections for an analysis"""
        update = {
            'type': 'error',
            'analysis_id': analysis_id,
            'error': error
        }
        await self.send_analysis_update(analysis_id, update)
    
    async def broadcast_completion(self, analysis_id: str, status: str):
        """Broadcast completion status"""
        update = {
            'type': 'completion',
            'analysis_id': analysis_id,
            'status': status
        }
        await self.send_analysis_update(analysis_id, update)

# Global manager instance
manager = ConnectionManager()