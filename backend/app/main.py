from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env file if available (not needed in Vercel)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception as e:
    logger.info("dotenv not loaded (not needed in production)")

# Import routes - try multiple import styles for different environments
routes_loaded = False
import_error = None

# Try relative imports first (for Vercel/standalone backend), then absolute imports (for root project)
try:
    logger.info("Attempting to import routes...")
    
    # Try backend.app imports (when running from project root via start_server.py)
    try:
        from backend.app.api.routes.phishing import router as phishing_router
        from backend.app.api.routes.deepfake import router as deepfake_router
        from backend.app.api.routes.auth import router as auth_router
        from backend.app.api.routes.mfa import router as mfa_router
        from backend.app.api.routes.test import router as test_router
        from backend.app.config.database import connect_to_mongo, close_mongo_connection
        from backend.app.config.settings import get_settings
        logger.info("✓ Imported using backend.app prefix")
    except ImportError:
        # Try app imports (when running from backend folder / Vercel)
        from app.api.routes.phishing import router as phishing_router
        from app.api.routes.deepfake import router as deepfake_router
        from app.api.routes.auth import router as auth_router
        from app.api.routes.mfa import router as mfa_router
        from app.api.routes.test import router as test_router
        from app.config.database import connect_to_mongo, close_mongo_connection
        from app.config.settings import get_settings
        logger.info("✓ Imported using app prefix")
    
    routes_loaded = True
    logger.info("All imports successful!")
except Exception as e:
    import traceback
    import_error = str(e)
    logger.error(f"Failed to import routes: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    get_settings = lambda: None

# Initialize FastAPI app
app = FastAPI(
    title="ScamCap API",
    description="AI-powered phishing and deepfake detection service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection events (optional for serverless)
# @app.on_event("startup")
# async def startup_event():
#     await connect_to_mongo()

# @app.on_event("shutdown")
# async def shutdown_event():
#     await close_mongo_connection()

# Include API routes only if they loaded successfully
if routes_loaded:
    try:
        app.include_router(test_router, prefix="/api/v1/test", tags=["testing"])
        app.include_router(phishing_router, prefix="/api/v1/phishing", tags=["phishing"])
        app.include_router(deepfake_router, prefix="/api/v1/deepfake", tags=["deepfake"])
        app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
        app.include_router(mfa_router, prefix="/api/v1/mfa", tags=["mfa"])
        logger.info("All routes loaded successfully")
    except Exception as e:
        logger.error(f"Failed to include routes: {e}")

@app.get("/")
async def root():
    response = {
        "message": "ScamCap API is running", 
        "version": "1.0.0",
        "routes_loaded": routes_loaded
    }
    if import_error:
        response["import_error"] = import_error
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ScamCap API"}

# Vercel serverless handler
handler = app

if __name__ == "__main__":
    try:
        import uvicorn
        settings = get_settings()
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            workers=1 if settings.debug else 4
        )
    except ImportError:
        print("Uvicorn not available in serverless environment")
