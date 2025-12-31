// ScamCap Background Service Worker - Production Ready
console.log('ScamCap service worker starting...');

// ============================================
// IMPORTANT: Configure your API URL here!
// ============================================
// For LOCAL DEVELOPMENT: http://localhost:8000/api/v1
// For PRODUCTION: Update to your deployed backend URL
// ============================================
const API_BASE_URL = 'https://scamcap-web-extention.vercel.app/api/v1';

const scanCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes cache
let stats = { threatsBlocked: 0, pagesScanned: 0, mfaTriggered: 0 };
let settings = {
    enabled: true,
    mfaEnabled: false,
    riskThreshold: 0.7,
    notificationsEnabled: true
};

// Load stats from storage
chrome.storage.local.get(['stats', 'settings'], (result) => {
    if (result.stats) {
        stats = result.stats;
        console.log('Loaded stats:', stats);
    }
    if (result.settings) {
        settings = { ...settings, ...result.settings };
        console.log('Loaded settings:', settings);
    }
});

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    try {
        if (changeInfo.status === 'complete' && tab.url && shouldScanUrl(tab.url)) {
            console.log('✅ Tab loaded, scanning:', tab.url);
            scanPage(tabId, tab.url);
        }
    } catch (error) {
        console.error('Error in tab update listener:', error);
    }
});

// Listen for tab activation
chrome.tabs.onActivated.addListener(async (activeInfo) => {
    try {
        const tab = await chrome.tabs.get(activeInfo.tabId);
        if (tab.url && shouldScanUrl(tab.url)) {
            console.log('✅ Tab activated, scanning:', tab.url);
            scanPage(activeInfo.tabId, tab.url);
        }
    } catch (error) {
        console.error('Error getting tab:', error);
    }
});

// Listen for messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('📩 Message received:', message.type);

    try {
        if (message.type === 'GET_SCAN_RESULT') {
            const cached = scanCache.get(message.url);
            if (cached) {
                console.log('✅ Returning cached result for:', message.url);
                sendResponse({ success: true, result: cached });
            } else {
                console.log('⏳ No cached result for:', message.url);
                sendResponse({ success: false, message: 'Scanning...' });
            }
            return true;
        }

        if (message.type === 'GET_STATS') {
            console.log('📊 Returning stats:', stats);
            sendResponse({ success: true, stats: stats });
            return true;
        }

        if (message.type === 'GET_SETTINGS') {
            console.log('⚙️ Returning settings:', settings);
            sendResponse(settings);
            return true;
        }

        if (message.type === 'SAVE_SETTINGS') {
            if (message.settings) {
                settings = { ...settings, ...message.settings };
                chrome.storage.local.set({ settings: settings }, () => {
                    console.log('💾 Settings saved:', settings);
                });
            }
            sendResponse({ success: true });
            return true;
        }

        if (message.type === 'ANALYZE_CURRENT_PAGE') {
            const tabId = message.tabId;
            if (tabId) {
                chrome.tabs.get(tabId, (tab) => {
                    if (chrome.runtime.lastError) {
                        sendResponse({ success: false, error: chrome.runtime.lastError.message });
                        return;
                    }
                    const cached = scanCache.get(tab.url);
                    if (cached) {
                        sendResponse({ success: true, data: cached });
                    } else {
                        scanPage(tabId, tab.url).then(() => {
                            const result = scanCache.get(tab.url);
                            sendResponse({ success: true, data: result || { risk_score: 0, is_phishing: false } });
                        }).catch((error) => {
                            sendResponse({ success: false, error: error.message });
                        });
                    }
                });
            } else {
                sendResponse({ success: false, error: 'No tab ID provided' });
            }
            return true;
        }

        if (message.type === 'MANUAL_SCAN') {
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                if (chrome.runtime.lastError) {
                    sendResponse({ success: false, error: chrome.runtime.lastError.message });
                    return;
                }
                if (tabs[0]) {
                    console.log('🔍 Manual scan requested');
                    scanPage(tabs[0].id, tabs[0].url).then(() => {
                        sendResponse({ success: true });
                    }).catch((error) => {
                        sendResponse({ success: false, error: error.message });
                    });
                } else {
                    sendResponse({ success: false, error: 'No active tab' });
                }
            });
            return true;
        }

        sendResponse({ success: false, error: 'Unknown message type' });
    } catch (error) {
        console.error('❌ Message handler error:', error);
        sendResponse({ success: false, error: error.message });
    }
    return true;
});

function shouldScanUrl(url) {
    if (!url) return false;
    if (url.startsWith('chrome://')) return false;
    if (url.startsWith('about:')) return false;
    if (url.startsWith('chrome-extension://')) return false;
    if (url.startsWith('edge://')) return false;
    return true;
}

async function scanPage(tabId, url) {
    try {
        // Check if protection is enabled
        if (!settings.enabled) {
            console.log('⏸️ Protection disabled, skipping scan');
            return;
        }

        console.log('🔍 Scanning URL:', url);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

        const response = await fetch(`${API_BASE_URL}/test/quick-scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            console.error('❌ API error:', response.status);
            updateBadge(tabId, { is_safe: true, risk_score: 0, risk_level: 'ERROR' });
            return;
        }

        const result = await response.json();
        console.log('✅ Scan result:', result);

        // Update stats
        stats.pagesScanned++;
        if (!result.is_safe) {
            stats.threatsBlocked++;
        }
        saveStats();

        // Cache result
        scanCache.set(url, result);

        // Update badge
        updateBadge(tabId, result);

        // Show notification if dangerous
        if (!result.is_safe && result.risk_score >= 0.4) {
            showNotification(result, url);

            // Send message to content script
            try {
                await chrome.tabs.sendMessage(tabId, {
                    type: 'SHOW_WARNING',
                    result: result
                });
            } catch (e) {
                console.log('ℹ️ Could not send to content script (page may be loading)');
            }
        }

    } catch (error) {
        console.error('❌ Scan failed:', error);
        updateBadge(tabId, { is_safe: true, risk_score: 0, risk_level: 'ERROR' });
    }
}

function updateBadge(tabId, result) {
    let badgeText = '';
    let badgeColor = '#4CAF50';

    if (!result.is_safe) {
        if (result.risk_score >= 0.7) {
            badgeText = '!!!';
            badgeColor = '#F44336';
        } else if (result.risk_score >= 0.4) {
            badgeText = '!';
            badgeColor = '#FF9800';
        }
    } else {
        badgeText = '✓';
        badgeColor = '#4CAF50';
    }

    chrome.action.setBadgeText({ text: badgeText, tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: badgeColor, tabId: tabId });

    const title = result.is_safe
        ? `ScamCap: Safe (${Math.round(result.risk_score * 100)}% risk)`
        : `ScamCap: ${result.risk_level} Risk (${Math.round(result.risk_score * 100)}%)`;

    chrome.action.setTitle({ title: title, tabId: tabId });

    console.log('🎯 Badge updated:', badgeText, badgeColor);
}

function showNotification(result, url) {
    const domain = new URL(url).hostname;

    chrome.notifications.create({
        type: 'basic',
        title: '⚠️ ScamCap Security Alert',
        message: `${result.risk_level} RISK on ${domain}\nRisk Score: ${Math.round(result.risk_score * 100)}%`,
        priority: result.risk_score >= 0.7 ? 2 : 1,
        requireInteraction: result.risk_score >= 0.7
    });

    console.log('🔔 Notification shown');
}

function saveStats() {
    chrome.storage.local.set({ stats: stats }, () => {
        console.log('💾 Stats saved:', stats);
    });
}

console.log('✅ ScamCap service worker loaded successfully');
