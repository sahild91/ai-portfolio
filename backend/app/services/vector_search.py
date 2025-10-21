import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition
)
from qdrant_client.http import models

from app.core.config import settings
from app.services.openai_service import OpenAIService
from app.models.vector_models import (
    VectorSearchRequest, VectorSearchResult, VectorSearchResponse,
    IndexRequest, IndexResponse, BulkIndexRequest, BulkIndexResponse,
    CollectionStats, VectorHealth, ContentType
)
from app.utils.logger import logger
from app.core.cache import get_cache


class VectorSearchService:
    """
    Vector search service using Qdrant
    Handles embedding generation and semantic search
    """
    
    def __init__(self):
        """Initialize Qdrant client and OpenAI service"""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=30
            )
            
            # Initialize OpenAI service for embeddings
            self.openai_service = OpenAIService()
            
            # Vector configuration
            self.vector_size = settings.VECTOR_DIMENSION  # 1536 for ada-002
            self.distance_metric = Distance.COSINE
            
            logger.info("VectorSearchService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorSearchService: {e}")
            raise
    
    def _objectid_to_uuid(self, objectid_str: str) -> str:
        """
        Convert MongoDB ObjectId to UUID v5
        Ensures consistent UUID generation for same ObjectId
        
        Args:
            objectid_str: MongoDB ObjectId as string
            
        Returns:
            UUID string
        """
        # Use UUID v5 with a namespace to ensure consistency
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
        return str(uuid.uuid5(namespace, objectid_str))
    
    def _get_collection_name(self, portfolio_id: str) -> str:
        """
        Get collection name for a portfolio
        Multi-tenant: Each portfolio has its own collection
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            Collection name (e.g., 'portfolio_507f1f77bcf86cd799439011')
        """
        prefix = settings.QDRANT_COLLECTION_PREFIX
        return f"{prefix}_{portfolio_id}"
    
    def create_collection(self, portfolio_id: str) -> bool:
        """
        Create a new collection for a portfolio
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            True if created or already exists
        """
        try:
            collection_name = self._get_collection_name(portfolio_id)
            
            # Check if collection exists
            collections = self.client.get_collections().collections
            existing = [c.name for c in collections]
            
            if collection_name in existing:
                logger.info(f"Collection {collection_name} already exists")
                return True
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance_metric
                )
            )
            
            logger.info(f"Created collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection for {portfolio_id}: {e}")
            return False
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (1536 dimensions) or None on error
        """
        try:
            result = self.openai_service.generate_embedding(text)
            
            if result.get("success"):
                return result["embedding"]
            else:
                logger.error(f"Embedding generation failed: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def index_content(self, request: IndexRequest) -> IndexResponse:
        """
        Index a single content item
        
        Args:
            request: IndexRequest with content details
            
        Returns:
            IndexResponse with status and cost
        """
        start_time = time.time()
        
        try:
            portfolio_id = str(request.portfolio_id)
            content_id = str(request.content_id)
            
            # Ensure collection exists
            self.create_collection(portfolio_id)
            collection_name = self._get_collection_name(portfolio_id)
            
            # Generate embedding
            logger.debug(f"Generating embedding for {request.content_type.value} {content_id}")
            embedding_result = self.openai_service.generate_embedding(
                text=request.text_content,
                portfolio_id=portfolio_id
            )
            
            if not embedding_result.get("success"):
                raise Exception(f"Embedding generation failed: {embedding_result.get('error')}")
            
            embedding = embedding_result["embedding"]
            tokens_used = embedding_result["usage"]["total_tokens"]
            cost = embedding_result["cost"]
            
            # Prepare payload (metadata) - STORE ORIGINAL ObjectId
            payload = {
                "content_id": content_id,  # ✅ Store original ObjectId
                "content_type": request.content_type.value,
                "portfolio_id": portfolio_id,
                "indexed_at": datetime.utcnow().isoformat(),
                **request.metadata
            }
            
            # Convert ObjectId to UUID for Qdrant
            point_uuid = self._objectid_to_uuid(content_id)
            
            # Create point
            point = PointStruct(
                id=point_uuid,  # ✅ Using UUID
                vector=embedding,
                payload=payload
            )
            
            # Upsert to Qdrant
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            elapsed_time = time.time() - start_time
            
            logger.info(
                f"Indexed {request.content_type.value} {content_id} "
                f"in {elapsed_time:.2f}s (tokens: {tokens_used}, cost: ${cost})"
            )
            
            return IndexResponse(
                success=True,
                content_id=content_id,
                content_type=request.content_type,
                vector_dimensions=self.vector_size,
                tokens_used=tokens_used,
                cost=cost,
                message="Content indexed successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to index content: {e}")
            
            return IndexResponse(
                success=False,
                content_id=str(request.content_id),
                content_type=request.content_type,
                vector_dimensions=self.vector_size,
                tokens_used=0,
                cost=0.0,
                message=f"Indexing failed: {str(e)}"
            )
    
    def bulk_index(self, request: BulkIndexRequest) -> BulkIndexResponse:
        """
        Index multiple content items in bulk
        
        Args:
            request: BulkIndexRequest with multiple items
            
        Returns:
            BulkIndexResponse with aggregated results
        """
        start_time = time.time()
        
        total_items = len(request.items)
        successful = 0
        failed = 0
        failed_items = []
        total_tokens = 0
        total_cost = 0.0
        
        logger.info(f"Starting bulk index of {total_items} items for portfolio {request.portfolio_id}")
        
        for item in request.items:
            result = self.index_content(item)
            
            if result.success:
                successful += 1
                total_tokens += result.tokens_used
                total_cost += result.cost
            else:
                failed += 1
                failed_items.append(result.content_id)
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"Bulk index complete: {successful}/{total_items} successful "
            f"(tokens: {total_tokens}, cost: ${total_cost:.6f}, time: {processing_time:.2f}s)"
        )
        
        return BulkIndexResponse(
            success=(failed == 0),
            total_items=total_items,
            successful=successful,
            failed=failed,
            total_tokens=total_tokens,
            total_cost=total_cost,
            processing_time=processing_time,
            failed_items=failed_items,
            message=f"Indexed {successful}/{total_items} items successfully"
        )
    
    def search(self, request: VectorSearchRequest) -> VectorSearchResponse:
        """
        Perform semantic search
        
        Args:
            request: VectorSearchRequest with query and filters
            
        Returns:
            VectorSearchResponse with results
        """
        start_time = time.time()
        
        try:
            portfolio_id = str(request.portfolio_id)
            collection_name = self._get_collection_name(portfolio_id)

            cache = get_cache()
            cache_key = f"{portfolio_id}:{request.query}:{request.limit}:{request.score_threshold}"
            
            cached_result = cache.get("vector_search", cache_key)
            if cached_result:
                logger.info(f"Cache hit for query: '{request.query[:50]}'")
                # Update metadata for cached response
                cached_result.search_time = time.time() - start_time
                cached_result.used_cache = True
                return cached_result
            
            # Check if collection exists
            collections = self.client.get_collections().collections
            existing = [c.name for c in collections]
            
            if collection_name not in existing:
                logger.warning(f"Collection {collection_name} does not exist")
                return VectorSearchResponse(
                    success=True,
                    query=request.query,
                    total_results=0,
                    search_time=time.time() - start_time,
                    results=[],
                    query_embedding_generated=False,
                    message="No indexed content found for this portfolio"
                )
            
            # Generate query embedding
            logger.debug(f"Generating embedding for query: {request.query}")
            embedding_result = self.openai_service.generate_embedding(
                text=request.query,
                portfolio_id=portfolio_id
            )
            
            if not embedding_result.get("success"):
                raise Exception(f"Query embedding failed: {embedding_result.get('error')}")
            
            query_vector = embedding_result["embedding"]
            tokens_used = embedding_result["usage"]["total_tokens"]
            cost = embedding_result["cost"]
            
            # Build filter conditions
            must_conditions = []
            
            # Filter by content types
            if request.content_types:
                content_type_values = [ct.value for ct in request.content_types]
                must_conditions.append(
                    FieldCondition(
                        key="content_type",
                        match=models.MatchAny(any=content_type_values)
                    )
                )
            
            # Filter by tech stack
            if request.tech_filter:
                for tech in request.tech_filter:
                    must_conditions.append(
                        FieldCondition(
                            key="tech_stack",
                            match=models.MatchValue(value=tech)
                        )
                    )
            
            # Build filter
            search_filter = Filter(must=must_conditions) if must_conditions else None
            
            # Perform search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=request.limit,
                score_threshold=request.score_threshold,
                query_filter=search_filter
            )
            
            # Convert to response format
            results = []
            for hit in search_results:
                original_id = hit.payload.get("content_id", str(hit.id))
                result = VectorSearchResult(
                    content_id=original_id,
                    content_type=ContentType(hit.payload.get("content_type", "other")),
                    score=float(hit.score),
                    title=hit.payload.get("title", "Untitled"),
                    description=hit.payload.get("description", ""),
                    url=hit.payload.get("url"),
                    tech_stack=hit.payload.get("tech_stack", []),
                    tags=hit.payload.get("tags", []),
                    image_url=hit.payload.get("image_url"),
                    created_at=hit.payload.get("created_at")
                )
                results.append(result)
            
            search_time = time.time() - start_time
            
            logger.info(
                f"Search complete: found {len(results)} results "
                f"in {search_time:.2f}s (query: '{request.query[:50]}...')"
            )
            
            response = VectorSearchResponse(
                success=True,
                query=request.query,
                total_results=len(results),
                search_time=search_time,
                results=results,
                query_embedding_generated=True,
                used_cache=False,
                tokens_used=tokens_used,
                cost=cost
            )
            
            # ✅ ADD THIS: Cache the result
            cache.set("vector_search", cache_key, response, cost=cost)
            
            return response        
            
        except Exception as e:
            search_time = time.time() - start_time
            logger.error(f"Search failed: {e}")
            
            return VectorSearchResponse(
                success=False,
                query=request.query,
                total_results=0,
                search_time=search_time,
                results=[],
                query_embedding_generated=False,
                message=f"Search failed: {str(e)}"
            )
        
    def delete_content(self, content_id: str, portfolio_id: str) -> Dict[str, Any]:
        """
        Delete content from vector index
        
        Args:
            content_id: Content ID to delete
            portfolio_id: Portfolio ID for verification
            
        Returns:
            Dict with success status and message
        """
        try:
            collection_name = self._get_collection_name(portfolio_id)
            
            # Check if collection exists
            collections = self.client.get_collections().collections
            existing = [c.name for c in collections]
            
            if collection_name not in existing:
                return {
                    "success": False,
                    "message": f"Collection {collection_name} not found"
                }
            
            point_uuid = self._objectid_to_uuid(content_id)
            # Delete point
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=[point_uuid]
                )
            )
            
            logger.info(f"Deleted content {content_id} from {collection_name}")
            
            return {
                "success": True,
                "content_id": content_id,
                "message": "Content removed from index"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete content {content_id}: {e}")
            return {
                "success": False,
                "content_id": content_id,
                "message": f"Deletion failed: {str(e)}"
            }
        
    def delete_collection(self, portfolio_id: str) -> bool:
        """
        Delete entire collection for a portfolio
        Use when deleting a portfolio
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            True if deleted successfully
        """
        try:
            collection_name = self._get_collection_name(portfolio_id)
            
            self.client.delete_collection(collection_name=collection_name)
            
            logger.info(f"Deleted collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False
    
    def get_collection_stats(self, portfolio_id: str) -> Optional[CollectionStats]:
        """
        Get statistics for a portfolio's collection
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            CollectionStats or None if collection doesn't exist
        """
        try:
            collection_name = self._get_collection_name(portfolio_id)
            
            # Get collection info - use count instead of get_collection
            try:
                # Get points count using count method
                count_result = self.client.count(
                    collection_name=collection_name,
                    exact=True
                )
                total_points = count_result.count
            except Exception as e:
                logger.warning(f"Could not get point count: {e}")
                total_points = 0
            
            # Count by content type
            projects_count = 0
            blogs_count = 0
            other_count = 0
            
            # Scroll through points to count by type
            try:
                offset = None
                batch_size = 100
                
                while True:
                    records, offset = self.client.scroll(
                        collection_name=collection_name,
                        limit=batch_size,
                        offset=offset,
                        with_payload=True,
                        with_vectors=False  # Don't fetch vectors, just payload
                    )
                    
                    for record in records:
                        content_type = record.payload.get("content_type", "other")
                        if content_type == "project":
                            projects_count += 1
                        elif content_type == "blog":
                            blogs_count += 1
                        else:
                            other_count += 1
                    
                    # Break if no more records
                    if offset is None:
                        break
            except Exception as e:
                logger.warning(f"Could not scroll collection: {e}")
            
            return CollectionStats(
                portfolio_id=portfolio_id,
                collection_name=collection_name,
                total_points=total_points,
                projects_count=projects_count,
                blogs_count=blogs_count,
                other_count=other_count,
                vector_dimension=self.vector_size,
                distance_metric="cosine",
                last_indexed=datetime.utcnow(),
                is_healthy=True
            )
            
        except Exception as e:
            logger.error(f"Failed to get stats for {portfolio_id}: {e}")
            return None
        
    def health_check(self) -> VectorHealth:
        """
        Check health of vector search service
        
        Returns:
            VectorHealth with status and metrics
        """
        try:
            # Test Qdrant connection
            qdrant_connected = False
            try:
                collections = self.client.get_collections()
                qdrant_connected = True
                total_collections = len(collections.collections)
            except Exception as e:
                logger.error(f"Qdrant health check failed: {e}")
                total_collections = 0
            
            # Test OpenAI connection
            openai_connected = False
            try:
                test_result = self.openai_service.generate_embedding("test")
                openai_connected = test_result.get("success", False)
            except Exception as e:
                logger.error(f"OpenAI health check failed: {e}")
            
            # Determine overall status
            if qdrant_connected and openai_connected:
                status = "healthy"
                message = "All systems operational"
            elif qdrant_connected or openai_connected:
                status = "degraded"
                message = "Some services unavailable"
            else:
                status = "down"
                message = "Critical services unavailable"
            
            # Calculate total indexed items
            total_indexed = 0
            if qdrant_connected:
                try:
                    for collection in collections.collections:
                        info = self.client.get_collection(collection.name)
                        total_indexed += info.points_count
                except:
                    pass
            
            return VectorHealth(
                status=status,
                qdrant_connected=qdrant_connected,
                openai_connected=openai_connected,
                total_collections=total_collections,
                total_indexed_items=total_indexed,
                message=message,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return VectorHealth(
                status="down",
                qdrant_connected=False,
                openai_connected=False,
                total_collections=0,
                total_indexed_items=0,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.utcnow()
            )
    
    def reindex_portfolio(self, portfolio_id: str, items: List[IndexRequest]) -> BulkIndexResponse:
        """
        Reindex entire portfolio (delete collection and reindex all content)
        
        Args:
            portfolio_id: Portfolio ID
            items: All content items to index
            
        Returns:
            BulkIndexResponse with results
        """
        try:
            logger.info(f"Reindexing portfolio {portfolio_id} with {len(items)} items")
            
            # Delete existing collection
            self.delete_collection(portfolio_id)
            
            # Create fresh collection
            self.create_collection(portfolio_id)
            
            # Bulk index all items
            bulk_request = BulkIndexRequest(
                portfolio_id=portfolio_id,
                items=items
            )
            
            result = self.bulk_index(bulk_request)
            
            logger.info(f"Reindex complete for {portfolio_id}: {result.successful}/{result.total_items} successful")
            
            return result
            
        except Exception as e:
            logger.error(f"Reindex failed for {portfolio_id}: {e}")
            return BulkIndexResponse(
                success=False,
                total_items=len(items),
                successful=0,
                failed=len(items),
                total_tokens=0,
                total_cost=0.0,
                processing_time=0.0,
                failed_items=[],
                message=f"Reindex failed: {str(e)}"
            )

# Singleton instance
_vector_search_service = None

def get_vector_search_service() -> VectorSearchService:
    """Get or create VectorSearchService singleton"""
    global _vector_search_service
    if _vector_search_service is None:
        _vector_search_service = VectorSearchService()
    return _vector_search_service

"""
Usage Examples:

# Initialize service
vector_service = get_vector_search_service()

# Create collection for new portfolio
vector_service.create_collection(portfolio_id="507f...")

# Index a project
from app.models.vector_models import IndexRequest, ContentType

request = IndexRequest(
    content_id=ObjectId("507f..."),
    content_type=ContentType.PROJECT,
    portfolio_id=ObjectId("507f..."),
    text_content="AI Task Manager - Smart task management...",
    metadata={
        "title": "AI Task Manager",
        "tech_stack": ["React", "Python"],
        "url": "/projects/ai-task-manager"
    }
)
result = vector_service.index_content(request)

# Search
from app.models.vector_models import VectorSearchRequest

search_req = VectorSearchRequest(
    query="React projects",
    portfolio_id=ObjectId("507f..."),
    limit=5
)
results = vector_service.search(search_req)

# Health check
health = vector_service.health_check()
print(f"Status: {health.status}")

# Get stats
stats = vector_service.get_collection_stats("507f...")
print(f"Total points: {stats.total_points}")
"""