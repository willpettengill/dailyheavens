from fastapi import FastAPI, Request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance with custom docs and openapi url
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

@app.get("/api/py/hello")
async def hello_fast_api():
    logger.info("Hello endpoint called")
    return {"message": "Hello from FastAPI"}

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "FastAPI root endpoint"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response