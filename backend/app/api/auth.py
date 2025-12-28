"""
Authentication API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from ..models.schemas import UserRegistration, UserLogin, TokenResponse, UserResponse
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Initialize services
auth_service = AuthService()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegistration):
    """
    Register a new user
    """
    try:
        result = await auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            phone=user_data.phone
        )
        
        return UserResponse(
            user_id=result["user_id"],
            username=user_data.username,
            email=user_data.email,
            message="User registered successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """
    Authenticate user and return access token
    """
    try:
        result = await auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        
        if not result:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Create access token
        token = auth_service.create_access_token(result)
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=result["user_id"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/logout")
async def logout_user(
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """
    Logout user (invalidate token on client side)
    """
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """
    Get current user information
    """
    return UserResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        email=current_user["email"],
        message="User information retrieved"
    )
