from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler):
        from pydantic_core import core_schema
        
        def validate(value: Any) -> str:
            if isinstance(value, ObjectId):
                return str(value)
            if isinstance(value, str):
                if ObjectId.is_valid(value):
                    return value
                raise ValueError("Invalid ObjectId string")
            raise ValueError("Invalid ObjectId")
        
        return core_schema.no_info_plain_validator_function(validate)


class BaseDBModel(BaseModel):
    """
    Base model with common fields for all database models
    Provides id, created_at, updated_at fields
    """
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Import all models
from app.models.user import (
    User, 
    UserCreate, 
    UserLogin, 
    UserResponse
)

from app.models.portfolio import (
    Portfolio,
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    SocialLinks,
    PortfolioSettings
)

from app.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectFilter,
    ProjectStatus,
    ProjectCategory
)

from app.models.blog import (
    BlogPost,
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostResponse,
    BlogPostListResponse,
    BlogPostFilter,
    BlogStatus,
    BlogCategory
)


__all__ = [
    # Base classes
    "BaseDBModel",
    "PyObjectId",
    
    # User models
    "User",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    
    # Portfolio models
    "Portfolio",
    "PortfolioCreate",
    "PortfolioUpdate",
    "PortfolioResponse",
    "SocialLinks",
    "PortfolioSettings",
    
    # Project models
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
    "ProjectFilter",
    "ProjectStatus",
    "ProjectCategory",
    
    # Blog models
    "BlogPost",
    "BlogPostCreate",
    "BlogPostUpdate",
    "BlogPostResponse",
    "BlogPostListResponse",
    "BlogPostFilter",
    "BlogStatus",
    "BlogCategory",

    # Chat models
    "ChatMessage",
    "ChatConversation",
    "ChatMessageCreate",
    "ChatConversationCreate",
    "ChatConversationUpdate",
    "ChatResponse",
    "ConversationListResponse",
    "ConversationFilter",
    "ConversationStats",
    "MessageRole",
    "MessageType",
    "ConversationStatus",
    
    # Vector models
    "VectorPoint",
    "VectorSearchRequest",
    "VectorSearchResult",
    "VectorSearchResponse",
    "IndexRequest",
    "IndexResponse",
    "BulkIndexRequest",
    "BulkIndexResponse",
    "DeleteIndexRequest",
    "DeleteIndexResponse",
    "CollectionStats",
    "VectorHealth",
    "ContentType",
]