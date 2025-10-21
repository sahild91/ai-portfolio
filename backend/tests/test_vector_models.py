import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.vector_models import (
    VectorPoint, VectorSearchRequest, VectorSearchResult,
    VectorSearchResponse, IndexRequest, IndexResponse,
    BulkIndexRequest, BulkIndexResponse, CollectionStats,
    VectorHealth, ContentType
)
from bson import ObjectId


def test_vector_point():
    """Test VectorPoint model"""
    print("\n" + "=" * 70)
    print("📍 TEST 1: Vector Point Model")
    print("=" * 70 + "\n")
    
    try:
        # Create a vector point
        point = VectorPoint(
            point_id="project_507f1f77bcf86cd799439011",
            vector=[0.123, -0.456, 0.789, 0.234] * 384,  # 1536 dimensions
            payload={
                "content_type": "project",
                "portfolio_id": "507f1f77bcf86cd799439011",
                "title": "AI Task Manager",
                "description": "Smart task management with AI prioritization",
                "tech_stack": ["React", "Python", "TensorFlow"],
                "url": "/projects/ai-task-manager",
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        print("✅ Vector point created successfully!")
        print(f"   - Point ID: {point.point_id}")
        print(f"   - Vector dimensions: {len(point.vector)}")
        print(f"   - Payload keys: {list(point.payload.keys())}")
        print(f"   - Content type: {point.payload['content_type']}")
        print(f"   - Title: {point.payload['title']}")
        print()
        
        # Verify vector dimensions
        if len(point.vector) == 1536:
            print("✅ Vector has correct dimensions (1536 for OpenAI ada-002)")
        else:
            print(f"⚠️  Vector dimensions: {len(point.vector)} (expected 1536)")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Vector point test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_search_models():
    """Test vector search request/response models"""
    print("=" * 70)
    print("🔍 TEST 2: Vector Search Models")
    print("=" * 70 + "\n")
    
    try:
        portfolio_id = ObjectId()
        
        # Create search request
        search_request = VectorSearchRequest(
            query="machine learning projects with Python",
            portfolio_id=portfolio_id,
            limit=5,
            score_threshold=0.7,
            content_types=[ContentType.PROJECT, ContentType.BLOG],
            tech_filter=["Python", "TensorFlow"]
        )
        
        print("✅ Search request created successfully!")
        print(f"   - Query: {search_request.query}")
        print(f"   - Portfolio ID: {search_request.portfolio_id}")
        print(f"   - Limit: {search_request.limit}")
        print(f"   - Score threshold: {search_request.score_threshold}")
        print(f"   - Content types: {[ct.value for ct in search_request.content_types]}")
        print(f"   - Tech filter: {search_request.tech_filter}")
        print()
        
        # Create search results
        results = [
            VectorSearchResult(
                content_id="507f1f77bcf86cd799439011",
                content_type=ContentType.PROJECT,
                score=0.92,
                title="AI Task Manager",
                description="Smart task management with AI prioritization",
                url="/projects/ai-task-manager",
                tech_stack=["React", "Python", "TensorFlow"],
                tags=["AI", "productivity"],
                image_url="/images/ai-task.png",
                created_at=datetime.utcnow()
            ),
            VectorSearchResult(
                content_id="507f1f77bcf86cd799439012",
                content_type=ContentType.BLOG,
                score=0.85,
                title="Building ML Models with TensorFlow",
                description="A comprehensive guide to building machine learning models",
                url="/blog/tensorflow-guide",
                tech_stack=["Python", "TensorFlow"],
                tags=["ML", "tutorial"]
            )
        ]
        
        # Create search response
        search_response = VectorSearchResponse(
            success=True,
            query=search_request.query,
            total_results=len(results),
            search_time=0.15,
            results=results,
            query_embedding_generated=True,
            used_cache=False,
            tokens_used=8,
            cost=0.000001
        )
        
        print("✅ Search response created successfully!")
        print(f"   - Success: {search_response.success}")
        print(f"   - Total results: {search_response.total_results}")
        print(f"   - Search time: {search_response.search_time}s")
        print(f"   - Tokens used: {search_response.tokens_used}")
        print(f"   - Cost: ${search_response.cost}")
        print()
        
        print("✅ Search results:")
        for i, result in enumerate(search_response.results, 1):
            print(f"   {i}. [{result.content_type.value}] {result.title}")
            print(f"      Score: {result.score:.2f} | Tech: {', '.join(result.tech_stack)}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Search models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_indexing_models():
    """Test content indexing models"""
    print("=" * 70)
    print("📇 TEST 3: Indexing Models")
    print("=" * 70 + "\n")
    
    try:
        portfolio_id = ObjectId()
        content_id = ObjectId()
        
        # Single index request
        index_request = IndexRequest(
            content_id=content_id,
            content_type=ContentType.PROJECT,
            portfolio_id=portfolio_id,
            text_content="AI Task Manager - Smart task management with AI prioritization. Built with React, Python, and TensorFlow.",
            metadata={
                "title": "AI Task Manager",
                "tech_stack": ["React", "Python", "TensorFlow"],
                "url": "/projects/ai-task-manager"
            }
        )
        
        print("✅ Index request created successfully!")
        print(f"   - Content ID: {index_request.content_id}")
        print(f"   - Content type: {index_request.content_type.value}")
        print(f"   - Text length: {len(index_request.text_content)} chars")
        print(f"   - Metadata keys: {list(index_request.metadata.keys())}")
        print()
        
        # Index response
        index_response = IndexResponse(
            success=True,
            content_id=str(content_id),
            content_type=ContentType.PROJECT,
            vector_dimensions=1536,
            tokens_used=25,
            cost=0.0000025,
            message="Content indexed successfully"
        )
        
        print("✅ Index response created successfully!")
        print(f"   - Success: {index_response.success}")
        print(f"   - Vector dimensions: {index_response.vector_dimensions}")
        print(f"   - Tokens used: {index_response.tokens_used}")
        print(f"   - Cost: ${index_response.cost}")
        print()
        
        # Bulk index request
        bulk_request = BulkIndexRequest(
            portfolio_id=portfolio_id,
            items=[
                IndexRequest(
                    content_id=ObjectId(),
                    content_type=ContentType.PROJECT,
                    portfolio_id=portfolio_id,
                    text_content="Project 1 description...",
                    metadata={"title": "Project 1"}
                ),
                IndexRequest(
                    content_id=ObjectId(),
                    content_type=ContentType.BLOG,
                    portfolio_id=portfolio_id,
                    text_content="Blog post 1 content...",
                    metadata={"title": "Blog 1"}
                )
            ]
        )
        
        print("✅ Bulk index request created successfully!")
        print(f"   - Portfolio ID: {bulk_request.portfolio_id}")
        print(f"   - Items to index: {len(bulk_request.items)}")
        print()
        
        # Bulk index response
        bulk_response = BulkIndexResponse(
            success=True,
            total_items=2,
            successful=2,
            failed=0,
            total_tokens=50,
            total_cost=0.000005,
            processing_time=0.5,
            failed_items=[],
            message="All items indexed successfully"
        )
        
        print("✅ Bulk index response created successfully!")
        print(f"   - Total items: {bulk_response.total_items}")
        print(f"   - Successful: {bulk_response.successful}")
        print(f"   - Failed: {bulk_response.failed}")
        print(f"   - Total tokens: {bulk_response.total_tokens}")
        print(f"   - Total cost: ${bulk_response.total_cost}")
        print(f"   - Processing time: {bulk_response.processing_time}s")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Indexing models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stats_and_health():
    """Test statistics and health models"""
    print("=" * 70)
    print("📊 TEST 4: Stats & Health Models")
    print("=" * 70 + "\n")
    
    try:
        portfolio_id = ObjectId()
        
        # Collection stats
        stats = CollectionStats(
            portfolio_id=portfolio_id,
            collection_name="portfolio_507f1f77bcf86cd799439011",
            total_points=25,
            projects_count=10,
            blogs_count=15,
            other_count=0,
            vector_dimension=1536,
            distance_metric="cosine",
            last_indexed=datetime.utcnow(),
            is_healthy=True
        )
        
        print("✅ Collection stats created successfully!")
        print(f"   - Collection: {stats.collection_name}")
        print(f"   - Total points: {stats.total_points}")
        print(f"   - Projects: {stats.projects_count}")
        print(f"   - Blogs: {stats.blogs_count}")
        print(f"   - Vector dimension: {stats.vector_dimension}")
        print(f"   - Distance metric: {stats.distance_metric}")
        print(f"   - Healthy: {stats.is_healthy}")
        print()
        
        # Vector health check
        health = VectorHealth(
            status="healthy",
            qdrant_connected=True,
            openai_connected=True,
            avg_search_time=150.5,
            avg_indexing_time=250.3,
            total_collections=5,
            total_indexed_items=125,
            message="All systems operational",
            timestamp=datetime.utcnow()
        )
        
        print("✅ Vector health check created successfully!")
        print(f"   - Status: {health.status}")
        print(f"   - Qdrant connected: {health.qdrant_connected}")
        print(f"   - OpenAI connected: {health.openai_connected}")
        print(f"   - Avg search time: {health.avg_search_time}ms")
        print(f"   - Avg indexing time: {health.avg_indexing_time}ms")
        print(f"   - Total collections: {health.total_collections}")
        print(f"   - Total items: {health.total_indexed_items}")
        print(f"   - Message: {health.message}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Stats & health test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test model validation"""
    print("=" * 70)
    print("🔍 TEST 5: Validation Rules")
    print("=" * 70 + "\n")
    
    results = []
    portfolio_id = ObjectId()
    
    # Test 1: Query too long
    try:
        VectorSearchRequest(
            query="x" * 501,  # Too long
            portfolio_id=portfolio_id
        )
        print("❌ Long query validation failed")
        results.append(False)
    except Exception:
        print("✅ Long query rejected correctly")
        results.append(True)
    
    # Test 2: Invalid limit
    try:
        VectorSearchRequest(
            query="test",
            portfolio_id=portfolio_id,
            limit=25  # > 20
        )
        print("❌ Invalid limit validation failed")
        results.append(False)
    except Exception:
        print("✅ Invalid limit rejected correctly")
        results.append(True)
    
    # Test 3: Invalid score threshold
    try:
        VectorSearchRequest(
            query="test",
            portfolio_id=portfolio_id,
            score_threshold=1.5  # > 1.0
        )
        print("❌ Invalid score threshold validation failed")
        results.append(False)
    except Exception:
        print("✅ Invalid score threshold rejected correctly")
        results.append(True)
    
    # Test 4: Missing required fields
    try:
        IndexRequest(
            content_id=ObjectId(),
            content_type=ContentType.PROJECT
            # Missing portfolio_id and text_content
        )
        print("❌ Missing required fields validation failed")
        results.append(False)
    except Exception:
        print("✅ Missing required fields rejected correctly")
        results.append(True)
    
    print()
    success_rate = sum(results) / len(results) * 100
    print(f"Validation Tests: {sum(results)}/{len(results)} passed ({success_rate:.0f}%)")
    print()
    
    return all(results)


def main():
    """Run all tests"""
    print("\n" + "🧪 VECTOR MODELS TEST SUITE")
    print("Testing vector search and embedding models...\n")
    
    results = []
    
    # Run tests
    results.append(test_vector_point())
    results.append(test_vector_search_models())
    results.append(test_indexing_models())
    results.append(test_stats_and_health())
    results.append(test_validation())
    
    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print()
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Tests Passed: {passed}/{total} ({success_rate:.0f}%)")
    print()
    
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print()
        print("🎉 ALL MODELS COMPLETE!")
        print()
        print("Models Summary:")
        print("✅ User & Portfolio models")
        print("✅ Project & Blog models (Chunk 4A)")
        print("✅ Chat models (Chunk 4B)")
        print("✅ Vector models (Chunk 4C)")
        print()
        print("Next Steps:")
        print("1. Save vector_models.py to backend/app/models/")
        print("2. Update backend/app/models/__init__.py")
        print("3. Ready for Chunk 5: Vector Search Service Implementation!")
        print()
        print("🚀 Time to build services that USE these models!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above and fix the models.")
        return 1


if __name__ == "__main__":
    exit(main())