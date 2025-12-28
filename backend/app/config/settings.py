from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    debug: bool = True
    
    # Database Configuration
    mongodb_url: str = "mongodb://localhost:27017/scamcap"
    
    # JWT Configuration
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Risk Thresholds
    phishing_threshold: float = 0.7
    deepfake_threshold: float = 0.8
    mfa_trigger_threshold: float = 0.7
    
    # ML Models (Optional - placeholder implementation used)
    phishing_model_path: Optional[str] = None
    deepfake_model_path: Optional[str] = None
    
    # Risk Thresholds
    phishing_risk_threshold: float = 0.7
    deepfake_risk_threshold: float = 0.8
    mfa_trigger_threshold: float = 0.9
    
    # External Services
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    
    # Environment
    environment: str = "development"
    
    # CORS
    allowed_origins: str = "chrome-extension://*,http://localhost:3000"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # File Upload
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"]
    
    # Database name
    database_name: str = "scamcap"
    
    # Server configuration  
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from environment

# Global settings instance
_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
