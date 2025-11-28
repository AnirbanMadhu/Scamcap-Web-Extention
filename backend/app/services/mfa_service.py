import asyncio
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from ..models.schemas import MFAMethod, MFAChallenge, MFAResponse
from ..config.database import get_database
from ..config.settings import get_settings
import uuid

logger = logging.getLogger(__name__)

class MFAService:
    def __init__(self):
        self.settings = get_settings()
        
    async def setup_mfa(self, user_id: str, method: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """Setup MFA for a user"""
        try:
            from bson import ObjectId
            db = get_database()
            
            # Validate method
            if method not in ["sms", "email"]:
                raise ValueError("Invalid MFA method")
            
            # Update user MFA settings
            update_data = {
                "mfa_enabled": True,
                "updated_at": datetime.utcnow()
            }
            
            # Add method to user's MFA methods if not already present
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise ValueError("User not found")
            
            mfa_methods = user.get("mfa_methods", [])
            if method not in mfa_methods:
                mfa_methods.append(method)
                update_data["mfa_methods"] = mfa_methods
            
            # Update phone number if SMS method
            if method == "sms" and phone_number:
                update_data["phone_number"] = phone_number
            
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            return {
                "method": method,
                "enabled": True,
                "setup_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"MFA setup failed: {e}")
            raise

    async def create_challenge(self, user_id: str, method: str, risk_score: float) -> MFAChallenge:
        """Create MFA challenge"""
        try:
            db = get_database()
            
            # Generate session ID and code
            session_id = str(uuid.uuid4())
            mfa_code = self._generate_mfa_code()
            
            # Create challenge document
            challenge_doc = {
                "session_id": session_id,
                "user_id": user_id,
                "method": method,
                "code": mfa_code,
                "risk_score": risk_score,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=10),  # 10 min expiry
                "attempts_remaining": 3,
                "verified": False
            }
            
            await db.mfa_sessions.insert_one(challenge_doc)
            
            return MFAChallenge(
                session_id=session_id,
                method=MFAMethod(method),
                expires_at=challenge_doc["expires_at"],
                attempts_remaining=3
            )
            
        except Exception as e:
            logger.error(f"MFA challenge creation failed: {e}")
            raise

    async def send_mfa_code(self, session_id: str, method: str, email: str, phone_number: Optional[str] = None):
        """Send MFA code via specified method"""
        try:
            db = get_database()
            
            # Get MFA session
            session = await db.mfa_sessions.find_one({"session_id": session_id})
            if not session:
                raise ValueError("MFA session not found")
            
            code = session["code"]
            
            if method == "sms" and phone_number:
                await self._send_sms(phone_number, code)
            elif method == "email":
                await self._send_email(email, code)
            else:
                raise ValueError("Invalid MFA method or missing contact info")
            
            logger.info(f"MFA code sent via {method} for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to send MFA code: {e}")
            raise

    async def verify_code(self, session_id: str, code: str, user_id: str) -> MFAResponse:
        """Verify MFA code"""
        try:
            db = get_database()
            
            # Get MFA session
            session = await db.mfa_sessions.find_one({"session_id": session_id})
            if not session:
                return MFAResponse(
                    success=False,
                    message="Invalid session"
                )
            
            # Check if session is expired
            if datetime.utcnow() > session["expires_at"]:
                return MFAResponse(
                    success=False,
                    message="Session expired"
                )
            
            # Check if already verified
            if session.get("verified", False):
                return MFAResponse(
                    success=False,
                    message="Session already used"
                )
            
            # Check attempts remaining
            if session["attempts_remaining"] <= 0:
                return MFAResponse(
                    success=False,
                    message="Maximum attempts exceeded"
                )
            
            # Verify code
            if session["code"] == code and session["user_id"] == user_id:
                # Mark as verified
                await db.mfa_sessions.update_one(
                    {"session_id": session_id},
                    {"$set": {"verified": True, "verified_at": datetime.utcnow()}}
                )
                
                return MFAResponse(
                    success=True,
                    message="MFA verification successful",
                    session_id=session_id
                )
            else:
                # Decrement attempts
                await db.mfa_sessions.update_one(
                    {"session_id": session_id},
                    {"$inc": {"attempts_remaining": -1}}
                )
                
                return MFAResponse(
                    success=False,
                    message="Invalid code"
                )
            
        except Exception as e:
            logger.error(f"MFA verification failed: {e}")
            return MFAResponse(
                success=False,
                message="Verification error"
            )

    async def get_mfa_status(self, user_id: str) -> Dict[str, Any]:
        """Get MFA status for user"""
        try:
            from bson import ObjectId
            db = get_database()
            
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise ValueError("User not found")
            
            return {
                "mfa_enabled": user.get("mfa_enabled", False),
                "mfa_methods": user.get("mfa_methods", []),
                "phone_number_configured": bool(user.get("phone_number")),
                "backup_codes_count": len(user.get("backup_codes", []))
            }
            
        except Exception as e:
            logger.error(f"Failed to get MFA status: {e}")
            raise

    async def disable_mfa(self, user_id: str, method: str) -> Dict[str, Any]:
        """Disable specific MFA method"""
        try:
            from bson import ObjectId
            db = get_database()
            
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise ValueError("User not found")
            
            mfa_methods = user.get("mfa_methods", [])
            if method in mfa_methods:
                mfa_methods.remove(method)
            
            # If no methods left, disable MFA entirely
            mfa_enabled = len(mfa_methods) > 0
            
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "mfa_methods": mfa_methods,
                    "mfa_enabled": mfa_enabled,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {
                "method": method,
                "disabled": True,
                "mfa_enabled": mfa_enabled,
                "remaining_methods": mfa_methods
            }
            
        except Exception as e:
            logger.error(f"Failed to disable MFA: {e}")
            raise

    async def generate_backup_codes(self, user_id: str) -> List[str]:
        """Generate backup codes for MFA"""
        try:
            from bson import ObjectId
            db = get_database()
            
            # Generate 10 backup codes
            backup_codes = [self._generate_backup_code() for _ in range(10)]
            
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "backup_codes": backup_codes,
                    "backup_codes_generated_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return backup_codes
            
        except Exception as e:
            logger.error(f"Failed to generate backup codes: {e}")
            raise

    def _generate_mfa_code(self) -> str:
        """Generate 6-digit MFA code"""
        return ''.join(random.choices(string.digits, k=6))

    def _generate_backup_code(self) -> str:
        """Generate backup code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    async def _send_sms(self, phone_number: str, code: str):
        """Send SMS using Twilio"""
        try:
            # In production, use actual Twilio client
            if self.settings.twilio_account_sid and self.settings.twilio_auth_token:
                from twilio.rest import Client
                
                client = Client(
                    self.settings.twilio_account_sid,
                    self.settings.twilio_auth_token
                )
                
                message = client.messages.create(
                    body=f"Your ScamCap verification code is: {code}. This code expires in 10 minutes.",
                    from_=self.settings.twilio_phone_number,
                    to=phone_number
                )
                
                logger.info(f"SMS sent successfully: {message.sid}")
            else:
                # For development/testing
                logger.info(f"SMS would be sent to {phone_number}: {code}")
                
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            raise

    async def _send_email(self, email: str, code: str):
        """Send email with MFA code"""
        try:
            # In production, use actual email service (SendGrid, SES, etc.)
            # For now, just log the code
            logger.info(f"Email would be sent to {email}: {code}")
            
            # Example email content
            subject = "ScamCap Security Code"
            body = f"""
            Your ScamCap verification code is: {code}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            
            - ScamCap Security Team
            """
            
            # Here you would integrate with your email service
            # await send_email(email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
