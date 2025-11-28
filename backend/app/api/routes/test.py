from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import re
from urllib.parse import urlparse

router = APIRouter()

class QuickScanRequest(BaseModel):
    url: str
    content: Optional[str] = None

class QuickScanResponse(BaseModel):
    success: bool
    is_safe: bool
    risk_score: float
    risk_level: str
    message: str
    indicators: list

@router.post("/quick-scan")
async def quick_scan(request: QuickScanRequest):
    """
    Quick URL safety check without authentication
    Simple heuristic-based analysis for demo purposes
    """
    try:
        url = request.url
        parsed_url = urlparse(url)

        risk_score = 0.0
        indicators = []

        # Check for HTTPS
        if parsed_url.scheme != 'https':
            risk_score += 0.3
            indicators.append("⚠️ No HTTPS encryption")

        # Check for suspicious keywords in URL
        suspicious_keywords = [
            'login', 'verify', 'account', 'secure', 'update',
            'banking', 'paypal', 'amazon', 'microsoft', 'apple',
            'suspended', 'locked', 'confirm', 'billing'
        ]

        url_lower = url.lower()
        suspicious_count = sum(1 for keyword in suspicious_keywords if keyword in url_lower)

        if suspicious_count >= 3:
            risk_score += 0.4
            indicators.append(f"⚠️ Multiple suspicious keywords found ({suspicious_count})")
        elif suspicious_count >= 2:
            risk_score += 0.2
            indicators.append(f"⚠️ Suspicious keywords detected")

        # Check for IP address in URL
        if re.match(r'\d+\.\d+\.\d+\.\d+', parsed_url.netloc):
            risk_score += 0.3
            indicators.append("IP address instead of domain name")

        # Check for suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top']
        if any(parsed_url.netloc.endswith(tld) for tld in suspicious_tlds):
            risk_score += 0.3
            indicators.append("Suspicious domain extension")

        # Check URL length
        if len(url) > 100:
            risk_score += 0.1
            indicators.append("Unusually long URL")

        # Check for excessive subdomains
        subdomain_count = parsed_url.netloc.count('.')
        if subdomain_count > 3:
            risk_score += 0.2
            indicators.append(f"Excessive subdomains ({subdomain_count})")

        # Check for @ symbol in URL (phishing technique)
        if '@' in url:
            risk_score += 0.4
            indicators.append("@ symbol in URL (common phishing technique)")

        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)

        # Determine risk level and safety
        if risk_score >= 0.7:
            risk_level = "HIGH"
            is_safe = False
            message = "⚠️ High Risk - This site may be dangerous!"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
            is_safe = False
            message = "⚠️ Medium Risk - Proceed with caution"
        elif risk_score >= 0.2:
            risk_level = "LOW"
            is_safe = True
            message = "✓ Low Risk - Appears safe"
        else:
            risk_level = "SAFE"
            is_safe = True
            message = "✓ Safe - No threats detected"

        if not indicators:
            indicators = ["No suspicious patterns detected"]

        return QuickScanResponse(
            success=True,
            is_safe=is_safe,
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            message=message,
            indicators=indicators
        )

    except Exception as e:
        return QuickScanResponse(
            success=False,
            is_safe=True,
            risk_score=0.0,
            risk_level="UNKNOWN",
            message=f"Error analyzing URL: {str(e)}",
            indicators=["Analysis failed"]
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ScamCap Quick Scan",
        "version": "1.0.0"
    }
