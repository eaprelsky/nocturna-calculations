"""
Database models for the API
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    charts = relationship("Chart", back_populates="user")
    tokens = relationship("Token", back_populates="user")

class Chart(Base):
    """Chart model"""
    __tablename__ = "charts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timezone = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="charts")
    calculations = relationship("Calculation", back_populates="chart")

class Calculation(Base):
    """Calculation model for caching results"""
    __tablename__ = "calculations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    chart_id = Column(String, ForeignKey("charts.id"), nullable=False)
    calculation_type = Column(String, nullable=False)  # e.g., "positions", "aspects"
    parameters = Column(JSON, nullable=False)  # Input parameters
    result = Column(JSON, nullable=False)  # Calculation result
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    chart = relationship("Chart", back_populates="calculations")

class Token(Base):
    """Token model for refresh tokens and service tokens"""
    __tablename__ = "tokens"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    token_type = Column(String, nullable=False, default="refresh")  # "refresh" or "service"
    scope = Column(String, nullable=True)  # e.g., "calculations,admin" for service tokens
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)  # Track usage for service tokens
    
    # Relationships
    user = relationship("User", back_populates="tokens") 