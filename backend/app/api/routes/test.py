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
        
        # Start with the phishing detector's score as base
        risk_score = phishing_result.risk_score
        if phishing_result.threat_indicators:
            indicators.extend([f"⚠️ {indicator}" for indicator in phishing_result.threat_indicators])

        # Enhanced malware and suspicious site detection
        malware_indicators = await _analyze_malware_patterns(url, parsed_url)
        if malware_indicators['score'] > 0:
            risk_score = max(risk_score, risk_score + malware_indicators['score'] * 0.3)
            indicators.extend(malware_indicators['indicators'])

        # Additional suspicious patterns
        pattern_indicators = _analyze_suspicious_patterns(url, parsed_url)
        if pattern_indicators['score'] > 0:
            risk_score = max(risk_score, risk_score + pattern_indicators['score'] * 0.2)
            indicators.extend(pattern_indicators['indicators'])

        # Brand impersonation detection boost
        brand_names = ['paypal', 'amazon', 'microsoft', 'apple', 'google', 'netflix', 'facebook', 'instagram', 'twitter', 'linkedin', 'bank']
        domain = parsed_url.netloc.lower().replace('www.', '')
        
        # List of legitimate domain patterns
        legitimate_domains_exact = {
            'paypal.com', 'amazon.com', 'amazon.in', 'amazon.co.uk', 'microsoft.com', 
            'apple.com', 'google.com', 'netflix.com', 'facebook.com', 'instagram.com', 
            'twitter.com', 'x.com', 'linkedin.com', 'mail.google.com', 'accounts.google.com',
            'login.microsoft.com', 'outlook.com', 'live.com', 'github.com', 'youtube.com'
        }
        
        # Get the actual registered domain (last 2 parts for .com, last 3 for .co.uk etc)
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            # Handle common TLDs
            if len(domain_parts) >= 3 and domain_parts[-2] in ['co', 'com', 'org', 'net']:
                actual_domain = '.'.join(domain_parts[-3:])
            else:
                actual_domain = '.'.join(domain_parts[-2:])
        else:
            actual_domain = domain
        
        # Check if the ACTUAL domain (not subdomain) is legitimate
        is_legitimate = actual_domain in legitimate_domains_exact
        
        # Also check for legitimate subdomains of known domains
        for legit in legitimate_domains_exact:
            if domain == legit or (domain.endswith('.' + legit) and not any(brand in domain.replace(legit, '') for brand in brand_names)):
                is_legitimate = True
                break
        
        # Only check for brand impersonation if NOT a legitimate domain
        if not is_legitimate:
            for brand in brand_names:
                # If brand name appears anywhere in the domain
                if brand in domain:
                    # Check if the actual TLD domain is the real brand domain
                    real_domain = f"{brand}.com"
                    
                    # The key check: is the ACTUAL domain (last 2 parts) the real brand?
                    # For paypal.com.secure-verify.tk -> actual is secure-verify.tk, NOT paypal.com
                    if actual_domain != real_domain and not actual_domain.endswith(f".{brand}.com"):
                        risk_score = max(risk_score, 0.92)  # 92% for brand impersonation
                        if f"BRAND IMPERSONATION" not in str(indicators):
                            indicators.insert(0, f"🚨 CRITICAL: {brand.upper()} BRAND IMPERSONATION DETECTED!")
                            indicators.insert(1, f"⚠️ Fake domain pretending to be {real_domain}")
                        break

        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)

        # Determine risk level and safety based on thresholds:
        # 0-40% = SAFE (green)
        # 40-70% = MEDIUM (yellow) 
        # 70-100% = DANGER (red)
        if risk_score >= 0.7:
            risk_level = "DANGER"
            is_safe = False
            message = "🚨 DANGER - Phishing/Malware Detected! Do not proceed!"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
            is_safe = False
            message = "⚠️ MEDIUM RISK - Suspicious activity detected. Proceed with caution."
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
