"""
API Routes module - imports all route handlers
"""

from . import phishing, deepfake, auth, mfa

# Export all routers for easy import
__all__ = ["phishing", "deepfake", "auth", "mfa"]
