import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.schemas import UserCreate, UserUpdate, User, Token, TokenData
from ..config.database import get_database
from ..config.settings import get_settings
import uuid

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.settings = get_settings()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            db = get_database()
            if db is None:
                logger.warning("Database not available, cannot get user by email")
                return None
                
            user_data = await db.users.find_one({"email": email})
            
            if user_data:
                user_data["id"] = str(user_data["_id"])
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            from bson import ObjectId
            db = get_database()
            if db is None:
                logger.warning("Database not available, cannot get user by ID")
                return None
                
            user_data = await db.users.find_one({"_id": ObjectId(user_id)})
            
            if user_data:
                user_data["id"] = str(user_data["_id"])
                return User(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None
            
            db = get_database()
            if db is None:
                logger.warning("Database not available, cannot authenticate")
                return None
                
            user_doc = await db.users.find_one({"email": email})
            
            if not user_doc or not self.verify_password(password, user_doc.get("hashed_password", "")):
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            db = get_database()
            if db is None:
                raise HTTPException(
                    status_code=503,
                    detail="Database not available"
                )
            
            # Hash password
            hashed_password = self.get_password_hash(user_data.password)
            
            # Create user document
            user_doc = {
                "_id": str(uuid.uuid4()),
                "email": user_data.email,
                "full_name": user_data.full_name,
                "hashed_password": hashed_password,
                "phone_number": user_data.phone_number,
                "is_active": user_data.is_active,
                "mfa_enabled": False,
                "mfa_methods": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert user
            await db.users.insert_one(user_doc)
            
            # Return user object
            user_doc["id"] = user_doc["_id"]
            return User(**user_doc)
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create user"
            )

    async def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        """Update user information"""
        try:
            from bson import ObjectId
            db = get_database()
            if db is None:
                raise HTTPException(
                    status_code=503,
                    detail="Database not available"
                )
            
            # Prepare update data
            update_data = {}
            if user_update.full_name is not None:
                update_data["full_name"] = user_update.full_name
            if user_update.phone_number is not None:
                update_data["phone_number"] = user_update.phone_number
            if user_update.is_active is not None:
                update_data["is_active"] = user_update.is_active
            
            update_data["updated_at"] = datetime.utcnow()
            
            # Update user
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            # Return updated user
            updated_user = await self.get_user_by_id(user_id)
            return updated_user
            
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update user"
            )

    async def update_password(self, user_id: str, new_password: str):
        """Update user password"""
        try:
            from bson import ObjectId
            db = get_database()
            if db is None:
                raise HTTPException(
                    status_code=503,
                    detail="Database not available"
                )
            
            hashed_password = self.get_password_hash(new_password)
            
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "hashed_password": hashed_password,
                    "updated_at": datetime.utcnow()
                }}
            )
            
        except Exception as e:
            logger.error(f"Failed to update password: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update password"
            )

    async def verify_password(self, password: str, email: str) -> bool:
        """Verify user password"""
        try:
            db = get_database()
            if db is None:
                logger.warning("Database not available, cannot verify password")
                return False
                
            user_doc = await db.users.find_one({"email": email})
            
            if not user_doc:
                return False
            
            return pwd_context.verify(password, user_doc.get("hashed_password", ""))
            
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    async def create_access_token(self, data: dict) -> Token:
        """Create JWT access token"""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=self.settings.access_token_expire_minutes)
            to_encode.update({"exp": expire})
            
            encoded_jwt = jwt.encode(
                to_encode, 
                self.settings.secret_key, 
                algorithm=self.settings.algorithm
            )
            
            return Token(
                access_token=encoded_jwt,
                token_type="bearer",
                expires_in=self.settings.access_token_expire_minutes * 60
            )
            
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create access token"
            )

    async def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.settings.secret_key, 
                algorithms=[self.settings.algorithm]
            )
            email: str = payload.get("sub")
            if email is None:
                return None
            
            return TokenData(email=email)
            
        except JWTError:
            return None

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        auth_service = AuthService()
        token_data = await auth_service.verify_token(token)
        
        if token_data is None:
            raise credentials_exception
        
        user = await auth_service.get_user_by_email(token_data.email)
        if user is None:
            raise credentials_exception
        
        return user
        
    except Exception as e:
        logger.error(f"Get current user failed: {e}")
        raise credentials_exception

# Dependency to get current active user
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
