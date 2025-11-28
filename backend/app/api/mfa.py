"""
MFA (Multi-Factor Authentication) API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from ..models.schemas import MFAChallenge, MFAVerification, MFAResponse
from ..services.mfa_service import MFAService
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/mfa", tags=["mfa"])

# Initialize services
mfa_service = MFAService()
auth_service = AuthService()

@router.post("/challenge", response_model=MFAResponse)
async def create_mfa_challenge(
    mfa_request: MFAChallenge,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """
    Generate MFA challenge for high-risk scenarios
    """
    try:
        challenge = await mfa_service.generate_challenge(
            user_id=current_user["user_id"],
            method=mfa_request.method,
            contact_info=mfa_request.contact_info
        )
        
        return MFAResponse(
            challenge_id=challenge["challenge_id"],
            method=challenge["method"],
            expires_at=challenge["expires_at"],
            message="MFA challenge sent successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create MFA challenge: {str(e)}"
        )

@router.post("/verify")
async def verify_mfa_challenge(
    verification: MFAVerification,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """
    Verify MFA challenge response
    """
    try:
        result = await mfa_service.verify_challenge(
            challenge_id=verification.challenge_id,
            response_code=verification.response_code,
            user_id=current_user["user_id"]
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "MFA verification successful",
                "access_granted": True
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid MFA response"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"MFA verification failed: {str(e)}"
        )

@router.get("/status")
async def get_mfa_status(
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """
    Get user's MFA status and available methods
    """
    try:
        return {
            "user_id": current_user["user_id"],
            "mfa_enabled": True,
            "available_methods": ["sms", "email"],
            "preferred_method": "sms"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get MFA status: {str(e)}"
        )
