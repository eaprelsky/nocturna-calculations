"""
Calculations router for the Nocturna Calculations API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
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

# Chart-based calculation endpoints
@router.post("/charts/{chart_id}/positions", response_model=SimplePlanetaryPositionsResponse)
async def calculate_chart_planetary_positions_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate planetary positions for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        # Create core chart instance from stored data
        core_chart = CoreChart(
            date=chart.date.strftime("%Y-%m-%d"),
            time=chart.date.strftime("%H:%M:%S"),
            latitude=chart.latitude,
            longitude=chart.longitude,
            timezone=chart.timezone
        )
        
        # Get planets from request or use default
        planets = request.get("planets", ["SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"])
        
        # Calculate planetary positions
        positions_data = core_chart.calculate_planetary_positions(planets)
        
        # Calculate houses for planet house assignments
        houses_data = core_chart.calculate_houses()
        
        # Convert to the expected format with house assignments
        planetary_positions = []
        for planet_name, position in positions_data.items():
            # Calculate which house this planet is in
            planet_house = calculate_planet_house(position["longitude"], houses_data["cusps"])
            
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
                "house": planet_house,
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

@router.post("/charts/{chart_id}/aspects", response_model=SimpleAspectsResponse)
async def calculate_chart_aspects_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate aspects for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        # Create core chart instance from stored data
        core_chart = CoreChart(
            date=chart.date.strftime("%Y-%m-%d"),
            time=chart.date.strftime("%H:%M:%S"),
            latitude=chart.latitude,
            longitude=chart.longitude,
            timezone=chart.timezone
        )
        
        # Get aspects from request or use chart config
        aspects = request.get("aspects", chart.config.get("aspects", ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"]))
        
        # Calculate aspects
        aspects_data = core_chart.calculate_aspects(aspects)
        
        # Convert to the expected format
        aspect_list = []
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

@router.post("/charts/{chart_id}/houses", response_model=SimpleHousesResponse)
async def calculate_chart_houses_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate houses for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        # Create core chart instance from stored data
        core_chart = CoreChart(
            date=chart.date.strftime("%Y-%m-%d"),
            time=chart.date.strftime("%H:%M:%S"),
            latitude=chart.latitude,
            longitude=chart.longitude,
            timezone=chart.timezone
        )
        
        # Get house system from request or use chart config
        house_system = request.get("house_system", chart.config.get("house_system", "PLACIDUS"))
        
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

@router.post("/charts/{chart_id}/fixed-stars", response_model=FixedStarsResponse)
async def calculate_chart_fixed_stars_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate fixed stars for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "fixed_stars",
        request
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        date=chart.date.strftime("%Y-%m-%d"),
        time=chart.date.strftime("%H:%M:%S"),
        latitude=chart.latitude,
        longitude=chart.longitude,
        timezone=chart.timezone
    )
    
    result = core_chart.calculate_fixed_stars(**request)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/charts/{chart_id}/arabic-parts", response_model=ArabicPartsResponse)
async def calculate_chart_arabic_parts_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate Arabic parts for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "arabic_parts",
        request
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        date=chart.date.strftime("%Y-%m-%d"),
        time=chart.date.strftime("%H:%M:%S"),
        latitude=chart.latitude,
        longitude=chart.longitude,
        timezone=chart.timezone
    )
    
    result = core_chart.calculate_arabic_parts(**request)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/charts/{chart_id}/dignities", response_model=DignitiesResponse)
async def calculate_chart_dignities_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate planetary dignities for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "dignities",
        request
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        date=chart.date.strftime("%Y-%m-%d"),
        time=chart.date.strftime("%H:%M:%S"),
        latitude=chart.latitude,
        longitude=chart.longitude,
        timezone=chart.timezone
    )
    
    result = core_chart.calculate_dignities(**request)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/charts/{chart_id}/antiscia", response_model=AntisciaResponse)
async def calculate_chart_antiscia_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate antiscia points for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "antiscia",
        request
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        date=chart.date.strftime("%Y-%m-%d"),
        time=chart.date.strftime("%H:%M:%S"),
        latitude=chart.latitude,
        longitude=chart.longitude,
        timezone=chart.timezone
    )
    
    result = core_chart.calculate_antiscia(**request)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/charts/{chart_id}/declinations", response_model=DeclinationsResponse)
async def calculate_chart_declinations_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate declinations for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "declinations",
        request
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        date=chart.date.strftime("%Y-%m-%d"),
        time=chart.date.strftime("%H:%M:%S"),
        latitude=chart.latitude,
        longitude=chart.longitude,
        timezone=chart.timezone
    )
    
    result = core_chart.calculate_declinations(**request)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/charts/{chart_id}/harmonics", response_model=HarmonicsResponse)
async def calculate_chart_harmonics_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate harmonic charts for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "harmonics",
        request
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        date=chart.date.strftime("%Y-%m-%d"),
        time=chart.date.strftime("%H:%M:%S"),
        latitude=chart.latitude,
        longitude=chart.longitude,
        timezone=chart.timezone
    )
    
    result = core_chart.calculate_harmonics(**request)
    
    cache.set(cache_key, result)
    
    return result

@router.post("/charts/{chart_id}/rectification", response_model=RectificationResponse)
async def calculate_chart_rectification_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate chart rectification for a stored chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    cache_key = get_cache_key(
        str(chart.id),
        "rectification",
        request
    )
    
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    core_chart = CoreChart(
        date=chart.date.strftime("%Y-%m-%d"),
        time=chart.date.strftime("%H:%M:%S"),
        latitude=chart.latitude,
        longitude=chart.longitude,
        timezone=chart.timezone
    )
    
    result = core_chart.calculate_rectification(**request)
    
    cache.set(cache_key, result)
    
    return result

# Advanced calculation endpoints
@router.post("/charts/{chart_id}/synastry")
async def calculate_chart_synastry_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate synastry between two charts."""
    chart1 = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart1:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    target_chart_id = request.get("target_chart_id")
    if not target_chart_id:
        raise HTTPException(status_code=400, detail="target_chart_id is required")
    
    chart2 = db.query(Chart).filter(
        Chart.id == target_chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart2:
        raise HTTPException(status_code=404, detail="Target chart not found")
    
    try:
        # Create core chart instances
        core_chart1 = CoreChart(
            date=chart1.date.strftime("%Y-%m-%d"),
            time=chart1.date.strftime("%H:%M:%S"),
            latitude=chart1.latitude,
            longitude=chart1.longitude,
            timezone=chart1.timezone
        )
        
        core_chart2 = CoreChart(
            date=chart2.date.strftime("%Y-%m-%d"),
            time=chart2.date.strftime("%H:%M:%S"),
            latitude=chart2.latitude,
            longitude=chart2.longitude,
            timezone=chart2.timezone
        )
        
        # Calculate synastry aspects
        result = core_chart1.calculate_synastry(core_chart2, **request)
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating synastry: {str(e)}"
        )

@router.post("/charts/{chart_id}/progressions")
async def calculate_chart_progressions_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate progressions for a chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        core_chart = CoreChart(
            date=chart.date.strftime("%Y-%m-%d"),
            time=chart.date.strftime("%H:%M:%S"),
            latitude=chart.latitude,
            longitude=chart.longitude,
            timezone=chart.timezone
        )
        
        result = core_chart.calculate_progressions(**request)
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating progressions: {str(e)}"
        )

@router.post("/charts/{chart_id}/directions")
async def calculate_chart_directions_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate directions for a chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        core_chart = CoreChart(
            date=chart.date.strftime("%Y-%m-%d"),
            time=chart.date.strftime("%H:%M:%S"),
            latitude=chart.latitude,
            longitude=chart.longitude,
            timezone=chart.timezone
        )
        
        result = core_chart.calculate_directions(**request)
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating directions: {str(e)}"
        )

@router.post("/charts/{chart_id}/returns")
async def calculate_chart_returns_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate returns for a chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        core_chart = CoreChart(
            date=chart.date.strftime("%Y-%m-%d"),
            time=chart.date.strftime("%H:%M:%S"),
            latitude=chart.latitude,
            longitude=chart.longitude,
            timezone=chart.timezone
        )
        
        result = core_chart.calculate_returns(**request)
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating returns: {str(e)}"
        )

@router.post("/charts/{chart_id}/eclipses")
async def calculate_chart_eclipses_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate eclipses and their impact on a chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        core_chart = CoreChart(
            date=chart.date.strftime("%Y-%m-%d"),
            time=chart.date.strftime("%H:%M:%S"),
            latitude=chart.latitude,
            longitude=chart.longitude,
            timezone=chart.timezone
        )
        
        result = core_chart.calculate_eclipses(**request)
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating eclipses: {str(e)}"
        )

@router.post("/charts/{chart_id}/ingresses")
async def calculate_chart_ingresses_endpoint(
    chart_id: str,
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate ingresses and their impact on a chart."""
    chart = db.query(Chart).filter(
        Chart.id == chart_id,
        Chart.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        core_chart = CoreChart(
            date=chart.date.strftime("%Y-%m-%d"),
            time=chart.date.strftime("%H:%M:%S"),
            latitude=chart.latitude,
            longitude=chart.longitude,
            timezone=chart.timezone
        )
        
        result = core_chart.calculate_ingresses(**request)
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating ingresses: {str(e)}"
        )

# Helper function to calculate which house a planet is in
def calculate_planet_house(planet_longitude: float, house_cusps: list) -> int:
    """Calculate which house a planet is in based on its longitude and house cusps."""
    # Normalize longitude to 0-360 range
    planet_longitude = planet_longitude % 360
    
    for i in range(12):
        current_cusp = house_cusps[i] % 360
        next_cusp = house_cusps[(i + 1) % 12] % 360
        
        # Handle the case where house spans 0 degrees
        if current_cusp > next_cusp:
            if planet_longitude >= current_cusp or planet_longitude < next_cusp:
                return i + 1
        else:
            if current_cusp <= planet_longitude < next_cusp:
                return i + 1
    
    # Default to house 1 if no match (shouldn't happen)
    return 1 