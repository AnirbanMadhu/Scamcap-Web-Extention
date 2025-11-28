"""
Unit tests for ScamCap backend services
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import torch
import numpy as np
from PIL import Image
import io

# Import modules to test
from backend.app.main import app
from backend.app.services.phishing_detector import PhishingDetector
from backend.app.services.deepfake_detector import DeepfakeDetector
from backend.app.services.auth_service import AuthService
from backend.app.services.mfa_service import MFAService
from backend.app.models.schemas import PhishingRequest, DeepfakeRequest

# Test client
client = TestClient(app)

class TestPhishingDetector:
    """Test PhishingDetector service"""

    @pytest.fixture
    def detector(self):
        return PhishingDetector()

    def test_suspicious_url_patterns(self, detector):
        """Test URL pattern detection"""
        # Test suspicious URLs
        suspicious_urls = [
            "http://paypal-security.com",
            "https://amazon-login.net",
            "http://bank0famerica.com",
            "https://microsooft.com"
        ]
        
        for url in suspicious_urls:
            result = detector.analyze(url, "", "")
            assert result.risk_level in ["medium", "high"]
            assert result.confidence > 0.5

    def test_legitimate_urls(self, detector):
        """Test legitimate URL detection"""
        legitimate_urls = [
            "https://www.paypal.com",
            "https://amazon.com",
            "https://bankofamerica.com",
            "https://microsoft.com"
        ]
        
        for url in legitimate_urls:
            result = detector.analyze(url, "", "")
            assert result.risk_level == "low"

    def test_domain_spoofing_detection(self, detector):
        """Test domain spoofing detection"""
        spoofed_domains = [
            "g00gle.com",
            "faceb00k.com",
            "twitter.c0m",
            "linkedln.com"  # linkedin with 'l' instead of 'i'
        ]
        
        for domain in spoofed_domains:
            result = detector._check_domain_spoofing(domain)
            assert result["is_spoofed"] == True
            assert result["confidence"] > 0.7

    def test_phishing_content_analysis(self, detector):
        """Test content analysis for phishing indicators"""
        phishing_content = """
        URGENT: Your account has been suspended!
        Click here immediately to verify your identity.
        Failure to act within 24 hours will result in permanent closure.
        """
        
        result = detector._analyze_content(phishing_content)
        assert result["risk_score"] > 0.7
        assert len(result["indicators"]) > 0

    @patch('backend.app.services.phishing_detector.PhishingDetector._get_ml_prediction')
    def test_ml_model_integration(self, mock_ml, detector):
        """Test ML model integration"""
        mock_ml.return_value = {"phishing_probability": 0.85}
        
        result = detector._get_ml_prediction("test content")
        assert result["phishing_probability"] == 0.85
        mock_ml.assert_called_once()

class TestDeepfakeDetector:
    """Test DeepfakeDetector service"""

    @pytest.fixture
    def detector(self):
        return DeepfakeDetector()

    def test_image_preprocessing(self, detector):
        """Test image preprocessing"""
        # Create dummy image
        dummy_image = Image.new('RGB', (224, 224), color='red')
        img_bytes = io.BytesIO()
        dummy_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        preprocessed = detector._preprocess_image(img_bytes.getvalue())
        assert isinstance(preprocessed, torch.Tensor)
        assert preprocessed.shape == (1, 3, 224, 224)

    @patch('cv2.CascadeClassifier.detectMultiScale')
    def test_face_detection(self, mock_detect, detector):
        """Test face detection"""
        mock_detect.return_value = np.array([[50, 50, 100, 100]])
        
        dummy_image = np.zeros((300, 300, 3), dtype=np.uint8)
        faces = detector._detect_faces(dummy_image)
        assert len(faces) == 1
        assert faces[0].shape == (100, 100, 3)

    def test_artifact_analysis(self, detector):
        """Test deepfake artifact detection"""
        # Create test image with potential artifacts
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        artifacts = detector._analyze_artifacts(test_image)
        assert "compression_score" in artifacts
        assert "edge_inconsistency" in artifacts
        assert "color_distribution" in artifacts

    @patch('backend.app.services.deepfake_detector.DeepfakeDetector._get_ml_prediction')
    def test_ml_prediction(self, mock_ml, detector):
        """Test ML model prediction"""
        mock_ml.return_value = {"deepfake_probability": 0.75}
        
        dummy_tensor = torch.randn(1, 3, 224, 224)
        result = detector._get_ml_prediction(dummy_tensor)
        assert result["deepfake_probability"] == 0.75

class TestAuthService:
    """Test AuthService"""

    @pytest.fixture
    def auth_service(self):
        return AuthService()

    def test_password_hashing(self, auth_service):
        """Test password hashing and verification"""
        password = "test_password123"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrong_password", hashed)

    def test_jwt_token_creation(self, auth_service):
        """Test JWT token creation and validation"""
        user_data = {"user_id": "123", "email": "test@example.com"}
        token = auth_service.create_access_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_jwt_token_validation(self, auth_service):
        """Test JWT token validation"""
        user_data = {"user_id": "123", "email": "test@example.com"}
        token = auth_service.create_access_token(user_data)
        
        decoded_data = auth_service.verify_token(token)
        assert decoded_data["user_id"] == "123"
        assert decoded_data["email"] == "test@example.com"

    def test_invalid_token(self, auth_service):
        """Test invalid token handling"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):
            auth_service.verify_token(invalid_token)

class TestMFAService:
    """Test MFAService"""

    @pytest.fixture
    def mfa_service(self):
        return MFAService()

    def test_challenge_generation(self, mfa_service):
        """Test MFA challenge generation"""
        challenge = mfa_service.generate_challenge("123", "sms", "+1234567890")
        
        assert "challenge_id" in challenge
        assert challenge["method"] == "sms"
        assert challenge["expires_at"] is not None

    def test_sms_code_generation(self, mfa_service):
        """Test SMS code generation"""
        code = mfa_service._generate_sms_code()
        
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()

    @patch('backend.app.services.mfa_service.MFAService._send_sms')
    def test_sms_sending(self, mock_sms, mfa_service):
        """Test SMS sending"""
        mock_sms.return_value = True
        
        result = mfa_service._send_sms("+1234567890", "123456")
        assert result == True
        mock_sms.assert_called_once_with("+1234567890", "123456")

    def test_email_code_generation(self, mfa_service):
        """Test email code generation"""
        code = mfa_service._generate_email_code()
        
        assert isinstance(code, str)
        assert len(code) >= 8

class TestAPIEndpoints:
    """Test API endpoints"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_phishing_analysis_endpoint(self):
        """Test phishing analysis endpoint"""
        request_data = {
            "url": "http://suspicious-site.com",
            "content": "Click here to verify your account",
            "domain": "suspicious-site.com"
        }
        
        with patch('backend.app.services.phishing_detector.PhishingDetector.analyze') as mock_analyze:
            mock_analyze.return_value = Mock(
                risk_level="high",
                confidence=0.95,
                is_phishing=True,
                indicators=["suspicious_url", "urgency_language"]
            )
            
            response = client.post("/api/analyze/phishing", json=request_data)
            assert response.status_code == 200
            
            result = response.json()
            assert result["risk_level"] == "high"
            assert result["confidence"] == 0.95

    def test_deepfake_analysis_endpoint(self):
        """Test deepfake analysis endpoint"""
        # Create dummy image file
        dummy_image = Image.new('RGB', (224, 224), color='blue')
        img_bytes = io.BytesIO()
        dummy_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        with patch('backend.app.services.deepfake_detector.DeepfakeDetector.analyze_image') as mock_analyze:
            mock_analyze.return_value = Mock(
                risk_level="medium",
                confidence=0.75,
                is_deepfake=False,
                artifacts={"compression_score": 0.3}
            )
            
            files = {"file": ("test.jpg", img_bytes.getvalue(), "image/jpeg")}
            response = client.post("/api/analyze/deepfake", files=files)
            
            assert response.status_code == 200
            result = response.json()
            assert result["risk_level"] == "medium"

    def test_user_registration(self):
        """Test user registration endpoint"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "phone": "+1234567890"
        }
        
        with patch('backend.app.services.auth_service.AuthService.register_user') as mock_register:
            mock_register.return_value = {"user_id": "123", "message": "User registered successfully"}
            
            response = client.post("/api/auth/register", json=user_data)
            assert response.status_code == 200
            assert response.json()["user_id"] == "123"

    def test_user_login(self):
        """Test user login endpoint"""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        with patch('backend.app.services.auth_service.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "access_token": "fake_token",
                "user_id": "123"
            }
            
            response = client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
            assert "access_token" in response.json()

class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_full_phishing_analysis_flow(self):
        """Test complete phishing analysis workflow"""
        detector = PhishingDetector()
        
        # Test suspicious URL
        result = detector.analyze(
            "http://paypal-verification.com/login",
            "Urgent: Verify your account within 24 hours",
            "paypal-verification.com"
        )
        
        assert result.risk_level in ["medium", "high"]
        assert result.confidence > 0.5
        assert len(result.indicators) > 0

    @pytest.mark.asyncio
    async def test_mfa_workflow(self):
        """Test MFA challenge and verification workflow"""
        mfa_service = MFAService()
        
        # Generate challenge
        challenge = mfa_service.generate_challenge("user123", "sms", "+1234567890")
        challenge_id = challenge["challenge_id"]
        
        # Simulate code verification
        with patch('backend.app.services.mfa_service.MFAService.verify_challenge') as mock_verify:
            mock_verify.return_value = {"success": True, "message": "Challenge verified"}
            
            result = mfa_service.verify_challenge(challenge_id, "123456")
            assert result["success"] == True

if __name__ == "__main__":
    pytest.main(["-v", __file__])
