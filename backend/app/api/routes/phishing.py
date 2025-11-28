from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...models.schemas import PhishingRequest, PhishingResponse, APIResponse
from ...services.phishing_detector import PhishingDetector
from ...services.auth_service import get_current_user
from ...services.threat_logger import ThreatLogger
from ...models.schemas import User, ThreatType
import logging

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize services
phishing_detector = PhishingDetector()
threat_logger = ThreatLogger()

@router.post("/analyze", response_model=APIResponse)
async def analyze_phishing(
    request: PhishingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze URL and content for phishing threats
    """
    try:
        # Perform phishing detection
        result = await phishing_detector.analyze(
            url=request.url,
            content=request.content,
            domain=request.domain,
            headers=request.headers
        )
        
        # Log threat detection in background
        background_tasks.add_task(
            threat_logger.log_threat,
            user_id=current_user.id,
            threat_type=ThreatType.PHISHING,
            risk_score=result.risk_score,
            url=request.url,
            detection_details=result.analysis_details
        )
        
        # Prepare response
        response_data = PhishingResponse(
            is_phishing=result.is_phishing,
            risk_score=result.risk_score,
            confidence=result.confidence,
            threat_indicators=result.threat_indicators,
            safe_alternatives=result.safe_alternatives,
            analysis_details=result.analysis_details
        )
        
        return APIResponse(
            success=True,
            message="Phishing analysis completed",
            data=response_data.dict()
        )
        
    except Exception as e:
        logger.error(f"Phishing analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/bulk-analyze", response_model=APIResponse)
async def bulk_analyze_phishing(
    urls: list[str],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze multiple URLs for phishing threats
    """
    try:
        results = []
        
        for url in urls:
            result = await phishing_detector.analyze(url=url)
            results.append({
                "url": url,
                "is_phishing": result.is_phishing,
                "risk_score": result.risk_score,
                "confidence": result.confidence
            })
            
            # Log each threat detection
            background_tasks.add_task(
                threat_logger.log_threat,
                user_id=current_user.id,
                threat_type=ThreatType.PHISHING,
                risk_score=result.risk_score,
                url=url,
                detection_details=result.analysis_details
            )
        
        return APIResponse(
            success=True,
            message=f"Analyzed {len(urls)} URLs",
            data={"results": results}
        )
        
    except Exception as e:
        logger.error(f"Bulk phishing analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Bulk analysis failed: {str(e)}"
        )

@router.get("/model-info", response_model=APIResponse)
async def get_model_info():
    """
    Get information about the phishing detection model
    """
    try:
        model_info = await phishing_detector.get_model_info()
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
    url: str,
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
            url=url,
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
