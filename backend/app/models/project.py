from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

# Import base classes
try:
    from app.models import BaseDBModel, PyObjectId
except ImportError:
    from . import BaseDBModel, PyObjectId


class ProjectStatus(str, Enum):
    """Project status enum"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ProjectCategory(str, Enum):
    """Project category enum"""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API = "api"
    LIBRARY = "library"
    CLI_TOOL = "cli_tool"
    MACHINE_LEARNING = "machine_learning"
    DATA_SCIENCE = "data_science"
    GAME = "game"
    OTHER = "other"


class Project(BaseDBModel):
    """
    Project model for portfolio showcase
    Multi-tenant: Each project belongs to one portfolio
    """
    
    # Multi-tenant key
    portfolio_id: PyObjectId = Field(..., description="Portfolio this project belongs to")
    
    # Basic Information
    title: str = Field(..., min_length=3, max_length=200, description="Project title")
    slug: str = Field(..., min_length=3, max_length=200, description="URL-friendly slug")
    tagline: str = Field(..., max_length=300, description="Short description (1-2 sentences)")
    description: str = Field(..., description="Full project description (markdown supported)")
    
    # Project Details
    category: ProjectCategory = Field(default=ProjectCategory.OTHER, description="Project category")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies used")
    features: List[str] = Field(default_factory=list, description="Key features")
    
    # Media
    thumbnail: Optional[str] = Field(None, description="Thumbnail image URL")
    images: List[str] = Field(default_factory=list, description="Project screenshots/images")
    demo_video_url: Optional[HttpUrl] = Field(None, description="Demo video URL")
    
    # Links
    github_url: Optional[HttpUrl] = Field(None, description="GitHub repository URL")
    live_url: Optional[HttpUrl] = Field(None, description="Live demo URL")
    case_study_url: Optional[HttpUrl] = Field(None, description="Detailed case study URL")
    
    # Metadata
    start_date: Optional[str] = Field(None, description="Project start date (YYYY-MM)")
    end_date: Optional[str] = Field(None, description="Project end date (YYYY-MM) or 'Present'")
    duration: Optional[str] = Field(None, description="Project duration (e.g., '3 months')")
    
    # Status & Visibility
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT, description="Project status")
    is_featured: bool = Field(default=False, description="Feature on homepage")
    is_pinned: bool = Field(default=False, description="Pin to top of list")
    
    # Engagement Metrics (for analytics)
    view_count: int = Field(default=0, description="Number of views")
    like_count: int = Field(default=0, description="Number of likes")
    
    # SEO
    meta_description: Optional[str] = Field(None, max_length=160, description="SEO meta description")
    tags: List[str] = Field(default_factory=list, description="SEO tags")
    
    # Sort Order
    display_order: int = Field(default=0, description="Manual sort order (lower = higher priority)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "portfolio_id": "507f1f77bcf86cd799439011",
                "title": "AI-Powered Task Manager",
                "slug": "ai-task-manager",
                "tagline": "Smart task management with AI prioritization",
                "description": "A full-stack web application that uses machine learning...",
                "category": "web_app",
                "tech_stack": ["React", "FastAPI", "PostgreSQL", "TensorFlow"],
                "features": ["AI-powered prioritization", "Real-time collaboration", "Smart notifications"],
                "github_url": "https://github.com/username/project",
                "live_url": "https://demo.example.com",
                "status": "published",
                "is_featured": True
            }
        }
    }


class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    portfolio_id: PyObjectId
    title: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=200)
    tagline: str = Field(..., max_length=300)
    description: str
    category: ProjectCategory = ProjectCategory.OTHER
    tech_stack: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    thumbnail: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    github_url: Optional[HttpUrl] = None
    live_url: Optional[HttpUrl] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: ProjectStatus = ProjectStatus.DRAFT
    tags: List[str] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    slug: Optional[str] = Field(None, min_length=3, max_length=200)
    tagline: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    category: Optional[ProjectCategory] = None
    tech_stack: Optional[List[str]] = None
    features: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    images: Optional[List[str]] = None
    demo_video_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    live_url: Optional[HttpUrl] = None
    case_study_url: Optional[HttpUrl] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    status: Optional[ProjectStatus] = None
    is_featured: Optional[bool] = None
    is_pinned: Optional[bool] = None
    meta_description: Optional[str] = None
    tags: Optional[List[str]] = None
    display_order: Optional[int] = None


class ProjectResponse(BaseDBModel):
    """Public project data (returned by API)"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    portfolio_id: PyObjectId
    title: str
    slug: str
    tagline: str
    description: str
    category: str
    tech_stack: List[str]
    features: List[str]
    thumbnail: Optional[str]
    images: List[str]
    demo_video_url: Optional[str]
    github_url: Optional[str]
    live_url: Optional[str]
    case_study_url: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    duration: Optional[str]
    status: str
    is_featured: bool
    is_pinned: bool
    view_count: int
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "populate_by_name": True
    }


class ProjectListResponse(BaseModel):
    """Paginated project list response"""
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProjectFilter(BaseModel):
    """Schema for filtering projects"""
    portfolio_id: PyObjectId
    category: Optional[ProjectCategory] = None
    tech_stack: Optional[List[str]] = None  # Match any
    status: Optional[ProjectStatus] = None
    is_featured: Optional[bool] = None
    search_query: Optional[str] = None  # Search in title, tagline, description
    tags: Optional[List[str]] = None


__all__ = [
    "Project",
    "ProjectCreate", 
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
    "ProjectFilter",
    "ProjectStatus",
    "ProjectCategory"
]