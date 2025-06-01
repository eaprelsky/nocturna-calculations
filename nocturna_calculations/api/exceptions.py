"""
API Exception Classes

Custom exceptions for API error handling.
"""
from fastapi import HTTPException, status


class RegistrationDisabledException(HTTPException):
    """Exception raised when user registration is disabled"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User registration is currently disabled. Please contact system administrator."
        )


class RegistrationRequiresApprovalException(HTTPException):
    """Exception raised when registration requires approval (future enhancement)"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Registration submitted successfully. Account requires administrator approval."
        )


class UserLimitReachedException(HTTPException):
    """Exception raised when user limit is reached (future enhancement)"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Maximum number of users reached. Registration is temporarily disabled."
        ) 