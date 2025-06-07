"""
Nocturna Calculations Client Library

This package provides a Python client for the Nocturna Calculations API with automatic
token refresh capabilities for service tokens.

Example usage:
    from nocturna_calculations.client import NocturnaClient
    
    client = NocturnaClient(
        service_token="your_service_token_here",
        api_url="http://localhost:8000",
        auto_refresh=True
    )
    
    # Client automatically handles token refresh
    result = client.calculate_planetary_positions(
        date="2024-01-01",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        timezone="Europe/Moscow"
    )
"""

from .client import NocturnaClient, TokenManager
from .exceptions import (
    NocturnaClientError,
    TokenExpiredError,
    AuthenticationError,
    APIError
)

__all__ = [
    'NocturnaClient',
    'TokenManager',
    'NocturnaClientError',
    'TokenExpiredError',
    'AuthenticationError',
    'APIError'
] 