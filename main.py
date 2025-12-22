from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import routers
from app.routers import auth, screening, admin
from app.database import init_db_pool, close_db_pool

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting StrokeGuard API...")
    try:
        init_db_pool()
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down StrokeGuard API...")
    close_db_pool()
    logger.info("Database connection pool closed")

# Create FastAPI app
app = FastAPI(
    title="StrokeGuard API",
    description="API for stroke risk prediction with user management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(screening.router)
app.include_router(admin.router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to StrokeGuard API",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth (register, login)",
            "screening": "/screening (predict, history)",
            "admin": "/admin (patients, statistics)",
            "docs": "/docs (Swagger UI)",
            "redoc": "/redoc (ReDoc)"
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (Railway) or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

