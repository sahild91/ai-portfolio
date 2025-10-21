from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat
from app.utils.logger import logger

# Create FastAPI app
app = FastAPI(
    title="AI Portfolio API",
    description="Backend API for AI-powered portfolio platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI Portfolio API",
        "version": "0.1.0",
        "status": "operational"
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-portfolio-api"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("AI Portfolio API starting...")
    logger.info("API documentation available at: /docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("AI Portfolio API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )