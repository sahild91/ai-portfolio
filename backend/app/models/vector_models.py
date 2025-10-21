from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# Import base classes
try:
    from app.models import BaseDBModel, PyObjectId
except ImportError:
    from . import BaseDBModel, PyObjectId


class ContentType(str, Enum):
    """Type of content being indexed"""
    PROJECT = "project"
    BLOG = "blog"
    PORTFOLIO = "portfolio"
    SKILL = "skill"
    EXPERIENCE = "experience"


class VectorPoint(BaseModel):
    """
    Vector point for Qdrant
    Represents a single piece of indexed content
    """
    
    # Point Identification
    point_id: str = Field(..., description="Unique point ID (content_id)")
    
    # Vector Data
    vector: List[float] = Field(..., description="Embedding vector (1536 dimensions)")
    
    # Payload (metadata stored with vector)
    payload: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "point_id": "project_507f1f77bcf86cd799439011",
                "vector": [0.123, -0.456, 0.789],  # Shortened for example
                "payload": {
                    "content_type": "project",
                    "portfolio_id": "507f1f77bcf86cd799439011",
                    "title": "AI Task Manager",
                    "description": "Smart task management...",
                    "tech_stack": ["React", "Python"],
                    "url": "/projects/ai-task-manager"
                }
            }
        }
    }


class VectorSearchRequest(BaseModel):
    """Request schema for vector search"""
    
    # Query
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    
    # Multi-tenant
    portfolio_id: PyObjectId = Field(..., description="Portfolio to search within")
    
    # Search Parameters
    limit: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    score_threshold: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0-1)"
    )
    
    # Filtering
    content_types: Optional[List[ContentType]] = Field(
        None,
        description="Filter by content types"
    )
    tech_filter: Optional[List[str]] = Field(
        None,
        description="Filter by technology stack"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "machine learning projects",
                "portfolio_id": "507f1f77bcf86cd799439011",
                "limit": 5,
                "score_threshold": 0.7,
                "content_types": ["project", "blog"],
                "tech_filter": ["Python", "TensorFlow"]
            }
        }
    }


class VectorSearchResult(BaseModel):
    """Individual search result"""
    
    # Content Identification
    content_id: str = Field(..., description="Content ID (ObjectId string)")
    content_type: ContentType = Field(..., description="Type of content")
    
    # Score
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")
    
    # Content Data
    title: str = Field(..., description="Content title")
    description: str = Field(..., description="Content description/excerpt")
    url: Optional[str] = Field(None, description="URL to content")
    
    # Additional Metadata
    tech_stack: Optional[List[str]] = Field(None, description="Technologies used")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    image_url: Optional[str] = Field(None, description="Thumbnail/cover image")
    created_at: Optional[datetime] = Field(None, description="Content creation date")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "content_id": "507f1f77bcf86cd799439011",
                "content_type": "project",
                "score": 0.89,
                "title": "AI Task Manager",
                "description": "Smart task management with AI prioritization",
                "url": "/projects/ai-task-manager",
                "tech_stack": ["React", "Python", "TensorFlow"],
                "tags": ["AI", "productivity"],
                "image_url": "/images/projects/ai-task.png"
            }
        }
    }


class VectorSearchResponse(BaseModel):
    """Response schema for vector search"""
    
    # Search Metadata
    success: bool = Field(default=True, description="Search success status")
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Number of results found")
    search_time: float = Field(..., description="Search time in seconds")
    
    # Results
    results: List[VectorSearchResult] = Field(
        default_factory=list,
        description="Search results ordered by relevance"
    )
    
    # Query Understanding
    query_embedding_generated: bool = Field(
        default=True,
        description="Whether query embedding was generated"
    )
    used_cache: bool = Field(default=False, description="Whether cache was used")
    
    # Tokens & Cost (if embedding was generated)
    tokens_used: Optional[int] = Field(None, description="Tokens used for embedding")
    cost: Optional[float] = Field(None, description="API cost for embedding")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "query": "machine learning projects",
                "total_results": 3,
                "search_time": 0.15,
                "results": [
                    {
                        "content_id": "507f1f77bcf86cd799439011",
                        "content_type": "project",
                        "score": 0.89,
                        "title": "AI Task Manager",
                        "description": "Smart task management..."
                    }
                ],
                "tokens_used": 8,
                "cost": 0.000001
            }
        }
    }


class IndexRequest(BaseModel):
    """Request to index content"""
    
    # Content Identification
    content_id: PyObjectId = Field(..., description="Content ID to index")
    content_type: ContentType = Field(..., description="Type of content")
    portfolio_id: PyObjectId = Field(..., description="Portfolio this content belongs to")
    
    # Content to Index
    text_content: str = Field(..., description="Text content to generate embedding from")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "content_id": "507f1f77bcf86cd799439011",
                "content_type": "project",
                "portfolio_id": "507f1f77bcf86cd799439011",
                "text_content": "AI Task Manager - Smart task management with AI prioritization...",
                "metadata": {
                    "title": "AI Task Manager",
                    "tech_stack": ["React", "Python"],
                    "url": "/projects/ai-task-manager"
                }
            }
        }
    }


class IndexResponse(BaseModel):
    """Response after indexing content"""
    
    success: bool = Field(default=True, description="Indexing success status")
    content_id: str = Field(..., description="Indexed content ID")
    content_type: ContentType = Field(..., description="Content type")
    
    # Embedding Details
    vector_dimensions: int = Field(..., description="Embedding dimensions (1536)")
    tokens_used: int = Field(..., description="Tokens used for embedding")
    cost: float = Field(..., description="API cost for embedding")
    
    # Status
    message: str = Field(default="Content indexed successfully", description="Status message")
    indexed_at: datetime = Field(default_factory=datetime.utcnow, description="Index timestamp")


class BulkIndexRequest(BaseModel):
    """Request to index multiple content items"""
    
    portfolio_id: PyObjectId = Field(..., description="Portfolio ID")
    items: List[IndexRequest] = Field(..., description="Items to index")


class BulkIndexResponse(BaseModel):
    """Response after bulk indexing"""
    
    success: bool = Field(default=True, description="Overall success status")
    total_items: int = Field(..., description="Total items attempted")
    successful: int = Field(..., description="Successfully indexed")
    failed: int = Field(..., description="Failed to index")
    
    # Aggregated Metrics
    total_tokens: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total API cost")
    processing_time: float = Field(..., description="Total processing time in seconds")
    
    # Details
    failed_items: List[str] = Field(default_factory=list, description="IDs of failed items")
    message: str = Field(..., description="Status message")


class DeleteIndexRequest(BaseModel):
    """Request to delete indexed content"""
    
    content_id: PyObjectId = Field(..., description="Content ID to delete")
    portfolio_id: PyObjectId = Field(..., description="Portfolio ID for verification")


class DeleteIndexResponse(BaseModel):
    """Response after deleting indexed content"""
    
    success: bool = Field(default=True, description="Deletion success status")
    content_id: str = Field(..., description="Deleted content ID")
    message: str = Field(default="Content removed from index", description="Status message")


class CollectionStats(BaseModel):
    """Statistics about a Qdrant collection"""
    
    portfolio_id: PyObjectId = Field(..., description="Portfolio ID")
    collection_name: str = Field(..., description="Qdrant collection name")
    
    # Content Counts
    total_points: int = Field(..., description="Total indexed points")
    projects_count: int = Field(default=0, description="Number of projects")
    blogs_count: int = Field(default=0, description="Number of blog posts")
    other_count: int = Field(default=0, description="Other content types")
    
    # Collection Info
    vector_dimension: int = Field(default=1536, description="Vector dimensions")
    distance_metric: str = Field(default="cosine", description="Distance metric used")
    
    # Status
    last_indexed: Optional[datetime] = Field(None, description="Last indexing timestamp")
    is_healthy: bool = Field(default=True, description="Collection health status")


class VectorHealth(BaseModel):
    """Health check for vector search service"""
    
    status: str = Field(..., description="Service status (healthy/degraded/down)")
    qdrant_connected: bool = Field(..., description="Qdrant connection status")
    openai_connected: bool = Field(..., description="OpenAI connection status")
    
    # Performance
    avg_search_time: Optional[float] = Field(None, description="Average search time (ms)")
    avg_indexing_time: Optional[float] = Field(None, description="Average indexing time (ms)")
    
    # Metrics
    total_collections: int = Field(default=0, description="Number of collections")
    total_indexed_items: int = Field(default=0, description="Total indexed items")
    
    message: str = Field(..., description="Health status message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")


__all__ = [
    # Core Models
    "VectorPoint",
    "VectorSearchRequest",
    "VectorSearchResult",
    "VectorSearchResponse",
    
    # Indexing
    "IndexRequest",
    "IndexResponse",
    "BulkIndexRequest",
    "BulkIndexResponse",
    "DeleteIndexRequest",
    "DeleteIndexResponse",
    
    # Stats & Health
    "CollectionStats",
    "VectorHealth",
    
    # Enums
    "ContentType"
]