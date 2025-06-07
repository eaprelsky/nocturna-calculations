"""
Authentication router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import uuid

from nocturna_calculations.api.database import get_db
from nocturna_calculations.api.models import User, Token
from nocturna_calculations.api.config import settings
from nocturna_calculations.api.exceptions import RegistrationDisabledException

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_superuser: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

class ServiceTokenResponse(BaseModel):
    service_token: str
    expires_at: datetime
    expires_in_days: int
    scope: Optional[str]
    token_id: str

class ServiceTokenCreateRequest(BaseModel):
    days: Optional[int] = 30
    scope: Optional[str] = "calculations"
    eternal: bool = False

class RegistrationSettingsResponse(BaseModel):
    allow_user_registration: bool
    registration_requires_approval: bool
    max_users_limit: Optional[int]

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time. If None, defaults to 15 minutes.
                      Pass timedelta(0) or use eternal=True parameter to create eternal tokens.
    """
    to_encode = data.copy()
    
    # Check if this is an eternal token request (no expiration)
    if expires_delta is None:
        # Default to 15 minutes for regular tokens
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
    elif expires_delta.total_seconds() == 0:
        # Eternal token - no expiration claim
        pass
    else:
        # Custom expiration time
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str, db: Session) -> str:
    """Create and store refresh token"""
    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_token = Token(
        user_id=user_id,
        token=token,
        token_type="refresh",
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return token

def create_service_token(user_id: str, db: Session, days: int = 30, scope: str = "calculations", eternal: bool = False) -> tuple[str, str]:
    """Create and store service token
    
    Returns:
        tuple: (jwt_token, token_id)
    """
    token_id = str(uuid.uuid4())
    
    if eternal:
        expires_at = datetime.utcnow() + timedelta(days=36500)  # 100 years
        expires_delta = timedelta(0)  # No expiration in JWT
    else:
        expires_at = datetime.utcnow() + timedelta(days=days)
        expires_delta = timedelta(days=days)
    
    # Create JWT token
    jwt_token = create_access_token(
        data={
            "sub": user_id,
            "type": "service",
            "scope": scope,
            "token_id": token_id
        },
        expires_delta=expires_delta
    )
    
    # Store in database
    db_token = Token(
        id=token_id,
        user_id=user_id,
        token=jwt_token,
        token_type="service",
        scope=scope,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return jwt_token, token_id

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_service_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Token:
    """Get current service token and verify it's valid"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate service token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type")
        token_id = payload.get("token_id")
        
        if token_type != "service" or not token_id:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Verify token exists in database and is not expired
    db_token = db.query(Token).filter(
        Token.id == token_id,
        Token.token_type == "service",
        Token.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        raise credentials_exception
    
    # Update last used timestamp
    db_token.last_used_at = datetime.utcnow()
    db.commit()
    
    return db_token

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user and verify admin privileges"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# Endpoints
@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if registration is allowed
    if not settings.ALLOW_USER_REGISTRATION:
        raise RegistrationDisabledException()
    
    # Check if user exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return tokens"""
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(user.id, db)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    # Find token
    token = db.query(Token).filter(
        Token.token == refresh_token,
        Token.expires_at > datetime.utcnow()
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": token.user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/logout")
async def logout(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Logout user by invalidating refresh token"""
    token = db.query(Token).filter(Token.token == refresh_token).first()
    if token:
        db.delete(token)
        db.commit()
    
    return {"success": True}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/admin/verify")
async def verify_admin_access(admin_user: User = Depends(get_current_admin_user)):
    """Verify admin access - returns 200 if user is admin, 403 if not"""
    return {
        "is_admin": True,
        "user_id": admin_user.id,
        "email": admin_user.email,
        "username": admin_user.username
    }

@router.get("/admin/registration-settings", response_model=RegistrationSettingsResponse)
async def get_registration_settings(admin_user: User = Depends(get_current_admin_user)):
    """Get current registration settings"""
    return RegistrationSettingsResponse(
        allow_user_registration=settings.ALLOW_USER_REGISTRATION,
        registration_requires_approval=settings.REGISTRATION_REQUIRES_APPROVAL,
        max_users_limit=settings.MAX_USERS_LIMIT
    )

# Service Token Endpoints
@router.post("/admin/service-tokens", response_model=ServiceTokenResponse)
async def create_service_token_endpoint(
    request: ServiceTokenCreateRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new service token (admin only)"""
    jwt_token, token_id = create_service_token(
        user_id=admin_user.id,
        db=db,
        days=request.days,
        scope=request.scope,
        eternal=request.eternal
    )
    
    # Calculate expiration info
    if request.eternal:
        expires_at = datetime.utcnow() + timedelta(days=36500)
        expires_in_days = 36500
    else:
        expires_at = datetime.utcnow() + timedelta(days=request.days)
        expires_in_days = request.days
    
    return ServiceTokenResponse(
        service_token=jwt_token,
        expires_at=expires_at,
        expires_in_days=expires_in_days,
        scope=request.scope,
        token_id=token_id
    )

@router.get("/admin/service-tokens")
async def list_service_tokens(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List all service tokens (admin only)"""
    tokens = db.query(Token).filter(
        Token.token_type == "service"
    ).order_by(Token.created_at.desc()).all()
    
    return [
        {
            "id": token.id,
            "user_id": token.user_id,
            "scope": token.scope,
            "created_at": token.created_at,
            "expires_at": token.expires_at,
            "last_used_at": token.last_used_at,
            "is_expired": token.expires_at < datetime.utcnow(),
            "days_until_expiry": (token.expires_at - datetime.utcnow()).days if token.expires_at > datetime.utcnow() else 0
        }
        for token in tokens
    ]

@router.delete("/admin/service-tokens/{token_id}")
async def revoke_service_token(
    token_id: str,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke a service token (admin only)"""
    token = db.query(Token).filter(
        Token.id == token_id,
        Token.token_type == "service"
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service token not found"
        )
    
    db.delete(token)
    db.commit()
    
    return {"success": True, "message": f"Service token {token_id} revoked"}

@router.post("/service-token/refresh", response_model=TokenResponse)
async def refresh_service_token(
    service_token: Token = Depends(get_current_service_token),
    db: Session = Depends(get_db)
):
    """Exchange service token for fresh access token"""
    # Create new short-lived access token
    access_token = create_access_token(
        data={
            "sub": service_token.user_id,
            "type": "access",
            "scope": service_token.scope
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": service_token.token,  # Service token acts as refresh token
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    } 