from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# Import base classes
try:
    from app.models import BaseDBModel, PyObjectId
except ImportError:
    from . import BaseDBModel, PyObjectId


class BlogStatus(str, Enum):
    """Blog post status enum"""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class BlogCategory(str, Enum):
    """Blog post category enum"""
    TUTORIAL = "tutorial"
    CASE_STUDY = "case_study"
    OPINION = "opinion"
    NEWS = "news"
    TECHNICAL = "technical"
    CAREER = "career"
    OTHER = "other"


class BlogPost(BaseDBModel):
    """
    Blog post model with markdown support
    Multi-tenant: Each post belongs to one portfolio
    """
    
    # Multi-tenant key
    portfolio_id: PyObjectId = Field(..., description="Portfolio this blog post belongs to")
    
    # Basic Information
    title: str = Field(..., min_length=5, max_length=200, description="Blog post title")
    slug: str = Field(..., min_length=5, max_length=200, description="URL-friendly slug")
    excerpt: str = Field(..., max_length=500, description="Short excerpt/summary")
    content: str = Field(..., description="Full blog content (markdown)")
    
    # Classification
    category: BlogCategory = Field(default=BlogCategory.OTHER, description="Post category")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    
    # Media
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    images: List[str] = Field(default_factory=list, description="Images used in post")
    
    # Metadata
    author_name: str = Field(..., description="Author display name")
    reading_time: Optional[int] = Field(None, description="Estimated reading time in minutes")
    word_count: Optional[int] = Field(None, description="Word count")
    
    # Publishing
    status: BlogStatus = Field(default=BlogStatus.DRAFT, description="Post status")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publication time")
    
    # Visibility
    is_featured: bool = Field(default=False, description="Feature on blog homepage")
    is_pinned: bool = Field(default=False, description="Pin to top of list")
    
    # Engagement Metrics
    view_count: int = Field(default=0, description="Number of views")
    like_count: int = Field(default=0, description="Number of likes")
    comment_count: int = Field(default=0, description="Number of comments")
    
    # SEO
    meta_title: Optional[str] = Field(None, max_length=60, description="SEO meta title")
    meta_description: Optional[str] = Field(None, max_length=160, description="SEO meta description")
    meta_keywords: List[str] = Field(default_factory=list, description="SEO keywords")
    canonical_url: Optional[str] = Field(None, description="Canonical URL for SEO")
    
    # Social Media
    og_title: Optional[str] = Field(None, description="Open Graph title")
    og_description: Optional[str] = Field(None, description="Open Graph description")
    og_image: Optional[str] = Field(None, description="Open Graph image URL")
    twitter_card: Optional[str] = Field(default="summary_large_image", description="Twitter card type")
    
    # Series (for multi-part posts)
    series_name: Optional[str] = Field(None, description="Series name if part of series")
    series_order: Optional[int] = Field(None, description="Order in series")
    
    # Related Content
    related_project_ids: List[PyObjectId] = Field(default_factory=list, description="Related project IDs")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "portfolio_id": "507f1f77bcf86cd799439011",
                "title": "Building a Real-Time Chat App with WebSockets",
                "slug": "building-realtime-chat-websockets",
                "excerpt": "Learn how to build a scalable real-time chat application using WebSockets and Redis.",
                "content": "# Introduction\n\nIn this tutorial, we'll build...",
                "category": "tutorial",
                "tags": ["WebSockets", "Redis", "FastAPI", "React"],
                "author_name": "John Doe",
                "reading_time": 12,
                "status": "published",
                "is_featured": True
            }
        }
    }


class BlogPostCreate(BaseModel):
    """Schema for creating a new blog post"""
    portfolio_id: PyObjectId
    title: str = Field(..., min_length=5, max_length=200)
    slug: str = Field(..., min_length=5, max_length=200)
    excerpt: str = Field(..., max_length=500)
    content: str
    category: BlogCategory = BlogCategory.OTHER
    tags: List[str] = Field(default_factory=list)
    cover_image: Optional[str] = None
    author_name: str
    status: BlogStatus = BlogStatus.DRAFT
    scheduled_at: Optional[datetime] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: List[str] = Field(default_factory=list)


class BlogPostUpdate(BaseModel):
    """Schema for updating a blog post"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    slug: Optional[str] = Field(None, min_length=5, max_length=200)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    category: Optional[BlogCategory] = None
    tags: Optional[List[str]] = None
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    reading_time: Optional[int] = None
    status: Optional[BlogStatus] = None
    published_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    is_featured: Optional[bool] = None
    is_pinned: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[List[str]] = None
    canonical_url: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    series_name: Optional[str] = None
    series_order: Optional[int] = None
    related_project_ids: Optional[List[PyObjectId]] = None


class BlogPostResponse(BaseDBModel):
    """Public blog post data (returned by API)"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    portfolio_id: PyObjectId
    title: str
    slug: str
    excerpt: str
    content: str
    category: str
    tags: List[str]
    cover_image: Optional[str]
    author_name: str
    reading_time: Optional[int]
    word_count: Optional[int]
    status: str
    published_at: Optional[datetime]
    is_featured: bool
    is_pinned: bool
    view_count: int
    like_count: int
    comment_count: int
    meta_title: Optional[str]
    meta_description: Optional[str]
    series_name: Optional[str]
    series_order: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "populate_by_name": True
    }


class BlogPostListResponse(BaseModel):
    """Paginated blog post list response"""
    posts: List[BlogPostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BlogPostFilter(BaseModel):
    """Schema for filtering blog posts"""
    portfolio_id: PyObjectId
    category: Optional[BlogCategory] = None
    tags: Optional[List[str]] = None  # Match any
    status: Optional[BlogStatus] = None
    is_featured: Optional[bool] = None
    search_query: Optional[str] = None  # Search in title, excerpt, content
    series_name: Optional[str] = None
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None


__all__ = [
    "BlogPost",
    "BlogPostCreate",
    "BlogPostUpdate", 
    "BlogPostResponse",
    "BlogPostListResponse",
    "BlogPostFilter",
    "BlogStatus",
    "BlogCategory"
]