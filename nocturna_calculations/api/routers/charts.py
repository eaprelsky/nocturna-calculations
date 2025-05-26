"""
Charts router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from nocturna_calculations.api.database import get_db
from nocturna_calculations.api.models import User, Chart
from nocturna_calculations.api.routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class ChartConfig(BaseModel):
    house_system: str
    aspects: List[str]
    orbs: dict

class ChartCreate(BaseModel):
    date: datetime
    latitude: float
    longitude: float
    timezone: str
    config: ChartConfig

class ChartUpdate(BaseModel):
    config: Optional[ChartConfig] = None

class ChartResponse(BaseModel):
    id: str
    date: datetime
    latitude: float
    longitude: float
    timezone: str
    config: ChartConfig
    created_at: datetime
    updated_at: datetime

# Endpoints
@router.post("", response_model=ChartResponse)
async def create_chart(
    chart_data: ChartCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new chart"""
    chart = Chart(
        user_id=current_user.id,
        date=chart_data.date,
        latitude=chart_data.latitude,
        longitude=chart_data.longitude,
        timezone=chart_data.timezone,
        config=chart_data.config.dict()
    )
    db.add(chart)
    db.commit()
    db.refresh(chart)
    return chart

@router.get("/{chart_id}", response_model=ChartResponse)
async def get_chart(
    chart_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chart by ID"""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found"
        )
    
    return chart

@router.put("/{chart_id}", response_model=ChartResponse)
async def update_chart(
    chart_id: str,
    chart_data: ChartUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update chart"""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found"
        )
    
    if chart_data.config:
        chart.config = chart_data.config.dict()
    
    db.commit()
    db.refresh(chart)
    return chart

@router.delete("/{chart_id}")
async def delete_chart(
    chart_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete chart"""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found"
        )
    
    db.delete(chart)
    db.commit()
    return {"success": True}

@router.get("", response_model=List[ChartResponse])
async def list_charts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's charts"""
    charts = db.query(Chart).filter(
        Chart.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return charts 