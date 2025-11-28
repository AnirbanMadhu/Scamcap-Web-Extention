from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ThreatType(str, Enum):
    PHISHING = "phishing"
    DEEPFAKE = "deepfake"
    UNKNOWN = "unknown"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MFAMethod(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    TOTP = "totp"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    phone_number: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    phone_number: Optional[str] = None
    mfa_enabled: bool = False
    mfa_methods: List[MFAMethod] = []

    class Config:
        populate_by_name = True

# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None

# Phishing Detection Models
class PhishingRequest(BaseModel):
    url: str
    content: Optional[str] = None
    domain: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

class PhishingResponse(BaseModel):
    is_phishing: bool
    risk_score: float
    confidence: float
    threat_indicators: List[str]
    safe_alternatives: Optional[List[str]] = None
    analysis_details: Dict[str, Any]

# Deepfake Detection Models
class DeepfakeRequest(BaseModel):
    file_type: str  # image, video
    file_size: int
    metadata: Optional[Dict[str, Any]] = None

class DeepfakeResponse(BaseModel):
    is_deepfake: bool
    risk_score: float
    confidence: float
    analysis_method: str
    frame_analysis: Optional[List[Dict[str, float]]] = None
    temporal_consistency: Optional[float] = None

# MFA Models
class MFARequest(BaseModel):
    user_id: str
    method: MFAMethod
    risk_score: float

class MFAChallenge(BaseModel):
    session_id: str
    method: MFAMethod
    expires_at: datetime
    attempts_remaining: int = 3

class MFAVerification(BaseModel):
    session_id: str
    code: str

class MFAResponse(BaseModel):
    success: bool
    message: str
    session_id: Optional[str] = None

# Threat Log Models
class ThreatLog(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    threat_type: ThreatType
    risk_score: float
    risk_level: RiskLevel
    url: Optional[str] = None
    content_hash: Optional[str] = None
    detection_details: Dict[str, Any]
    user_action: Optional[str] = None  # blocked, allowed, reported
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        populate_by_name = True

class ThreatLogCreate(BaseModel):
    user_id: str
    threat_type: ThreatType
    risk_score: float
    url: Optional[str] = None
    content_hash: Optional[str] = None
    detection_details: Dict[str, Any]
    user_action: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# Analytics Models
class ThreatStats(BaseModel):
    total_threats: int
    phishing_count: int
    deepfake_count: int
    blocked_count: int
    avg_risk_score: float
    top_threat_domains: List[Dict[str, Any]]
    detection_accuracy: float

class UserActivity(BaseModel):
    user_id: str
    daily_scans: int
    threats_detected: int
    mfa_triggers: int
    last_activity: datetime

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    error: str
    message: str
    code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
