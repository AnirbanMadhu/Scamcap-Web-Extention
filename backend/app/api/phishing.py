"""
Phishing detection API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import asyncio

from ..models.schemas import PhishingRequest, PhishingResponse
from ..services.phishing_detector import PhishingDetector
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/analyze", tags=["phishing"])

# Initialize services
phishing_detector = PhishingDetector()
auth_service = AuthService()

@router.post("/phishing", response_model=PhishingResponse)
async def analyze_phishing(
    request: PhishingRequest,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """
    Analyze URL/content for phishing threats
    """
    try:
        # Perform phishing analysis
        result = await phishing_detector.analyze(
            url=request.url,
            content=request.content,
            domain=request.domain
        )
        
        return PhishingResponse(
            url=request.url,
            risk_level=result.risk_level,
            confidence=result.confidence,
            is_phishing=result.is_phishing,
            indicators=result.indicators,
            threat_types=result.threat_types,
            recommendations=result.recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing content: {str(e)}"
        )

@router.get("/phishing/status")
async def get_phishing_service_status():
    """
    Get phishing detection service status
    """
    try:
        # Test if the service is working
        test_result = await phishing_detector.analyze(
            url="https://example.com",
            content="test content",
            domain="example.com"
        )
        
        return {
            "status": "healthy",
            "service": "phishing_detector",
            "model_loaded": True,
            "test_analysis_completed": True
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "phishing_detector",
            "error": str(e)
        }
