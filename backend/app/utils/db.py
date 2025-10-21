"""
Database Connection Utility
MongoDB connection management with connection pooling
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings
from app.utils.logger import logger


class DatabaseManager:
    """
    MongoDB connection manager
    Handles connection lifecycle and provides database access
    """
    
    def __init__(self):
        """Initialize database manager"""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._is_connected: bool = False
    
    async def connect(self) -> None:
        """
        Establish connection to MongoDB
        Creates connection pool and selects database
        """
        try:
            logger.info(f"Connecting to MongoDB: {settings.MONGODB_DB_NAME}")
            
            # Create MongoDB client with connection pooling
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=settings.MONGODB_MAX_CONNECTIONS,
                minPoolSize=settings.MONGODB_MIN_CONNECTIONS,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
            )
            
            # Select database
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            
            self._is_connected = True
            logger.info("✅ MongoDB connected successfully")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB connection timeout: {str(e)}")
            raise
        
        except Exception as e:
            logger.exception(f"Unexpected error connecting to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close MongoDB connection
        Cleanup connection pool
        """
        if self.client:
            logger.info("Disconnecting from MongoDB...")
            self.client.close()
            self._is_connected = False
            logger.info("✅ MongoDB disconnected")
    
    async def health_check(self) -> dict:
        """
        Check database health
        
        Returns:
            Dict with health status and details
        """
        try:
            if not self._is_connected or not self.client:
                return {
                    "status": "disconnected",
                    "database": settings.MONGODB_DB_NAME,
                    "healthy": False
                }
            
            # Ping database
            await self.client.admin.command('ping')
            
            # Get server info
            server_info = await self.client.server_info()
            
            return {
                "status": "connected",
                "database": settings.MONGODB_DB_NAME,
                "healthy": True,
                "version": server_info.get("version", "unknown"),
                "collections": await self.db.list_collection_names()
            }
        
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "error",
                "database": settings.MONGODB_DB_NAME,
                "healthy": False,
                "error": str(e)
            }
    
    def get_collection(self, collection_name: str):
        """
        Get a collection from the database
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            AsyncIOMotorCollection instance
        """
        if not self._is_connected or self.db is None:
            raise ConnectionError("Database not connected")
        
        return self.db[collection_name]
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._is_connected


# ============================================
# Global Database Instance
# ============================================

# Create singleton instance
db_manager = DatabaseManager()


# ============================================
# Convenience Functions
# ============================================

async def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance
    Used for dependency injection in FastAPI
    """
    if not db_manager.is_connected:
        await db_manager.connect()
    return db_manager.db


def get_collection(collection_name: str):
    """
    Get collection by name
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection instance
    """
    return db_manager.get_collection(collection_name)


# ============================================
# Collection Names (Constants)
# ============================================

class Collections:
    """Database collection names"""
    USERS = "users"
    PORTFOLIOS = "portfolios"
    PROJECTS = "projects"
    BLOGS = "blogs"
    CHAT_HISTORY = "chat_history"
    USAGE_STATS = "usage_stats"


__all__ = [
    "db_manager",
    "get_database",
    "get_collection",
    "Collections",
    "DatabaseManager"
]