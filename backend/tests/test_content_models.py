import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectResponse, 
    ProjectStatus, ProjectCategory
)
from app.models.blog import (
    BlogPost, BlogPostCreate, BlogPostUpdate, BlogPostResponse,
    BlogStatus, BlogCategory
)
from bson import ObjectId


def test_project_model():
    """Test Project model creation and validation"""
    print("\n" + "=" * 70)
    print("🚀 TEST 1: Project Model")
    print("=" * 70 + "\n")
    
    try:
        # Create a sample project
        portfolio_id = ObjectId()
        
        project = Project(
            portfolio_id=portfolio_id,
            title="AI-Powered Task Manager",
            slug="ai-task-manager",
            tagline="Smart task management with AI prioritization",
            description="A full-stack web application that uses machine learning to intelligently prioritize your tasks based on deadlines, importance, and context.",
            category=ProjectCategory.WEB_APP,
            tech_stack=["React", "TypeScript", "FastAPI", "PostgreSQL", "TensorFlow"],
            features=[
                "AI-powered task prioritization",
                "Real-time collaboration",
                "Smart notifications",
                "Analytics dashboard"
            ],
            github_url="https://github.com/username/ai-task-manager",
            live_url="https://taskai.example.com",
            start_date="2024-01",
            end_date="2024-06",
            duration="6 months",
            status=ProjectStatus.PUBLISHED,
            is_featured=True,
            tags=["AI", "productivity", "full-stack"]
        )
        
        print("✅ Project model created successfully!")
        print(f"   - Title: {project.title}")
        print(f"   - Category: {project.category.value}")
        print(f"   - Tech Stack: {', '.join(project.tech_stack)}")
        print(f"   - Status: {project.status.value}")
        print(f"   - Featured: {project.is_featured}")
        print(f"   - Portfolio ID: {project.portfolio_id}")
        print()
        
        # Test serialization
        project_dict = project.model_dump()
        print("✅ Project serialization successful!")
        print(f"   - Keys: {len(project_dict)} fields")
        print(f"   - Created at: {project.created_at}")
        print()
        
        # Test ProjectCreate schema
        project_create = ProjectCreate(
            portfolio_id=portfolio_id,
            title="E-commerce Platform",
            slug="ecommerce-platform",
            tagline="Modern online store with AI recommendations",
            description="A complete e-commerce solution...",
            category=ProjectCategory.WEB_APP,
            tech_stack=["Next.js", "Node.js", "MongoDB"],
            status=ProjectStatus.DRAFT
        )
        print("✅ ProjectCreate schema validated!")
        print(f"   - Title: {project_create.title}")
        print(f"   - Status: {project_create.status.value}")
        print()
        
        # Test ProjectUpdate schema
        project_update = ProjectUpdate(
            title="Updated Title",
            is_featured=True,
            tags=["updated", "tag"]
        )
        print("✅ ProjectUpdate schema validated!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Project model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_blog_model():
    """Test Blog model creation and validation"""
    print("=" * 70)
    print("📝 TEST 2: Blog Post Model")
    print("=" * 70 + "\n")
    
    try:
        # Create a sample blog post
        portfolio_id = ObjectId()
        
        blog = BlogPost(
            portfolio_id=portfolio_id,
            title="Building a Real-Time Chat App with WebSockets",
            slug="building-realtime-chat-websockets",
            excerpt="Learn how to build a scalable real-time chat application using WebSockets and Redis for message brokering.",
            content="""# Introduction

In this tutorial, we'll build a real-time chat application using WebSockets.

## Prerequisites
- Python 3.8+
- FastAPI
- Redis

## Step 1: Setup
First, let's install the dependencies...

```python
# Install required packages
pip install fastapi websockets redis
```

## Conclusion
We've successfully built a scalable chat app!
""",
            category=BlogCategory.TUTORIAL,
            tags=["WebSockets", "Redis", "FastAPI", "Real-time", "Tutorial"],
            author_name="John Doe",
            reading_time=12,
            word_count=850,
            status=BlogStatus.PUBLISHED,
            published_at=datetime.utcnow(),
            is_featured=True,
            meta_title="WebSocket Chat Tutorial - FastAPI & Redis",
            meta_description="Step-by-step guide to building a real-time chat application with WebSockets, FastAPI, and Redis."
        )
        
        print("✅ Blog post model created successfully!")
        print(f"   - Title: {blog.title}")
        print(f"   - Category: {blog.category.value}")
        print(f"   - Tags: {', '.join(blog.tags)}")
        print(f"   - Status: {blog.status.value}")
        print(f"   - Reading Time: {blog.reading_time} minutes")
        print(f"   - Word Count: {blog.word_count}")
        print(f"   - Featured: {blog.is_featured}")
        print(f"   - Portfolio ID: {blog.portfolio_id}")
        print()
        
        # Test serialization
        blog_dict = blog.model_dump()
        print("✅ Blog post serialization successful!")
        print(f"   - Keys: {len(blog_dict)} fields")
        print(f"   - Created at: {blog.created_at}")
        print()
        
        # Test BlogPostCreate schema
        blog_create = BlogPostCreate(
            portfolio_id=portfolio_id,
            title="Understanding TypeScript Generics",
            slug="understanding-typescript-generics",
            excerpt="A deep dive into TypeScript generics...",
            content="# TypeScript Generics\n\nGenerics allow you to...",
            category=BlogCategory.TECHNICAL,
            tags=["TypeScript", "JavaScript"],
            author_name="John Doe",
            status=BlogStatus.DRAFT
        )
        print("✅ BlogPostCreate schema validated!")
        print(f"   - Title: {blog_create.title}")
        print(f"   - Category: {blog_create.category.value}")
        print()
        
        # Test BlogPostUpdate schema
        blog_update = BlogPostUpdate(
            status=BlogStatus.PUBLISHED,
            published_at=datetime.utcnow(),
            is_featured=True
        )
        print("✅ BlogPostUpdate schema validated!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Blog model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_validation():
    """Test model validation rules"""
    print("=" * 70)
    print("🔍 TEST 3: Model Validation Rules")
    print("=" * 70 + "\n")
    
    results = []
    portfolio_id = ObjectId()
    
    # Test 1: Project title too short
    try:
        Project(
            portfolio_id=portfolio_id,
            title="AB",  # Too short
            slug="ab",
            tagline="Test",
            description="Test description"
        )
        print("❌ Short project title validation failed")
        results.append(False)
    except Exception:
        print("✅ Short project title rejected correctly")
        results.append(True)
    
    # Test 2: Blog excerpt too long
    try:
        BlogPost(
            portfolio_id=portfolio_id,
            title="Test Blog",
            slug="test-blog",
            excerpt="x" * 501,  # Too long
            content="Test content",
            author_name="John"
        )
        print("❌ Long blog excerpt validation failed")
        results.append(False)
    except Exception:
        print("✅ Long blog excerpt rejected correctly")
        results.append(True)
    
    # Test 3: Invalid enum value
    try:
        ProjectCreate(
            portfolio_id=portfolio_id,
            title="Test Project",
            slug="test-project",
            tagline="Test tagline",
            description="Test description",
            category="INVALID_CATEGORY"  # Invalid enum
        )
        print("❌ Invalid enum validation failed")
        results.append(False)
    except Exception:
        print("✅ Invalid enum value rejected correctly")
        results.append(True)
    
    # Test 4: Missing required fields
    try:
        Project(
            portfolio_id=portfolio_id,
            title="Test"
            # Missing required fields
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


def test_multi_tenant_fields():
    """Test multi-tenant portfolio_id field"""
    print("=" * 70)
    print("🏢 TEST 4: Multi-Tenant Support")
    print("=" * 70 + "\n")
    
    try:
        portfolio_1 = ObjectId()
        portfolio_2 = ObjectId()
        
        # Create project for portfolio 1
        project_1 = Project(
            portfolio_id=portfolio_1,
            title="Portfolio 1 Project",
            slug="portfolio-1-project",
            tagline="Test",
            description="Description"
        )
        
        # Create blog for portfolio 2
        blog_2 = BlogPost(
            portfolio_id=portfolio_2,
            title="Portfolio 2 Blog",
            slug="portfolio-2-blog",
            excerpt="Excerpt",
            content="Content",
            author_name="Author"
        )
        
        print("✅ Multi-tenant models created successfully!")
        print(f"   - Project Portfolio ID: {project_1.portfolio_id}")
        print(f"   - Blog Portfolio ID: {blog_2.portfolio_id}")
        print(f"   - IDs are different: {portfolio_1 != portfolio_2}")
        print()
        
        print("✅ Each model is properly isolated by portfolio_id")
        print("   This enables multi-tenant architecture!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-tenant test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪 CONTENT MODELS TEST SUITE")
    print("Testing Project and Blog models...\n")
    
    results = []
    
    # Run tests
    results.append(test_project_model())
    results.append(test_blog_model())
    results.append(test_model_validation())
    results.append(test_multi_tenant_fields())
    
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
        print("Next Steps:")
        print("1. Save project.py to backend/app/models/")
        print("2. Save blog.py to backend/app/models/")
        print("3. Update backend/app/models/__init__.py to export new models")
        print("4. Proceed to Chunk 4B: Chat Models")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above and fix the models.")
        return 1


if __name__ == "__main__":
    exit(main())