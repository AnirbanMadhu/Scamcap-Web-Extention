// ScamCap Extension Configuration
// Update this URL after deploying your backend to Vercel

const CONFIG = {
    // IMPORTANT: Change this URL after deploying your backend to Vercel
    // Format: https://your-backend-project.vercel.app
    // For local development, use: http://localhost:8000
    API_BASE_URL: 'https://your-backend-url.vercel.app',
    
    // API version prefix
    API_VERSION: '/api/v1',
    
    // Get full API URL
    getApiUrl: function() {
        return this.API_BASE_URL + this.API_VERSION;
    },
    
    // Endpoints
    ENDPOINTS: {
        QUICK_SCAN: '/test/quick-scan',
        HEALTH: '/test/health',
        PHISHING_ANALYZE: '/phishing/analyze',
        DEEPFAKE_ANALYZE_IMAGE: '/deepfake/analyze-image',
        DEEPFAKE_ANALYZE_VIDEO: '/deepfake/analyze-video',
        AUTH_LOGIN: '/auth/login',
        AUTH_REGISTER: '/auth/register',
    },
    
    // Default settings
    DEFAULT_SETTINGS: {
        enabled: true,
        mfaEnabled: false,
        riskThreshold: 0.7,
        notificationsEnabled: true,
        autoScan: true
    },
    
    // Request timeout in milliseconds
    REQUEST_TIMEOUT: 10000,
    
    // Cache duration in milliseconds (5 minutes)
    CACHE_DURATION: 5 * 60 * 1000
};

// Make CONFIG immutable
if (typeof Object.freeze === 'function') {
    Object.freeze(CONFIG);
    Object.freeze(CONFIG.ENDPOINTS);
    Object.freeze(CONFIG.DEFAULT_SETTINGS);
}
