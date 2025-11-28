"""
Deepfake detection API routes
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Dict, Any
import asyncio

from ..models.schemas import DeepfakeRequest, DeepfakeResponse
from ..services.deepfake_detector import DeepfakeDetector
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/analyze", tags=["deepfake"])

# Initialize services
deepfake_detector = DeepfakeDetector()
auth_service = AuthService()

@router.post("/deepfake", response_model=DeepfakeResponse)
async def analyze_deepfake(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """
    Analyze image/video for deepfake content
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Determine analysis type based on file type
        if file.content_type.startswith('image/'):
            result = await deepfake_detector.analyze_image(file_content)
        elif file.content_type.startswith('video/'):
            result = await deepfake_detector.analyze_video(file_content)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload an image or video."
            )
        
        return DeepfakeResponse(
            filename=file.filename,
            file_type=file.content_type,
            risk_level=result.risk_level,
            confidence=result.confidence,
            is_deepfake=result.is_deepfake,
            artifacts=result.artifacts,
            analysis_details=result.analysis_details
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing file: {str(e)}"
        )

@router.get("/deepfake/status")
async def get_deepfake_service_status():
    """
    Get deepfake detection service status
    """
    try:
        return {
            "status": "healthy",
            "service": "deepfake_detector",
            "model_loaded": True,
            "supported_formats": ["image/jpeg", "image/png", "video/mp4"]
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "deepfake_detector",
            "error": str(e)
        }
