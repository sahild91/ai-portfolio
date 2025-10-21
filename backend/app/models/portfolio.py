"""
Portfolio Model
Portfolio settings and metadata
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId

# Import base classes
try:
    from app.models import BaseDBModel, PyObjectId
except ImportError:
    from . import BaseDBModel, PyObjectId


class SocialLinks(BaseModel):
    """Social media links"""
    github: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None


class PortfolioSettings(BaseModel):
    """Portfolio configuration settings"""
    theme: str = Field(default="default", description="Theme name")
    primary_color: str = Field(default="#3B82F6", description="Primary color hex")
    
    # AI Chat Settings
    chat_enabled: bool = Field(default=True, description="Enable AI chat")
    chat_greeting: str = Field(
        default="Hi! I'm an AI assistant. Ask me about this portfolio!",
        description="Chat widget greeting"
    )
    
    # Analytics
    analytics_enabled: bool = Field(default=False, description="Enable analytics")
    google_analytics_id: Optional[str] = None
    
    # SEO
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    og_image: Optional[str] = None


class Portfolio(BaseDBModel):
    """
    Portfolio model
    Multi-tenant: Each portfolio belongs to one user/owner
    """
    
    # Owner Information
    owner_id: PyObjectId = Field(..., description="User who owns this portfolio")
    
    # Domain & URL
    subdomain: str = Field(..., min_length=3, max_length=50, description="Subdomain (unique)")
    custom_domain: Optional[str] = Field(None, description="Custom domain if configured")
    
    # Profile Information
    display_name: str = Field(..., description="Display name on portfolio")
    tagline: Optional[str] = Field(None, max_length=200, description="Short tagline")
    bio: Optional[str] = Field(None, description="Detailed bio (markdown supported)")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    resume_url: Optional[str] = Field(None, description="Resume/CV URL")
    
    # Skills & Expertise
    skills: List[str] = Field(default_factory=list, description="List of skills")
    
    # Social Links
    social_links: Optional[SocialLinks] = None
    
    # Settings
    settings: PortfolioSettings = Field(default_factory=PortfolioSettings)
    
    # Status
    is_published: bool = Field(default=False, description="Portfolio published status")
    
    # Usage Stats (for cost tracking)
    api_calls_today: int = Field(default=0, description="OpenAI API calls today")
    api_calls_month: int = Field(default=0, description="OpenAI API calls this month")
    last_reset_date: Optional[str] = Field(None, description="Last daily reset date")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "owner_id": "507f1f77bcf86cd799439011",
                "subdomain": "johndoe",
                "display_name": "John Doe",
                "tagline": "Full-Stack Developer",
                "bio": "Passionate developer with 5 years of experience...",
                "skills": ["Python", "React", "FastAPI"],
                "is_published": True
            }
        }
    }


class PortfolioCreate(BaseModel):
    """Schema for creating a new portfolio"""
    owner_id: PyObjectId
    subdomain: str = Field(..., min_length=3, max_length=50)
    display_name: str
    tagline: Optional[str] = None
    bio: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class PortfolioUpdate(BaseModel):
    """Schema for updating portfolio"""
    display_name: Optional[str] = None
    tagline: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    resume_url: Optional[str] = None
    skills: Optional[List[str]] = None
    social_links: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None


class PortfolioResponse(BaseDBModel):
    """Public portfolio data"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    subdomain: str
    custom_domain: Optional[str] = None
    display_name: str
    tagline: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    resume_url: Optional[str] = None
    skills: List[str]
    social_links: Optional[Dict[str, Any]] = None
    settings: Dict[str, Any]
    is_published: bool
    created_at: datetime
    
    model_config = {
        "populate_by_name": True
    }


__all__ = [
    "Portfolio",
    "PortfolioCreate",
    "PortfolioUpdate",
    "PortfolioResponse",
    "SocialLinks",
    "PortfolioSettings"
]