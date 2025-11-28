// ScamCap Background Service Worker
// Handles API communication, threat analysis, and user notifications

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ScamCapBackground {
    constructor() {
        this.isEnabled = true;
        this.userToken = null;
        this.threatCache = new Map();
        this.riskThreshold = 0.7;
        
        this.initializeExtension();
    }

    async initializeExtension() {
        // Load user settings and authentication
        const settings = await this.loadSettings();
        this.isEnabled = settings.enabled !== false;
        this.userToken = settings.userToken;
        this.riskThreshold = settings.riskThreshold || 0.7;

        console.log('ScamCap initialized:', { enabled: this.isEnabled });
    }

    async loadSettings() {
        try {
            const result = await chrome.storage.sync.get([
                'enabled', 'userToken', 'riskThreshold', 'mfaEnabled'
            ]);
            return result;
        } catch (error) {
            console.error('Failed to load settings:', error);
            return {};
        }
    }

    async saveSettings(settings) {
        try {
            await chrome.storage.sync.set(settings);
        } catch (error) {
            console.error('Failed to save settings:', error);
        }
    }

    // Analyze URL for phishing threats
    async analyzePhishing(url, content = null, headers = null) {
        try {
            // Check cache first
            const cacheKey = this.generateCacheKey(url, content);
            if (this.threatCache.has(cacheKey)) {
                const cached = this.threatCache.get(cacheKey);
                if (Date.now() - cached.timestamp < 300000) { // 5 minutes cache
                    return cached.result;
                }
            }

            const response = await fetch(`${API_BASE_URL}/phishing/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.userToken}`
                },
                body: JSON.stringify({
                    url: url,
                    content: content,
                    headers: headers
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const result = await response.json();
            
            // Cache result
            this.threatCache.set(cacheKey, {
                result: result,
                timestamp: Date.now()
            });

            return result;

        } catch (error) {
            console.error('Phishing analysis failed:', error);
            return {
                success: false,
                data: {
                    is_phishing: false,
                    risk_score: 0.0,
                    confidence: 0.0,
                    threat_indicators: [],
                    analysis_details: { error: error.message }
                }
            };
        }
    }

    // Analyze media for deepfake threats
    async analyzeDeepfake(file, fileType) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const endpoint = fileType.startsWith('image/') ? 
                'deepfake/analyze-image' : 'deepfake/analyze-video';

            const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.userToken}`
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const result = await response.json();
            return result;

        } catch (error) {
            console.error('Deepfake analysis failed:', error);
            return {
                success: false,
                data: {
                    is_deepfake: false,
                    risk_score: 0.0,
                    confidence: 0.0,
                    analysis_method: 'error',
                    analysis_details: { error: error.message }
                }
            };
        }
    }

    // Trigger MFA when risk threshold is exceeded
    async triggerMFA(riskScore, threatType) {
        try {
            if (riskScore < this.riskThreshold) {
                return { mfa_required: false };
            }

            const response = await fetch(`${API_BASE_URL}/mfa/challenge`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.userToken}`
                },
                body: JSON.stringify({
                    user_id: 'current_user', // Will be derived from token
                    method: 'email', // Default to email
                    risk_score: riskScore
                })
            });

            if (!response.ok) {
                throw new Error(`MFA API error: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.data.mfa_required) {
                // Show MFA popup
                await this.showMFAPrompt(result.data);
            }

            return result.data;

        } catch (error) {
            console.error('MFA trigger failed:', error);
            return { mfa_required: false, error: error.message };
        }
    }

    // Show MFA prompt to user
    async showMFAPrompt(mfaData) {
        return new Promise((resolve) => {
            chrome.windows.create({
                url: chrome.runtime.getURL('popup/mfa.html') + 
                     `?session=${mfaData.session_id}&method=${mfaData.method}`,
                type: 'popup',
                width: 400,
                height: 300,
                focused: true
            }, (window) => {
                // Listen for MFA completion
                const listener = (message, sender, sendResponse) => {
                    if (message.type === 'MFA_COMPLETE' && sender.tab?.windowId === window.id) {
                        chrome.runtime.onMessage.removeListener(listener);
                        chrome.windows.remove(window.id);
                        resolve(message.verified);
                    }
                };
                chrome.runtime.onMessage.addListener(listener);
            });
        });
    }

    // Show threat warning to user
    async showThreatWarning(threatData, tabId) {
        // Create notification
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'assets/icons/icon-48.png',
            title: 'ScamCap Security Alert',
            message: `${threatData.threat_type} detected with ${Math.round(threatData.risk_score * 100)}% risk score`,
            priority: threatData.risk_score >= 0.8 ? 2 : 1
        });

        // Inject warning overlay into the page
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: this.injectWarningOverlay,
            args: [threatData]
        });

        // Update extension badge
        chrome.action.setBadgeText({
            text: '!',
            tabId: tabId
        });
        chrome.action.setBadgeBackgroundColor({
            color: threatData.risk_score >= 0.8 ? '#ff0000' : '#ff8800',
            tabId: tabId
        });
    }

    // Function to inject warning overlay (will be executed in content script context)
    injectWarningOverlay(threatData) {
        // Remove existing overlay
        const existingOverlay = document.getElementById('scamcap-warning-overlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }

        // Create warning overlay
        const overlay = document.createElement('div');
        overlay.id = 'scamcap-warning-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 0, 0, 0.9);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Arial, sans-serif;
        `;

        const warningBox = document.createElement('div');
        warningBox.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 500px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        `;

        const riskLevel = threatData.risk_score >= 0.8 ? 'HIGH' : 'MEDIUM';
        const riskColor = threatData.risk_score >= 0.8 ? '#ff0000' : '#ff8800';

        warningBox.innerHTML = `
            <h2 style="color: ${riskColor}; margin-top: 0;">⚠️ Security Threat Detected</h2>
            <p><strong>Threat Type:</strong> ${threatData.threat_type.toUpperCase()}</p>
            <p><strong>Risk Level:</strong> <span style="color: ${riskColor};">${riskLevel}</span></p>
            <p><strong>Risk Score:</strong> ${Math.round(threatData.risk_score * 100)}%</p>
            <p style="color: #666;">This content may be malicious or deceptive. Proceed with caution.</p>
            <div style="margin-top: 20px;">
                <button id="scamcap-proceed" style="margin-right: 10px; padding: 10px 20px; background: #007cba; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    I Understand, Proceed
                </button>
                <button id="scamcap-close-tab" style="padding: 10px 20px; background: #ccc; border: none; border-radius: 5px; cursor: pointer;">
                    Close Tab
                </button>
            </div>
        `;

        overlay.appendChild(warningBox);
        document.body.appendChild(overlay);

        // Add button event listeners
        document.getElementById('scamcap-proceed').onclick = () => {
            overlay.remove();
        };

        document.getElementById('scamcap-close-tab').onclick = () => {
            window.close();
        };
    }

    generateCacheKey(url, content) {
        const data = url + (content || '');
        return btoa(data).slice(0, 32); // Simple hash for caching
    }

    // Clean up old cache entries
    cleanCache() {
        const now = Date.now();
        for (const [key, value] of this.threatCache.entries()) {
            if (now - value.timestamp > 300000) { // 5 minutes
                this.threatCache.delete(key);
            }
        }
    }
}

// Initialize background service
const scamCap = new ScamCapBackground();

// Message handler for content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    switch (message.type) {
        case 'ANALYZE_PHISHING':
            scamCap.analyzePhishing(message.url, message.content, message.headers)
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true; // Keep channel open for async response

        case 'ANALYZE_DEEPFAKE':
            scamCap.analyzeDeepfake(message.file, message.fileType)
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;

        case 'THREAT_DETECTED':
            scamCap.showThreatWarning(message.threatData, sender.tab.id)
                .then(() => sendResponse({ success: true }))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;

        case 'TRIGGER_MFA':
            scamCap.triggerMFA(message.riskScore, message.threatType)
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;

        case 'GET_SETTINGS':
            scamCap.loadSettings()
                .then(settings => sendResponse(settings))
                .catch(error => sendResponse({ error: error.message }));
            return true;

        case 'SAVE_SETTINGS':
            scamCap.saveSettings(message.settings)
                .then(() => sendResponse({ success: true }))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;

        default:
            sendResponse({ success: false, error: 'Unknown message type' });
    }
});

// Tab update listener
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        // Reset badge for new page
        chrome.action.setBadgeText({ text: '', tabId: tabId });
        
        // Trigger automatic scan for high-risk domains
        if (scamCap.isEnabled) {
            // This would trigger content script analysis
            chrome.tabs.sendMessage(tabId, { type: 'SCAN_PAGE' }).catch(() => {
                // Ignore errors (content script might not be ready)
            });
        }
    }
});

// Periodic cache cleanup
setInterval(() => {
    scamCap.cleanCache();
}, 60000); // Every minute

// Command handler
chrome.commands.onCommand.addListener((command) => {
    switch (command) {
        case 'quick_scan':
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                if (tabs[0]) {
                    chrome.tabs.sendMessage(tabs[0].id, { type: 'QUICK_SCAN' });
                }
            });
            break;
        
        case 'toggle_protection':
            scamCap.isEnabled = !scamCap.isEnabled;
            scamCap.saveSettings({ enabled: scamCap.isEnabled });
            
            // Update all tabs
            chrome.tabs.query({}, (tabs) => {
                tabs.forEach(tab => {
                    chrome.tabs.sendMessage(tab.id, { 
                        type: 'TOGGLE_PROTECTION', 
                        enabled: scamCap.isEnabled 
                    }).catch(() => {});
                });
            });
            break;
    }
});

console.log('ScamCap background service worker loaded');
