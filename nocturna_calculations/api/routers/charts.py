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
from nocturna_calculations.core.chart import Chart as CoreChart

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

class NatalChartCreate(BaseModel):
    date: str
    time: str
    latitude: float
    longitude: float
    timezone: str = "UTC"

class NatalChartResponse(BaseModel):
    chart_id: str
    planets: dict
    houses: dict
    aspects: dict

# Endpoints
@router.post("/natal", response_model=NatalChartResponse)
async def create_natal_chart(
    chart_data: NatalChartCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new natal chart"""
    try:
        # Validate data before creating chart
        # Check date format
        try:
            datetime.strptime(chart_data.date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid date format. Expected YYYY-MM-DD"
            )
        
        # Check time format
        try:
            datetime.strptime(chart_data.time, "%H:%M:%S")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid time format. Expected HH:MM:SS"
            )
        
        # Validate coordinates
        if not -90 <= chart_data.latitude <= 90:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Latitude must be between -90 and 90 degrees"
            )
        
        if not -180 <= chart_data.longitude <= 180:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Longitude must be between -180 and 180 degrees"
            )
        
        # Create core chart instance
        core_chart = CoreChart(
            date=chart_data.date,
            time=chart_data.time,
            latitude=chart_data.latitude,
            longitude=chart_data.longitude,
            timezone=chart_data.timezone
        )
        
        # Calculate chart data
        planets = core_chart.calculate_planetary_positions()
        houses = core_chart.calculate_houses()
        aspects = core_chart.calculate_aspects()
        
        # Create database chart record
        chart = Chart(
            user_id=current_user.id,
            date=datetime.strptime(f"{chart_data.date} {chart_data.time}", "%Y-%m-%d %H:%M:%S"),
            latitude=chart_data.latitude,
            longitude=chart_data.longitude,
            timezone=chart_data.timezone,
            config={
                "house_system": "PLACIDUS",
                "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
                "orbs": {
                    "conjunction": 10.0,
                    "opposition": 10.0,
                    "trine": 8.0,
                    "square": 8.0,
                    "sextile": 6.0
                }
            }
        )
        db.add(chart)
        db.commit()
        db.refresh(chart)
        
        return {
            "chart_id": chart.id,
            "planets": planets,
            "houses": houses,
            "aspects": aspects
        }
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        # Catch-all for other errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating chart: {str(e)}"
        )

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

@router.delete("/{chart_id}", status_code=204)
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
    # Return nothing for 204 status

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