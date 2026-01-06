"""
Nocturna Calculations API Client

Provides a Python client for the Nocturna Calculations API with automatic token refresh.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
import requests
from jose import jwt, JWTError
import logging

from .exceptions import (
    TokenExpiredError,
    AuthenticationError,
    APIError,
    RateLimitError,
    ValidationError
)

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages service token refresh and access token lifecycle"""
    
    def __init__(self, service_token: str, api_url: str, refresh_threshold: int = 300):
        """
        Initialize token manager
        
        Args:
            service_token: Long-lived service token
            api_url: Base API URL
            refresh_threshold: Seconds before expiry to refresh token (default: 5 minutes)
        """
        self.service_token = service_token
        self.api_url = api_url.rstrip('/')
        self.refresh_threshold = refresh_threshold
        
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self._lock = threading.Lock()
        
        # Validate service token on initialization
        self._validate_service_token()
    
    def _validate_service_token(self):
        """Validate the service token format and basic claims"""
        try:
            payload = jwt.decode(self.service_token, key="", options={"verify_signature": False, "verify_exp": False})
            
            if payload.get("type") != "service":
                raise AuthenticationError("Invalid token type - expected service token")
            
            # Check if token is expired (if it has expiration)
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                exp_date = datetime.fromtimestamp(exp_timestamp)
                if exp_date < datetime.utcnow():
                    raise TokenExpiredError(
                        f"Service token expired on {exp_date}. Please create a new service token."
                    )
                    
        except JWTError as e:
            raise AuthenticationError(f"Invalid service token format: {e}")
    
    def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        with self._lock:
            if self._needs_refresh():
                self._refresh_token()
            return self.access_token
    
    def _needs_refresh(self) -> bool:
        """Check if token needs to be refreshed"""
        if not self.access_token or not self.token_expires_at:
            return True
        
        time_until_expiry = (self.token_expires_at - datetime.utcnow()).total_seconds()
        return time_until_expiry < self.refresh_threshold
    
    def _refresh_token(self):
        """Refresh the access token using the service token"""
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/service-token/refresh",
                headers={
                    "Authorization": f"Bearer {self.service_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 401:
                error_detail = response.json().get('detail', '')
                if 'expired' in error_detail.lower():
                    raise TokenExpiredError(
                        "Service token has expired. Please create a new service token with: "
                        "make service-token-create"
                    )
                else:
                    raise AuthenticationError(f"Service token authentication failed: {error_detail}")
            
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data["access_token"]
            expires_in = data["expires_in"]
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            logger.info(f"Token refreshed successfully, expires at {self.token_expires_at}")
            
        except requests.exceptions.Timeout:
            raise APIError("Token refresh timeout - API server may be unavailable")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Token refresh failed: {e}")
    
    def force_refresh(self):
        """Force refresh the token regardless of expiration time"""
        with self._lock:
            self._refresh_token()


class NocturnaClient:
    """Main client for Nocturna Calculations API"""
    
    def __init__(
        self,
        service_token: str,
        api_url: str = "http://localhost:8000",
        auto_refresh: bool = True,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Nocturna API client
        
        Args:
            service_token: Long-lived service token
            api_url: Base API URL
            auto_refresh: Enable automatic token refresh
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        if auto_refresh:
            self.token_manager = TokenManager(service_token, api_url)
        else:
            self.service_token = service_token
            self.token_manager = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        if self.token_manager:
            token = self.token_manager.get_valid_token()
        else:
            token = self.service_token
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Nocturna-Python-Client/1.0"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries"""
        url = f"{self.api_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
                
                # Handle specific HTTP status codes
                if response.status_code == 401:
                    error_detail = response.json().get('detail', '')
                    if 'expired' in error_detail.lower() and self.token_manager:
                        # Try to refresh token and retry
                        if attempt < self.max_retries:
                            self.token_manager.force_refresh()
                            continue
                    raise AuthenticationError(f"Authentication failed: {error_detail}")
                
                elif response.status_code == 403:
                    raise AuthenticationError("Insufficient permissions")
                
                elif response.status_code == 429:
                    raise RateLimitError("API rate limit exceeded")
                
                elif response.status_code == 422:
                    error_data = response.json()
                    raise ValidationError(
                        f"Request validation failed: {error_data}",
                        status_code=422,
                        response_data=error_data
                    )
                
                elif not response.ok:
                    error_data = response.json() if response.content else {}
                    raise APIError(
                        f"API request failed: {response.status_code}",
                        status_code=response.status_code,
                        response_data=error_data
                    )
                
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Request timeout, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                raise APIError("Request timeout after retries")
            
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    continue
                raise APIError(f"Request failed after retries: {e}")
    
    # API Methods
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        return self._make_request("GET", "/health")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        return self._make_request("GET", "/api/auth/me")
    
    def calculate_planetary_positions(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        planets: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Calculate planetary positions
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            timezone: Timezone (e.g., "Europe/Moscow")
            planets: List of planets to calculate (optional)
        """
        data = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone
        }
        
        if planets:
            data["planets"] = planets
        
        return self._make_request("POST", "/api/calculations/planetary-positions", data=data)
    
    def calculate_houses(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        house_system: str = "placidus"
    ) -> Dict[str, Any]:
        """
        Calculate astrological houses
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            timezone: Timezone (e.g., "Europe/Moscow")
            house_system: House system to use (default: "placidus")
        """
        data = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "house_system": house_system
        }
        
        return self._make_request("POST", "/api/calculations/houses", data=data)
    
    def calculate_aspects(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        orb_tolerance: float = 8.0
    ) -> Dict[str, Any]:
        """
        Calculate planetary aspects
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            timezone: timezone (e.g., "Europe/Moscow")
            orb_tolerance: Orb tolerance in degrees (default: 8.0)
        """
        data = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "orb_tolerance": orb_tolerance
        }
        
        return self._make_request("POST", "/api/calculations/aspects", data=data)
    
    def create_natal_chart(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a complete natal chart
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM:SS format
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            timezone: Timezone (e.g., "Europe/Moscow")
            name: Optional name for the chart
        """
        data = {
            "date": date,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone
        }
        
        if name:
            data["name"] = name
        
        return self._make_request("POST", "/api/charts/natal", data=data) 