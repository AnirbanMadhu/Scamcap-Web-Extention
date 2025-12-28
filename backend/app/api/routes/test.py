from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import re
from urllib.parse import urlparse
from ...services.phishing_detector import PhishingDetector

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

# Initialize detector
phishing_detector = PhishingDetector()

@router.post("/quick-scan")
async def quick_scan(request: QuickScanRequest):
    """
    Quick URL safety check using advanced phishing detection and malware analysis
    """
    try:
        url = request.url
        parsed_url = urlparse(url)

        risk_score = 0.0
        indicators = []

        # Use advanced phishing detection
        phishing_result = await phishing_detector.analyze(url, request.content)
        if phishing_result.is_phishing:
            risk_score += phishing_result.risk_score * 0.8  # Weight phishing detection heavily
            indicators.extend([f"🐟 {indicator}" for indicator in phishing_result.threat_indicators])

        # Enhanced malware and suspicious site detection
        malware_indicators = await _analyze_malware_patterns(url, parsed_url)
        if malware_indicators['score'] > 0:
            risk_score += malware_indicators['score'] * 0.6  # Weight malware detection
            indicators.extend(malware_indicators['indicators'])

        # Additional suspicious patterns
        pattern_indicators = _analyze_suspicious_patterns(url, parsed_url)
        if pattern_indicators['score'] > 0:
            risk_score += pattern_indicators['score'] * 0.4
            indicators.extend(pattern_indicators['indicators'])

        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)

        # Determine risk level and safety with enhanced thresholds
        if risk_score >= 0.8:
            risk_level = "CRITICAL"
            is_safe = False
            message = "🚨 CRITICAL RISK - Malware/Phishing Detected! Do not proceed!"
        elif risk_score >= 0.6:
            risk_level = "HIGH"
            is_safe = False
            message = "⚠️ HIGH RISK - Strong indicators of phishing/malware!"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
            is_safe = False
            message = "⚠️ MEDIUM RISK - Suspicious activity detected"
        elif risk_score >= 0.2:
            risk_level = "LOW"
            is_safe = False
            message = "⚠️ LOW RISK - Minor suspicious patterns found"
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

async def _analyze_malware_patterns(url: str, parsed_url) -> dict:
    """Analyze URL for malware distribution patterns"""
    score = 0.0
    indicators = []

    # Known malware distribution patterns
    malware_patterns = [
        r'\.exe$', r'\.scr$', r'\.pif$', r'\.bat$', r'\.cmd$', r'\.com$',  # Executable files
        r'\.zip$', r'\.rar$', r'\.7z$',  # Archive files that might contain malware
        r'crack', r'keygen', r'patch', r'serial',  # Piracy-related
        r'free.*download', r'download.*free',  # Suspicious download sites
        r'hack', r'exploit', r'vulnerability',  # Security-related suspicious terms
        r'malware', r'virus', r'trojan', r'ransomware',  # Direct malware terms
    ]

    url_lower = url.lower()
    malware_matches = []

    for pattern in malware_patterns:
        if re.search(pattern, url_lower, re.IGNORECASE):
            malware_matches.append(pattern.replace(r'\.', '.').replace('$', ''))

    if malware_matches:
        score += min(len(malware_matches) * 0.3, 0.8)
        indicators.append(f"🚨 Malware indicators detected: {', '.join(malware_matches[:3])}")

    # Check for drive-by download patterns
    drive_by_indicators = [
        r'auto.*download', r'force.*download', r'hidden.*download',
        r'iframe.*src', r'embed.*src', r'object.*data'
    ]

    for pattern in drive_by_indicators:
        if re.search(pattern, url_lower):
            score += 0.4
            indicators.append("🚨 Potential drive-by download detected")
            break

    # Check for suspicious query parameters
    query_params = parsed_url.query.lower()
    suspicious_params = ['exe', 'download', 'run', 'exec', 'cmd', 'shell']

    for param in suspicious_params:
        if param in query_params:
            score += 0.2
            indicators.append(f"🚨 Suspicious query parameter: {param}")
            break

    return {
        'score': min(score, 1.0),
        'indicators': indicators
    }

def _analyze_suspicious_patterns(url: str, parsed_url) -> dict:
    """Analyze URL for general suspicious patterns"""
    score = 0.0
    indicators = []

    # Check for HTTPS
    if parsed_url.scheme != 'https':
        score += 0.2
        indicators.append("🔒 No HTTPS encryption")

    # Enhanced suspicious keywords
    suspicious_keywords = [
        'login', 'verify', 'account', 'secure', 'update', 'confirm',
        'banking', 'paypal', 'amazon', 'microsoft', 'apple', 'google',
        'suspended', 'locked', 'billing', 'payment', 'credit', 'card',
        'password', 'security', 'alert', 'warning', 'urgent', 'immediate',
        'click', 'here', 'now', 'act', 'fast', 'quick', 'limited', 'time'
    ]

    url_lower = url.lower()
    keyword_matches = [kw for kw in suspicious_keywords if kw in url_lower]

    if len(keyword_matches) >= 4:
        score += 0.5
        indicators.append(f"🔍 Multiple suspicious keywords: {', '.join(keyword_matches[:4])}")
    elif len(keyword_matches) >= 2:
        score += 0.3
        indicators.append(f"🔍 Suspicious keywords detected: {', '.join(keyword_matches)}")

    # Check for IP address in URL
    if re.match(r'\d+\.\d+\.\d+\.\d+', parsed_url.netloc):
        score += 0.4
        indicators.append("🌐 IP address instead of domain name")

    # Enhanced suspicious TLDs
    suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.club', '.online', '.site']
    if any(parsed_url.netloc.endswith(tld) for tld in suspicious_tlds):
        score += 0.4
        indicators.append("🏴 Suspicious domain extension")

    # Check URL length
    if len(url) > 120:
        score += 0.2
        indicators.append("📏 Unusually long URL")

    # Check for excessive subdomains
    subdomain_count = parsed_url.netloc.count('.')
    if subdomain_count > 4:
        score += 0.3
        indicators.append(f"🔗 Excessive subdomains ({subdomain_count})")

    # Check for @ symbol in URL (phishing technique)
    if '@' in url:
        score += 0.5
        indicators.append("✉️ @ symbol in URL (phishing technique)")

    # Check for URL encoding abuse
    encoded_chars = url.count('%')
    if encoded_chars > 5:
        score += 0.2
        indicators.append("🔤 Excessive URL encoding")

    # Check for suspicious characters
    suspicious_chars = ['<', '>', '"', "'", ';', '|', '&', '$', '`']
    char_count = sum(url.count(char) for char in suspicious_chars)
    if char_count > 2:
        score += 0.3
        indicators.append("⚠️ Suspicious characters in URL")

    return {
        'score': min(score, 1.0),
        'indicators': indicators
    }
