"""
WebSocket router for real-time calculations
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime

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
            await self.active_connections[user_id].send_json(message)

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
    try:
        # Get chart
        chart = db.query(Chart).filter(
            Chart.id == chart_id,
            Chart.user_id == user_id
        ).first()
        
        if not chart:
            await manager.send_message(user_id, {
                "status": "error",
                "message": "Chart not found"
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
                "message": f"Unknown calculation type: {calculation_type}"
            })
            return
        
        # Send result
        await manager.send_message(user_id, {
            "status": "success",
            "calculation_type": calculation_type,
            "chart_id": chart_id,
            "result": result
        })
        
    except Exception as e:
        await manager.send_message(user_id, {
            "status": "error",
            "message": str(e)
        })

# WebSocket endpoint
@router.websocket("/ws/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time calculations"""
    try:
        # Verify token and get user
        user = await get_current_user(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Connect
        await manager.connect(websocket, str(user.id))
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Validate message format
                if not all(k in message for k in ["chart_id", "calculation_type", "parameters"]):
                    await manager.send_message(str(user.id), {
                        "status": "error",
                        "message": "Invalid message format"
                    })
                    continue
                
                # Process calculation
                await process_calculation(
                    websocket,
                    str(user.id),
                    message["chart_id"],
                    message["calculation_type"],
                    message["parameters"],
                    db
                )
                
        except WebSocketDisconnect:
            manager.disconnect(str(user.id))
            
    except Exception as e:
        if websocket.client_state.CONNECTED:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR) 