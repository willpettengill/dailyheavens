from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import birthchart

# Set up logging
setup_logging()

app = FastAPI(
    title="Daily Heavens Birth Chart API",
    description="Astrological birth chart calculation API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include birth chart router
app.include_router(birthchart.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Daily Heavens Birth Chart API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 