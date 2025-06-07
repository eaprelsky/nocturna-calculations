"""
Client library exceptions
"""


class NocturnaClientError(Exception):
    """Base exception for Nocturna client errors"""
    pass


class TokenExpiredError(NocturnaClientError):
    """Raised when service token has expired and needs renewal"""
    pass


class AuthenticationError(NocturnaClientError):
    """Raised when authentication fails"""
    pass


class APIError(NocturnaClientError):
    """Raised when API returns an error response"""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded"""
    pass


class ValidationError(APIError):
    """Raised when API request validation fails"""
    pass 