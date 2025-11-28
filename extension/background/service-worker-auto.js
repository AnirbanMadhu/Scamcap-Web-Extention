// ScamCap Background Service Worker - Automatic Version
// Automatically scans pages and shows notifications

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ScamCapAuto {
    constructor() {
        this.isEnabled = true;
        this.scanCache = new Map();
        this.cacheDuration = 300000; // 5 minutes

        console.log('ScamCap Auto initialized');
        this.setupListeners();
    }

    setupListeners() {
        // Listen for tab updates (page loads)
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete' && tab.url) {
                this.autoScanPage(tabId, tab.url);
            }
        });

        // Listen for messages from content script or popup
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true;
        });

        // Listen for tab activation
        chrome.tabs.onActivated.addListener(async (activeInfo) => {
            const tab = await chrome.tabs.get(activeInfo.tabId);
            if (tab.url) {
                this.autoScanPage(activeInfo.tabId, tab.url);
            }
        });
    }

    async autoScanPage(tabId, url) {
        if (!this.isEnabled) return;
        if (!this.shouldScanUrl(url)) return;

        try {
            // Check cache first
            const cached = this.scanCache.get(url);
            if (cached && Date.now() - cached.timestamp < this.cacheDuration) {
                this.updateBadge(tabId, cached.result);
                return;
            }

            console.log('Auto-scanning:', url);

            // Call the quick-scan API
            const response = await fetch(`${API_BASE_URL}/test/quick-scan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) {
                console.error('Scan API error:', response.status);
                return;
            }

            const result = await response.json();

            // Cache the result
            this.scanCache.set(url, {
                result: result,
                timestamp: Date.now()
            });

            // Update UI
            this.updateBadge(tabId, result);

            // Show notification if dangerous
            if (!result.is_safe && result.risk_score >= 0.4) {
                this.showThreatNotification(result, url, tabId);
            }

        } catch (error) {
            console.error('Auto-scan failed:', error);
        }
    }

    shouldScanUrl(url) {
        // Don't scan chrome:// urls, about: pages, etc.
        if (!url) return false;
        if (url.startsWith('chrome://')) return false;
        if (url.startsWith('about:')) return false;
        if (url.startsWith('chrome-extension://')) return false;
        if (url.startsWith('edge://')) return false;
        if (url === 'about:blank') return false;

        return true;
    }

    updateBadge(tabId, result) {
        let badgeText = '';
        let badgeColor = '#4CAF50'; // Green for safe

        if (!result.is_safe) {
            if (result.risk_score >= 0.7) {
                badgeText = '!!!';
                badgeColor = '#F44336'; // Red for high risk
            } else if (result.risk_score >= 0.4) {
                badgeText = '!';
                badgeColor = '#FF9800'; // Orange for medium risk
            }
        } else {
            badgeText = '✓';
            badgeColor = '#4CAF50'; // Green for safe
        }

        chrome.action.setBadgeText({ text: badgeText, tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: badgeColor, tabId: tabId });

        // Update title
        const title = result.is_safe
            ? `ScamCap: Safe (${Math.round(result.risk_score * 100)}% risk)`
            : `ScamCap: ${result.risk_level} Risk (${Math.round(result.risk_score * 100)}%)`;

        chrome.action.setTitle({ title: title, tabId: tabId });
    }

    async showThreatNotification(result, url, tabId) {
        const notificationId = `threat-${tabId}-${Date.now()}`;

        let iconUrl = chrome.runtime.getURL('assets/icons/icon-48.png');
        // Since we don't have icons, we'll use a basic notification without icon

        const domain = new URL(url).hostname;

        await chrome.notifications.create(notificationId, {
            type: 'basic',
            title: '⚠️ ScamCap Security Alert',
            message: `${result.risk_level} RISK DETECTED on ${domain}\nRisk Score: ${Math.round(result.risk_score * 100)}%`,
            priority: result.risk_score >= 0.7 ? 2 : 1,
            requireInteraction: result.risk_score >= 0.7
        });

        // Send message to content script to show warning
        try {
            await chrome.tabs.sendMessage(tabId, {
                type: 'SHOW_WARNING',
                result: result
            });
        } catch (error) {
            // Content script might not be loaded yet
            console.log('Could not send warning to content script:', error);
        }
    }

    handleMessage(message, sender, sendResponse) {
        switch (message.type) {
            case 'GET_SETTINGS':
                sendResponse({ enabled: this.isEnabled });
                break;

            case 'SAVE_SETTINGS':
                if (message.settings) {
                    this.isEnabled = message.settings.enabled !== false;
                }
                sendResponse({ success: true });
                break;

            case 'MANUAL_SCAN':
                if (sender.tab) {
                    this.autoScanPage(sender.tab.id, sender.tab.url)
                        .then(() => sendResponse({ success: true }))
                        .catch(error => sendResponse({ success: false, error: error.message }));
                }
                break;

            case 'GET_SCAN_RESULT':
                const cached = this.scanCache.get(message.url);
                if (cached) {
                    sendResponse({ success: true, result: cached.result });
                } else {
                    sendResponse({ success: false, message: 'No cached result' });
                }
                break;

            default:
                sendResponse({ success: false, error: 'Unknown message type' });
        }
    }
}

// Initialize the automatic scanner
const scamCapAuto = new ScamCapAuto();

console.log('ScamCap Auto service worker loaded');
