"""
WebSocket router for real-time calculations
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import logging

from nocturna_calculations.api.database import get_db
from nocturna_calculations.api.models import User, Chart
from nocturna_calculations.api.routers.auth import get_current_user
from nocturna_calculations.core.chart import Chart as CoreChart
from nocturna_calculations.core.config import Config as CoreConfig

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                # Log error and remove stale connection
                logging.error(f"Failed to send message to user {user_id}: {e}")
                self.disconnect(user_id)
    
    def get_connection_count(self) -> int:
        """Get the count of active connections."""
        return len(self.active_connections)
    
    def get_connected_users(self) -> List[str]:
        """Get list of connected user IDs."""
        return list(self.active_connections.keys())
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected users."""
        disconnected_users = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logging.error(f"Failed to broadcast to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Clean up failed connections
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    async def cleanup_stale_connections(self):
        """Clean up stale/closed connections."""
        stale_users = []
        for user_id, websocket in self.active_connections.items():
            try:
                # Check if connection is still active
                if hasattr(websocket, 'client_state') and not websocket.client_state.CONNECTED:
                    stale_users.append(user_id)
            except Exception:
                # If we can't check the state, consider it stale
                stale_users.append(user_id)
        
        # Remove stale connections
        for user_id in stale_users:
            self.disconnect(user_id)

manager = ConnectionManager()

# Helper functions
def create_core_chart(db_chart: Chart) -> CoreChart:
    """Create core chart instance from database chart"""
    config = CoreConfig(
        house_system=db_chart.config["house_system"],
        aspects=db_chart.config["aspects"],
        orbs=db_chart.config["orbs"]
    )
    return CoreChart(
        date=db_chart.date,
        latitude=db_chart.latitude,
        longitude=db_chart.longitude,
        timezone=db_chart.timezone,
        config=config
    )

async def process_calculation(
    websocket: WebSocket,
    user_id: str,
    chart_id: str,
    calculation_type: str,
    parameters: dict,
    db: Session
):
    """Process calculation request and send results"""
    logger = logging.getLogger(__name__)
    
    try:
        # Get chart
        chart = db.query(Chart).filter(
            Chart.id == chart_id,
            Chart.user_id == user_id
        ).first()
        
        if not chart:
            await manager.send_message(user_id, {
                "status": "error",
                "message": "Chart not found",
                "chart_id": chart_id
            })
            return
        
        # Create core chart
        core_chart = create_core_chart(chart)
        
        # Perform calculation
        result = None
        if calculation_type == "positions":
            result = core_chart.calculate_planetary_positions(**parameters)
        elif calculation_type == "aspects":
            result = core_chart.calculate_aspects(**parameters)
        elif calculation_type == "houses":
            result = core_chart.calculate_houses(**parameters)
        elif calculation_type == "fixed_stars":
            result = core_chart.calculate_fixed_stars(**parameters)
        elif calculation_type == "arabic_parts":
            result = core_chart.calculate_arabic_parts(**parameters)
        elif calculation_type == "dignities":
            result = core_chart.calculate_dignities(**parameters)
        elif calculation_type == "antiscia":
            result = core_chart.calculate_antiscia(**parameters)
        elif calculation_type == "declinations":
            result = core_chart.calculate_declinations(**parameters)
        elif calculation_type == "harmonics":
            result = core_chart.calculate_harmonics(**parameters)
        elif calculation_type == "rectification":
            result = core_chart.calculate_rectification(**parameters)
        else:
            await manager.send_message(user_id, {
                "status": "error",
                "message": f"Unknown calculation type: {calculation_type}",
                "calculation_type": calculation_type
            })
            return
        
        # Send result
        await manager.send_message(user_id, {
            "status": "success",
            "calculation_type": calculation_type,
            "chart_id": chart_id,
            "result": result
        })
        
        logger.info(f"Calculation completed for user {user_id}, type: {calculation_type}")
        
    except Exception as e:
        logger.error(f"Calculation failed for user {user_id}: {str(e)}", exc_info=True)
        await manager.send_message(user_id, {
            "status": "error",
            "message": f"Calculation failed: {str(e)}",
            "calculation_type": calculation_type,
            "chart_id": chart_id
        })

# WebSocket endpoint
@router.websocket("/ws/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time calculations"""
    logger = logging.getLogger(__name__)
    user_id = None
    
    try:
        # Verify token and get user
        user = await get_current_user(token, db)
        if not user:
            logger.warning(f"WebSocket connection rejected: invalid token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        user_id = str(user.id)
        logger.info(f"WebSocket connection established for user {user_id}")
        
        # Connect
        await manager.connect(websocket, user_id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from user {user_id}: {e}")
                    await manager.send_message(user_id, {
                        "status": "error",
                        "message": "Invalid JSON format"
                    })
                    continue
                
                # Validate message format
                required_fields = ["chart_id", "calculation_type", "parameters"]
                if not all(k in message for k in required_fields):
                    logger.error(f"Invalid message format from user {user_id}: missing fields")
                    await manager.send_message(user_id, {
                        "status": "error",
                        "message": "Invalid message format. Required fields: chart_id, calculation_type, parameters"
                    })
                    continue
                
                # Process calculation
                await process_calculation(
                    websocket,
                    user_id,
                    message["chart_id"],
                    message["calculation_type"],
                    message["parameters"],
                    db
                )
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
            
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}", exc_info=True)
        if websocket.client_state.CONNECTED:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        # Cleanup connection
        if user_id:
            manager.disconnect(user_id)
            logger.info(f"WebSocket connection cleaned up for user {user_id}") 