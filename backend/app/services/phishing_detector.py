"""
ScamCap Phishing Detector - Rule-based implementation
Analyzes URLs and content for phishing threats using pattern matching and heuristics.
"""
import asyncio
import re
import hashlib
import logging
import os
from typing import Optional, Dict, List, Any
from urllib.parse import urlparse
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class PhishingDetectionResult:
    def __init__(self):
        self.is_phishing: bool = False
        self.risk_score: float = 0.0
        self.confidence: float = 0.0
        self.threat_indicators: List[str] = []
        self.safe_alternatives: Optional[List[str]] = None
        self.analysis_details: Dict[str, Any] = {}


class PhishingDetector:
    def __init__(self):
        self.settings = get_settings()
        
        # Suspicious patterns and keywords
        self.suspicious_patterns = [
            r'urgent.*action.*required',
            r'verify.*account.*immediately',
            r'click.*here.*now',
            r'suspended.*account',
            r'confirm.*identity',
            r'update.*payment.*information',
            r'free.*money',
            r'winner.*lottery',
            r'tax.*refund',
            r'security.*alert'
        ]
        
        # Known phishing domains (simplified list)
        self.known_phishing_domains = {
            'paypal-security.com',
            'amazon-update.net',
            'microsoft-security.org',
            'google-verification.com',
            'apple-support.net',
            'netflix-billing.com'
        }
        
        # Legitimate domain patterns
        self.legitimate_domains = {
            'paypal.com', 'amazon.com', 'microsoft.com', 'google.com',
            'apple.com', 'facebook.com', 'twitter.com', 'linkedin.com',
            'netflix.com', 'instagram.com', 'youtube.com'
        }
        
        # Suspicious TLDs
        self.suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', 
                               '.top', '.club', '.online', '.site', '.buzz']
        
        # URL shorteners
        self.url_shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 
                              'short.ly', 'ow.ly', 'is.gd', 'buff.ly']

    async def analyze(
        self, 
        url: str, 
        content: Optional[str] = None,
        domain: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> PhishingDetectionResult:
        """
        Analyze URL and content for phishing threats
        """
        result = PhishingDetectionResult()
        
        try:
            # URL analysis (primary method)
            url_score = await self._analyze_url(url)
            result.analysis_details['url_analysis'] = url_score
            
            # Domain analysis
            domain_score = await self._analyze_domain(url, domain)
            result.analysis_details['domain_analysis'] = domain_score
            
            # Content analysis
            content_score = 0.0
            if content:
                content_score = await self._analyze_content(content)
                result.analysis_details['content_analysis'] = content_score
            
            # Header analysis
            header_score = 0.0
            if headers:
                header_score = await self._analyze_headers(headers)
                result.analysis_details['header_analysis'] = header_score
            
            # Calculate overall risk score
            weights = {
                'url': 0.35,
                'domain': 0.35,
                'content': 0.20,
                'headers': 0.10
            }
            
            result.risk_score = (
                url_score['score'] * weights['url'] +
                domain_score['score'] * weights['domain'] +
                content_score * weights['content'] +
                header_score * weights['headers']
            )
            
            # Determine if phishing
            result.is_phishing = result.risk_score >= self.settings.phishing_threshold
            result.confidence = min(result.risk_score * 1.2, 1.0)
            
            # Collect threat indicators
            result.threat_indicators = []
            if url_score['indicators']:
                result.threat_indicators.extend(url_score['indicators'])
            if domain_score['indicators']:
                result.threat_indicators.extend(domain_score['indicators'])
            
            # Suggest safe alternatives if phishing detected
            if result.is_phishing:
                result.safe_alternatives = await self._get_safe_alternatives(url)
            
            logger.info(f"Phishing analysis completed: {url} - Risk: {result.risk_score:.2f}")
            
        except Exception as e:
            logger.error(f"Phishing analysis failed: {e}")
            result.risk_score = 0.5  # Default to medium risk on error
            result.analysis_details['error'] = str(e)
        
        return result

    async def _analyze_url(self, url: str) -> Dict[str, Any]:
        """Analyze URL structure for suspicious patterns"""
        try:
            parsed = urlparse(url)
            score = 0.0
            indicators = []
            
            # Check for IP address instead of domain
            if re.search(r'\d+\.\d+\.\d+\.\d+', parsed.netloc):
                score += 0.5
                indicators.append("Uses IP address instead of domain name")
            
            # Check for very long domain
            if len(parsed.netloc) > 50:
                score += 0.2
                indicators.append("Unusually long domain name")
            
            # Check for too many hyphens
            if parsed.netloc.count('-') > 3:
                score += 0.3
                indicators.append("Excessive hyphens in domain")
            
            # Check for many numbers in domain
            if re.search(r'[0-9]{4,}', parsed.netloc):
                score += 0.3
                indicators.append("Suspicious numeric patterns in domain")
            
            # Check for @ symbol (phishing technique)
            if '@' in url:
                score += 0.6
                indicators.append("@ symbol in URL (phishing technique)")
            
            # Check for URL shorteners
            if any(shortener in parsed.netloc for shortener in self.url_shorteners):
                score += 0.3
                indicators.append("Uses URL shortener")
            
            # Check for suspicious TLDs - High risk indicator
            for tld in self.suspicious_tlds:
                if parsed.netloc.endswith(tld):
                    score += 0.5
                    indicators.append(f"High-risk domain extension ({tld})")
                    break
            
            # Check URL length
            if len(url) > 120:
                score += 0.2
                indicators.append("Unusually long URL")
            
            # Check for excessive subdomains
            subdomain_count = parsed.netloc.count('.')
            if subdomain_count > 4:
                score += 0.3
                indicators.append(f"Excessive subdomains ({subdomain_count})")
            
            # Check for URL encoding abuse
            if url.count('%') > 5:
                score += 0.2
                indicators.append("Excessive URL encoding")
            
            # Check for no HTTPS
            if parsed.scheme != 'https':
                score += 0.2
                indicators.append("No HTTPS encryption")
            
            return {
                'score': min(score, 1.0),
                'indicators': indicators,
                'details': {
                    'domain': parsed.netloc,
                    'path': parsed.path,
                    'scheme': parsed.scheme
                }
            }
            
        except Exception as e:
            logger.error(f"URL analysis failed: {e}")
            return {'score': 0.5, 'indicators': ['URL analysis failed'], 'details': {}}

    async def _analyze_domain(self, url: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Analyze domain reputation and legitimacy"""
        try:
            parsed = urlparse(url)
            domain = domain or parsed.netloc.lower()
            
            score = 0.0
            indicators = []
            
            # Check against known phishing domains
            if domain in self.known_phishing_domains:
                score = 1.0
                indicators.append("Domain is in known phishing list")
                return {'score': score, 'indicators': indicators, 'details': {'domain': domain}}
            
            # Check for domain spoofing - CRITICAL indicator
            # First, check if this IS a legitimate domain (to avoid false positives)
            clean_domain = domain.replace('www.', '')
            is_legitimate = False
            for legit_domain in self.legitimate_domains:
                if clean_domain == legit_domain or clean_domain.endswith('.' + legit_domain):
                    is_legitimate = True
                    break
            
            # Only check for spoofing if it's NOT a legitimate domain
            if not is_legitimate:
                for legit_domain in self.legitimate_domains:
                    legit_name = legit_domain.split('.')[0]  # e.g., 'amazon' from 'amazon.com'
                    # Check if legitimate brand name is in the domain but it's not the actual domain
                    if legit_name in domain and legit_domain not in domain:
                        score += 0.9  # Very high score for brand impersonation
                        indicators.append(f"⚠️ BRAND IMPERSONATION: Fake {legit_domain} domain!")
                        break
                    elif self._is_spoofed_domain(domain, legit_domain):
                        score += 0.85
                        indicators.append(f"Domain appears to spoof {legit_domain}")
                        break
            
            # Only check for suspicious keywords if not a legitimate domain
            if not is_legitimate:
                # Check for suspicious keywords in domain
                phishing_keywords = ['secure', 'login', 'verify', 'update', 'account', 
                                   'banking', 'support', 'help', 'service', 'suspended',
                                   'confirm', 'billing', 'payment', 'alert', 'security']
                keyword_count = sum(1 for kw in phishing_keywords if kw in domain)
                if keyword_count >= 3:
                    score += 0.6
                    indicators.append(f"Multiple phishing keywords in domain ({keyword_count} found)")
                elif keyword_count >= 2:
                    score += 0.45
                    indicators.append("Multiple suspicious keywords in domain")
                elif keyword_count == 1:
                    score += 0.25
                    indicators.append("Suspicious keyword in domain")
            
            # Check for excessive subdomains
            if domain.count('.') > 3:
                score += 0.2
                indicators.append("Excessive subdomains")
            
            return {
                'score': min(score, 1.0),
                'indicators': indicators,
                'details': {'domain': domain}
            }
            
        except Exception as e:
            logger.error(f"Domain analysis failed: {e}")
            return {'score': 0.5, 'indicators': ['Domain analysis failed'], 'details': {}}

    async def _analyze_content(self, content: str) -> float:
        """Analyze page content using pattern matching"""
        try:
            pattern_score = 0.0
            
            for pattern in self.suspicious_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    pattern_score += 0.2
            
            # Check for suspicious keywords
            suspicious_keywords = ['urgent', 'verify', 'suspended', 'click here', 'act now', 
                                   'limited time', 'password', 'account locked', 'confirm identity']
            keyword_count = sum(1 for keyword in suspicious_keywords if keyword in content.lower())
            keyword_score = min(keyword_count * 0.15, 0.6)
            
            # Combine scores
            final_score = min(pattern_score + keyword_score, 1.0)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return 0.5

    async def _analyze_headers(self, headers: Dict[str, str]) -> float:
        """Analyze HTTP headers for suspicious patterns"""
        try:
            score = 0.0
            
            # Check for missing security headers
            security_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'Strict-Transport-Security']
            missing_headers = [h for h in security_headers if h not in headers]
            score += len(missing_headers) * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Header analysis failed: {e}")
            return 0.0

    def _is_spoofed_domain(self, domain: str, legitimate: str) -> bool:
        """Check if domain is attempting to spoof a legitimate domain"""
        # Clean up domain (remove www. prefix)
        clean_domain = domain.lower().replace('www.', '')
        clean_legit = legitimate.lower().replace('www.', '')
        
        # If it's exactly the legitimate domain, it's not spoofed
        if clean_domain == clean_legit:
            return False
        
        # If domain ends with the legitimate domain (e.g., mail.google.com), it's not spoofed
        if clean_domain.endswith('.' + clean_legit) or clean_domain == clean_legit:
            return False
        
        # Check for character substitution attacks
        common_substitutions = {
            'o': '0', 'i': '1', 'l': '1', 'e': '3',
            'a': '@', 's': '$', 'g': '9'
        }
        
        for char, substitute in common_substitutions.items():
            spoofed = clean_legit.replace(char, substitute)
            if clean_domain == spoofed:
                return True
        
        # Check for typosquatting (adding/removing characters)
        legit_name = clean_legit.split('.')[0]  # e.g., 'google' from 'google.com'
        domain_name = clean_domain.split('.')[0]
        
        # If the domain name contains the brand but has extra characters AND different TLD
        if legit_name in domain_name and domain_name != legit_name:
            # This could be like 'google-login.com' or 'googlesecure.xyz'
            if not clean_domain.endswith(clean_legit):
                return True
        
        return False

    async def _get_safe_alternatives(self, url: str) -> List[str]:
        """Suggest safe alternatives for suspicious URLs"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        alternatives = []
        
        # Check if it's spoofing a known legitimate site
        for legit_domain in self.legitimate_domains:
            if legit_domain.replace('.com', '') in domain:
                alternatives.append(f"https://www.{legit_domain}")
        
        # Add general safe alternatives
        if not alternatives:
            alternatives = [
                "Visit the official website directly by typing the URL",
                "Contact the organization through official channels"
            ]
        
        return alternatives

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the phishing detection"""
        return {
            "model_name": "Rule-Based Phishing Detector",
            "version": "1.0.0",
            "analysis_methods": [
                "URL structure analysis",
                "Domain reputation checking",
                "Content pattern matching",
                "Header security analysis"
            ],
            "threshold": self.settings.phishing_threshold
        }
