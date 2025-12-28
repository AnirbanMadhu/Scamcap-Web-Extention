from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...models.schemas import DeepfakeRequest, DeepfakeResponse, APIResponse
from ...services.deepfake_detector import DeepfakeDetector
from ...services.auth_service import get_current_user
from ...services.threat_logger import ThreatLogger
from ...models.schemas import User, ThreatType
from ...config.settings import get_settings
import logging
import os
import uuid

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize services
deepfake_detector = DeepfakeDetector()
threat_logger = ThreatLogger()

@router.post("/analyze-image", response_model=APIResponse)
async def analyze_image_deepfake(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze uploaded image for deepfake manipulation
    """
    try:
        # Validate file
        if file.size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_file_size} bytes"
            )
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in [".jpg", ".jpeg", ".png"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Supported: JPG, JPEG, PNG"
            )
        
        # Save uploaded file temporarily
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_path = f"/tmp/{temp_filename}"
        
        content = await file.read()
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(content)
        
        # Perform deepfake detection
        result = await deepfake_detector.analyze_image(temp_path)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        # Log threat detection in background
        if background_tasks:
            background_tasks.add_task(
                threat_logger.log_threat,
                user_id=current_user.id,
                threat_type=ThreatType.DEEPFAKE,
                risk_score=result.risk_score,
                content_hash=result.content_hash,
                detection_details=result.analysis_details
            )
        
        # Prepare response
        response_data = DeepfakeResponse(
            is_deepfake=result.is_deepfake,
            risk_score=result.risk_score,
            confidence=result.confidence,
            analysis_method=result.analysis_method
        )
        
        return APIResponse(
            success=True,
            message="Image deepfake analysis completed",
            data=response_data.dict()
        )
        
    except Exception as e:
        logger.error(f"Image deepfake analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/analyze-video", response_model=APIResponse)
async def analyze_video_deepfake(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze uploaded video for deepfake manipulation
    """
    try:
        # Validate file
        if file.size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_file_size} bytes"
            )
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in [".mp4", ".avi", ".mov"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Supported: MP4, AVI, MOV"
            )
        
        # Save uploaded file temporarily
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_path = f"/tmp/{temp_filename}"
        
        content = await file.read()
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(content)
        
        # Perform deepfake detection
        result = await deepfake_detector.analyze_video(temp_path)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        # Log threat detection in background
        if background_tasks:
            background_tasks.add_task(
                threat_logger.log_threat,
                user_id=current_user.id,
                threat_type=ThreatType.DEEPFAKE,
                risk_score=result.risk_score,
                content_hash=result.content_hash,
                detection_details=result.analysis_details
            )
        
        # Prepare response
        response_data = DeepfakeResponse(
            is_deepfake=result.is_deepfake,
            risk_score=result.risk_score,
            confidence=result.confidence,
            analysis_method=result.analysis_method,
            frame_analysis=result.frame_analysis,
            temporal_consistency=result.temporal_consistency
        )
        
        return APIResponse(
            success=True,
            message="Video deepfake analysis completed",
            data=response_data.dict()
        )
        
    except Exception as e:
        logger.error(f"Video deepfake analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/model-info", response_model=APIResponse)
async def get_model_info():
    """
    Get information about the deepfake detection model
    """
    try:
        model_info = await deepfake_detector.get_model_info()
        return APIResponse(
            success=True,
            message="Model information retrieved",
            data=model_info
        )
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve model information"
        )

@router.post("/report-false-positive", response_model=APIResponse)
async def report_false_positive(
    content_hash: str,
    feedback: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Report a false positive detection for model improvement
    """
    try:
        # Log the feedback for model retraining
        background_tasks.add_task(
            threat_logger.log_feedback,
            user_id=current_user.id,
            content_hash=content_hash,
            feedback_type="false_positive",
            feedback=feedback
        )
        
        return APIResponse(
            success=True,
            message="False positive reported successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to report false positive: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to report false positive"
        )
