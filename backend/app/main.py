from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Import routes - works when backend folder is deployed to Vercel
from app.api.routes.phishing import router as phishing_router
from app.api.routes.deepfake import router as deepfake_router
from app.api.routes.auth import router as auth_router
from app.api.routes.mfa import router as mfa_router
from app.api.routes.test import router as test_router
from app.config.database import connect_to_mongo, close_mongo_connection
from app.config.settings import get_settings

load_dotenv()

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

# Include API routes
app.include_router(test_router, prefix="/api/v1/test", tags=["testing"])
app.include_router(phishing_router, prefix="/api/v1/phishing", tags=["phishing"])
app.include_router(deepfake_router, prefix="/api/v1/deepfake", tags=["deepfake"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(mfa_router, prefix="/api/v1/mfa", tags=["mfa"])

@app.get("/")
async def root():
    return {"message": "ScamCap API is running", "version": "1.0.0"}

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
