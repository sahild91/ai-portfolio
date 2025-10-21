"""
User Model
User authentication and profile data
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

# Import base classes
try:
    from app.models import BaseDBModel, PyObjectId
except ImportError:
    # Fallback if running from different context
    from . import BaseDBModel, PyObjectId


class User(BaseDBModel):
    """
    User model for authentication and profile
    Multi-tenant: Each user owns one portfolio
    """
    
    email: EmailStr = Field(..., description="User email (unique)")
    username: str = Field(..., min_length=3, max_length=50, description="Username (unique)")
    password_hash: str = Field(..., description="Bcrypt hashed password")
    
    # Profile Information
    full_name: Optional[str] = Field(None, description="Full name")
    
    # Portfolio Link (One-to-One)
    portfolio_id: Optional[PyObjectId] = Field(None, description="Linked portfolio ID")
    
    # Subscription & Status
    subscription_tier: str = Field(default="free", description="Subscription tier")
    is_active: bool = Field(default=True, description="Account active status")
    is_verified: bool = Field(default=False, description="Email verified")
    
    # Authentication
    last_login: Optional[str] = Field(None, description="Last login timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "subscription_tier": "free",
                "is_active": True,
                "is_verified": False
            }
        }
    }


class UserCreate(BaseDBModel):
    """Schema for creating a new user"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, description="Plain password (will be hashed)")
    full_name: Optional[str] = None


class UserLogin(BaseDBModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseDBModel):
    """Public user data (excludes sensitive fields)"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    portfolio_id: Optional[PyObjectId] = None
    subscription_tier: str
    is_active: bool
    created_at: str
    
    class Config:
        populate_by_name = True


__all__ = ["User", "UserCreate", "UserLogin", "UserResponse"]