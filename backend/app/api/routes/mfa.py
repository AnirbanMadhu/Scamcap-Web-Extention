from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...models.schemas import MFARequest, MFAChallenge, MFAVerification, MFAResponse, APIResponse, User
from ...services.mfa_service import MFAService
from ...services.auth_service import get_current_user
import logging

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize MFA service
mfa_service = MFAService()

@router.post("/setup", response_model=APIResponse)
async def setup_mfa(
    method: str,  # "sms" or "email"
    phone_number: str = None,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Setup MFA for the current user
    """
    try:
        if method == "sms" and not phone_number:
            raise HTTPException(
                status_code=400,
                detail="Phone number required for SMS MFA"
            )
        
        # Setup MFA method
        result = await mfa_service.setup_mfa(
            user_id=current_user.id,
            method=method,
            phone_number=phone_number
        )
        
        return APIResponse(
            success=True,
            message=f"MFA setup successful for {method}",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA setup failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="MFA setup failed"
        )

@router.post("/challenge", response_model=APIResponse)
async def create_mfa_challenge(
    mfa_request: MFARequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create MFA challenge when risk threshold is exceeded
    """
    try:
        # Check if MFA is required based on risk score
        if mfa_request.risk_score < 0.7:  # Risk threshold
            return APIResponse(
                success=True,
                message="MFA not required - risk score below threshold",
                data={"mfa_required": False}
            )
        
        # Create MFA challenge
        challenge = await mfa_service.create_challenge(
            user_id=mfa_request.user_id,
            method=mfa_request.method,
            risk_score=mfa_request.risk_score
        )
        
        # Send MFA code in background
        background_tasks.add_task(
            mfa_service.send_mfa_code,
            challenge.session_id,
            challenge.method,
            current_user.email,
            current_user.phone_number
        )
        
        return APIResponse(
            success=True,
            message="MFA challenge created",
            data={
                "mfa_required": True,
                "session_id": challenge.session_id,
                "method": challenge.method,
                "expires_at": challenge.expires_at,
                "attempts_remaining": challenge.attempts_remaining
            }
        )
        
    except Exception as e:
        logger.error(f"MFA challenge creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create MFA challenge"
        )

@router.post("/verify", response_model=APIResponse)
async def verify_mfa(
    verification: MFAVerification,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verify MFA code
    """
    try:
        # Verify the MFA code
        result = await mfa_service.verify_code(
            session_id=verification.session_id,
            code=verification.code,
            user_id=current_user.id
        )
        
        if result.success:
            return APIResponse(
                success=True,
                message="MFA verification successful",
                data={"verified": True, "session_id": verification.session_id}
            )
        else:
            return APIResponse(
                success=False,
                message=result.message,
                data={"verified": False}
            )
        
    except Exception as e:
        logger.error(f"MFA verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="MFA verification failed"
        )

@router.get("/status", response_model=APIResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get MFA status for current user
    """
    try:
        status = await mfa_service.get_mfa_status(current_user.id)
        
        return APIResponse(
            success=True,
            message="MFA status retrieved",
            data=status
        )
        
    except Exception as e:
        logger.error(f"Failed to get MFA status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve MFA status"
        )

@router.post("/disable", response_model=APIResponse)
async def disable_mfa(
    method: str,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Disable MFA method for current user
    """
    try:
        result = await mfa_service.disable_mfa(
            user_id=current_user.id,
            method=method
        )
        
        return APIResponse(
            success=True,
            message=f"MFA {method} disabled successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Failed to disable MFA: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to disable MFA"
        )

@router.get("/backup-codes", response_model=APIResponse)
async def get_backup_codes(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get MFA backup codes for current user
    """
    try:
        backup_codes = await mfa_service.generate_backup_codes(current_user.id)
        
        return APIResponse(
            success=True,
            message="Backup codes generated",
            data={"backup_codes": backup_codes}
        )
        
    except Exception as e:
        logger.error(f"Failed to generate backup codes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate backup codes"
        )
