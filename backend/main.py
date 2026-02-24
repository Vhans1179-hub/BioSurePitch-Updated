from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports to work from both root and backend directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from backend.database import database
from backend.routers import patients, hcos, contracts, chat, pdfs, procurement

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# PDF endpoints are now available at /api/v1/pdfs
# Restarting to load new credentials and model configuration (gemini-1.5-pro-latest)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting up BioSure Backend API...")
    try:
        await database.connect_db()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.warning("API will start but database operations may fail")
    
    yield
    
    # Shutdown
    logger.info("Shutting down BioSure Backend API...")
    await database.close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router)
app.include_router(hcos.router)
app.include_router(contracts.router)
app.include_router(chat.router)
app.include_router(pdfs.router)
app.include_router(procurement.router)


@app.get("/healthz")
async def health_check():
    """
    Health check endpoint that verifies API and database connectivity.
    
    Returns:
        dict: Health status including database connection state
    """
    db_connected = await database.ping_db()
    
    return {
        "status": "ok",
        "database": "connected" if db_connected else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get(settings.api_v1_prefix + "/")
async def root():
    """
    Root endpoint for API v1.
    
    Returns:
        dict: Welcome message and API information
    """
    return {
        "message": "Welcome to BioSure Backend API",
        "version": settings.app_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use environment PORT if available (for Render), otherwise use settings
    port = int(os.getenv("PORT", settings.port))
    host = os.getenv("HOST", settings.host)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )