from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...models.schemas import UserCreate, UserUpdate, User, Token, APIResponse
from ...services.auth_service import AuthService, get_current_user
from ...config.database import get_database
import logging

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize auth service
auth_service = AuthService()

@router.post("/register", response_model=APIResponse)
async def register(user_data: UserCreate):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        db = get_database()
        existing_user = await db.users.find_one({"email": user_data.email})
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Create new user
        user = await auth_service.create_user(user_data)
        
        return APIResponse(
            success=True,
            message="User registered successfully",
            data={"user_id": user.id, "email": user.email}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )

@router.post("/login", response_model=APIResponse)
async def login(email: str, password: str):
    """
    Authenticate user and return access token
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        token = await auth_service.create_access_token({"sub": user.email})
        
        return APIResponse(
            success=True,
            message="Login successful",
            data={
                "access_token": token.access_token,
                "token_type": token.token_type,
                "expires_in": token.expires_in,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "mfa_enabled": user.mfa_enabled
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )

@router.get("/profile", response_model=APIResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get current user profile
    """
    try:
        return APIResponse(
            success=True,
            message="Profile retrieved successfully",
            data={
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "phone_number": current_user.phone_number,
                "mfa_enabled": current_user.mfa_enabled,
                "mfa_methods": current_user.mfa_methods,
                "created_at": current_user.created_at,
                "is_active": current_user.is_active
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve profile"
        )

@router.put("/profile", response_model=APIResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update current user profile
    """
    try:
        updated_user = await auth_service.update_user(current_user.id, user_update)
        
        return APIResponse(
            success=True,
            message="Profile updated successfully",
            data={
                "id": updated_user.id,
                "email": updated_user.email,
                "full_name": updated_user.full_name,
                "phone_number": updated_user.phone_number
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to update profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update profile"
        )

@router.post("/change-password", response_model=APIResponse)
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Change user password
    """
    try:
        # Verify current password
        if not await auth_service.verify_password(current_password, current_user.email):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )
        
        # Update password
        await auth_service.update_password(current_user.id, new_password)
        
        return APIResponse(
            success=True,
            message="Password changed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change password: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to change password"
        )

@router.post("/logout", response_model=APIResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user (invalidate token)
    """
    try:
        # In a real implementation, you would add the token to a blacklist
        # For now, we'll just return success
        return APIResponse(
            success=True,
            message="Logout successful"
        )
        
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Logout failed"
        )
