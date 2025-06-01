"""
Calculations router for the Nocturna Calculations API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from datetime import datetime
import json
import hashlib

from ..database import get_db
from ..models import Chart, Calculation
from ..schemas import (
    CalculationRequest,
    DirectCalculationRequest,
    CalculationResponse,
    PlanetaryPositionsResponse,
    AspectsResponse,
    HousesResponse,
    FixedStarsResponse,
    ArabicPartsResponse,
    DignitiesResponse,
    AntisciaResponse,
    DeclinationsResponse,
    HarmonicsResponse,
    RectificationResponse,
    PrimaryDirectionsResponse,
    SecondaryProgressionsResponse,
    SimplePlanetaryPositionsResponse,
    SimpleAspectsResponse,
    SimpleHousesResponse
)
from .auth import get_current_user
from ..cache import cache
from ...core.chart import Chart as CoreChart

router = APIRouter()

def get_cache_key(chart_id: str, calculation_type: str, params: dict) -> str:
    """Generate cache key for calculation results."""
    sorted_params = json.dumps(params, sort_keys=True)
    param_hash = hashlib.md5(sorted_params.encode()).hexdigest()
    return f"calc:{chart_id}:{calculation_type}:{param_hash}"

@router.post("/planetary-positions", response_model=SimplePlanetaryPositionsResponse)
async def calculate_planetary_positions_endpoint(
    request: DirectCalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate planetary positions."""
    try:
        # Create core chart instance from direct data
        core_chart = CoreChart(
            date=request.date,
            time=request.time,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone
        )
        
        # Get planets from request or use default
        planets = request.planets or ["SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"]
        
        # Calculate planetary positions - this returns a flat dict with planet names as keys
        positions_data = core_chart.calculate_planetary_positions(planets)
        
        # Convert to the expected format
        planetary_positions = []
        for planet_name, position in positions_data.items():
            # Convert longitude to sign/degree/minute/second
            longitude = position["longitude"]
            sign_num = int(longitude // 30)
            signs = ["ARIES", "TAURUS", "GEMINI", "CANCER", "LEO", "VIRGO", 
                    "LIBRA", "SCORPIO", "SAGITTARIUS", "CAPRICORN", "AQUARIUS", "PISCES"]
            sign = signs[sign_num]
            
            degree_in_sign = longitude % 30
            degree = int(degree_in_sign)
            minute = int((degree_in_sign - degree) * 60)
            second = int(((degree_in_sign - degree) * 60 - minute) * 60)
            
            planetary_positions.append({
                "planet": planet_name,
                "longitude": longitude,
                "latitude": position["latitude"],
                "distance": position["distance"],
                "speed": position["speed"],
                "is_retrograde": position["is_retrograde"],
                "house": None,  # Will be calculated separately
                "sign": sign,
                "degree": degree,
                "minute": minute,
                "second": second
            })
        
        return SimplePlanetaryPositionsResponse(
            positions=planetary_positions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating planetary positions: {str(e)}"
        )

@router.post("/aspects", response_model=SimpleAspectsResponse)
async def calculate_aspects_endpoint(
    request: DirectCalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate aspects."""
    try:
        # Create core chart instance from direct data
        core_chart = CoreChart(
            date=request.date,
            time=request.time,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone
        )
        
        # Get aspects from request or use default
        aspects = request.aspects or ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"]
        
        # Calculate aspects - this returns {"aspects": aspects_list}
        aspects_data = core_chart.calculate_aspects(aspects)
        
        # Convert to the expected format
        aspect_list = []
        # aspects_data["aspects"] is the list of aspects
        for aspect in aspects_data["aspects"]:
            aspect_list.append({
                "planet1": aspect["planet1"],
                "planet2": aspect["planet2"],
                "aspect_type": aspect["aspect_type"],
                "orb": aspect["orb"],
                "applying": aspect["applying"],
                "exact_time": None  # Would need additional calculation
            })
        
        return SimpleAspectsResponse(
            aspects=aspect_list
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating aspects: {str(e)}"
        )

@router.post("/houses", response_model=SimpleHousesResponse)
async def calculate_houses_endpoint(
    request: DirectCalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate house cusps."""
    try:
        # Create core chart instance from direct data
        core_chart = CoreChart(
            date=request.date,
            time=request.time,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone
        )
        
        # Get house system from request or use default
        house_system = request.house_system or "PLACIDUS"
        
        # Calculate houses
        houses_data = core_chart.calculate_houses(house_system=house_system)
        
        # Convert to the expected format
        house_list = []
        for i, cusp_longitude in enumerate(houses_data["cusps"], 1):
            # Convert longitude to sign/degree/minute/second
            longitude = cusp_longitude
            sign_num = int(longitude // 30)
            signs = ["ARIES", "TAURUS", "GEMINI", "CANCER", "LEO", "VIRGO", 
                    "LIBRA", "SCORPIO", "SAGITTARIUS", "CAPRICORN", "AQUARIUS", "PISCES"]
            sign = signs[sign_num]
            
            degree_in_sign = longitude % 30
            degree = int(degree_in_sign)
            minute = int((degree_in_sign - degree) * 60)
            second = int(((degree_in_sign - degree) * 60 - minute) * 60)
            
            house_list.append({
                "number": i,
                "longitude": longitude,
                "latitude": 0.0,  # House cusps don't have latitude
                "sign": sign,
                "degree": degree,
                "minute": minute,
                "second": second
            })
        
        return SimpleHousesResponse(
            houses=house_list
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating houses: {str(e)}"
        )

@router.post("/fixed-stars", response_model=FixedStarsResponse)
async def calculate_fixed_stars_endpoint(
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate fixed star positions."""
    chart = db.query(Chart).filter(
        Chart.id == request.chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "fixed_stars",
        request.parameters
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        datetime=chart.datetime,
        latitude=chart.latitude,
        longitude=chart.longitude,
        altitude=chart.altitude,
        **chart.config
    )
    
    result = core_chart.calculate_fixed_stars(**request.parameters)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/arabic-parts", response_model=ArabicPartsResponse)
async def calculate_arabic_parts_endpoint(
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate Arabic parts."""
    chart = db.query(Chart).filter(
        Chart.id == request.chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "arabic_parts",
        request.parameters
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        datetime=chart.datetime,
        latitude=chart.latitude,
        longitude=chart.longitude,
        altitude=chart.altitude,
        **chart.config
    )
    
    result = core_chart.calculate_arabic_parts(**request.parameters)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/dignities", response_model=DignitiesResponse)
async def calculate_dignities_endpoint(
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate planetary dignities."""
    chart = db.query(Chart).filter(
        Chart.id == request.chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "dignities",
        request.parameters
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        datetime=chart.datetime,
        latitude=chart.latitude,
        longitude=chart.longitude,
        altitude=chart.altitude,
        **chart.config
    )
    
    result = core_chart.calculate_dignities(**request.parameters)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/antiscia", response_model=AntisciaResponse)
async def calculate_antiscia_endpoint(
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate antiscia points."""
    chart = db.query(Chart).filter(
        Chart.id == request.chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "antiscia",
        request.parameters
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        datetime=chart.datetime,
        latitude=chart.latitude,
        longitude=chart.longitude,
        altitude=chart.altitude,
        **chart.config
    )
    
    result = core_chart.calculate_antiscia(**request.parameters)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/declinations", response_model=DeclinationsResponse)
async def calculate_declinations_endpoint(
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate declinations."""
    chart = db.query(Chart).filter(
        Chart.id == request.chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "declinations",
        request.parameters
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        datetime=chart.datetime,
        latitude=chart.latitude,
        longitude=chart.longitude,
        altitude=chart.altitude,
        **chart.config
    )
    
    result = core_chart.calculate_declinations(**request.parameters)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/harmonics", response_model=HarmonicsResponse)
async def calculate_harmonics_endpoint(
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate harmonic charts."""
    chart = db.query(Chart).filter(
        Chart.id == request.chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "harmonics",
        request.parameters
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        datetime=chart.datetime,
        latitude=chart.latitude,
        longitude=chart.longitude,
        altitude=chart.altitude,
        **chart.config
    )
    
    result = core_chart.calculate_harmonics(**request.parameters)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/rectification", response_model=RectificationResponse)
async def calculate_rectification_endpoint(
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate chart rectification."""
    chart = db.query(Chart).filter(
        Chart.id == request.chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "rectification",
        request.parameters
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        datetime=chart.datetime,
        latitude=chart.latitude,
        longitude=chart.longitude,
        altitude=chart.altitude,
        **chart.config
    )
    
    result = core_chart.calculate_rectification(**request.parameters)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/primary-directions", response_model=PrimaryDirectionsResponse)
async def calculate_primary_directions_endpoint(
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate primary directions."""
    chart = db.query(Chart).filter(
        Chart.id == request.chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "primary_directions",
        request.parameters
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        datetime=chart.datetime,
        latitude=chart.latitude,
        longitude=chart.longitude,
        altitude=chart.altitude,
        **chart.config
    )
    
    result = core_chart.calculate_primary_directions(**request.parameters)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/secondary-progressions", response_model=SecondaryProgressionsResponse)
async def calculate_secondary_progressions_endpoint(
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate secondary progressions."""
    chart = db.query(Chart).filter(
        Chart.id == request.chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "secondary_progressions",
        request.parameters
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        datetime=chart.datetime,
        latitude=chart.latitude,
        longitude=chart.longitude,
        altitude=chart.altitude,
        **chart.config
    )
    
    result = core_chart.calculate_secondary_progressions(**request.parameters)
    
    cache.set(cache_key, result)
    
    return result

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time calculations."""
    await websocket.accept()
    
    try:
        while True:
            # Receive calculation request
            data = await websocket.receive_json()
            request = CalculationRequest(**data)
            
            # Generate cache key
            cache_key = get_cache_key(
                str(request.chart_id),
                request.calculation_type,
                request.parameters
            )
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                await websocket.send_json(cached_result.dict())
                continue
            
            # Calculate if not in cache
            chart = CoreChart(
                datetime=request.datetime,
                latitude=request.latitude,
                longitude=request.longitude,
                altitude=request.altitude,
                **request.parameters
            )
            
            # Perform calculation based on type
            if request.calculation_type == "planetary_positions":
                result = chart.calculate_planetary_positions(**request.parameters)
            elif request.calculation_type == "aspects":
                result = chart.calculate_aspects(**request.parameters)
            elif request.calculation_type == "houses":
                result = chart.calculate_houses(**request.parameters)
            elif request.calculation_type == "fixed_stars":
                result = chart.calculate_fixed_stars(**request.parameters)
            elif request.calculation_type == "arabic_parts":
                result = chart.calculate_arabic_parts(**request.parameters)
            elif request.calculation_type == "dignities":
                result = chart.calculate_dignities(**request.parameters)
            elif request.calculation_type == "antiscia":
                result = chart.calculate_antiscia(**request.parameters)
            elif request.calculation_type == "declinations":
                result = chart.calculate_declinations(**request.parameters)
            elif request.calculation_type == "harmonics":
                result = chart.calculate_harmonics(**request.parameters)
            elif request.calculation_type == "rectification":
                result = chart.calculate_rectification(**request.parameters)
            elif request.calculation_type == "primary_directions":
                result = chart.calculate_primary_directions(**request.parameters)
            elif request.calculation_type == "secondary_progressions":
                result = chart.calculate_secondary_progressions(**request.parameters)
            else:
                await websocket.send_json({
                    "error": f"Unknown calculation type: {request.calculation_type}"
                })
                continue
            
            # Cache the result
            cache.set(cache_key, result)
            
            # Send result
            await websocket.send_json(result.dict())
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close() 