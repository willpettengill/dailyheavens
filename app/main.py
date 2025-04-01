from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import interpretation

# Set up logging
setup_logging()

app = FastAPI(
    title="Daily Heavens Interpretation API",
    description="Astrological interpretation API",
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

# Include interpretation router
app.include_router(interpretation.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Daily Heavens Interpretation API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Debug endpoint for chart shape analysis
@app.post("/api/v1/debug/trace-interpretation")
async def debug_trace_interpretation(birth_chart_request: dict):
    """Debug endpoint for detailed interpretation tracing."""
    from app.services.interpretation import InterpretationService
    import logging
    import traceback
    logging.basicConfig(level=logging.DEBUG)
    
    service = InterpretationService()
    birth_chart = birth_chart_request.get("birth_chart", {})
    level = birth_chart_request.get("level", "basic")
    
    # Collect debug info
    debug_info = {}
    
    try:
        # Trace each main step
        debug_info["validate"] = service._validate_birth_chart(birth_chart)
        
        # Planet interpretations
        planet_interpretations = service._generate_planet_interpretations(birth_chart, level)
        debug_info["planets"] = len(planet_interpretations)
        
        # House interpretations
        house_interpretations = service._generate_house_interpretations(birth_chart, level)
        debug_info["houses"] = len(house_interpretations)
        
        # Aspect interpretations
        aspect_interpretations = service._generate_aspect_interpretations(birth_chart, level)
        debug_info["aspects"] = len(aspect_interpretations)
        
        # Element and modality analysis
        debug_info["element_balance"] = service._analyze_simple_element_balance(birth_chart)
        debug_info["modality_balance"] = service._analyze_simple_modality_balance(birth_chart)
        
        # Simple patterns
        simple_patterns = service._analyze_simple_patterns(birth_chart)
        debug_info["simple_patterns"] = len(simple_patterns)
        
        # Complex patterns
        complex_patterns = service._analyze_complex_patterns(birth_chart)
        debug_info["complex_patterns"] = len(complex_patterns)
        
        # Chart shape
        try:
            chart_shape = service._analyze_chart_shape(birth_chart)
            debug_info["chart_shape"] = chart_shape
        except Exception as e:
            debug_info["chart_shape_error"] = f"{type(e).__name__}: {str(e)}"
            debug_info["chart_shape_traceback"] = traceback.format_exc()
        
        # Overall interpretation
        debug_info["overall"] = service._generate_overall_interpretation(birth_chart, level)
        
        return {"debug_info": debug_info}
    except Exception as e:
        return {
            "error": str(e), 
            "type": str(type(e)), 
            "traceback": traceback.format_exc(),
            "partial_debug_info": debug_info
        }
