// ScamCap Background Service Worker - FINAL WORKING VERSION
console.log('ScamCap service worker starting...');

const API_BASE_URL = 'http://localhost:8000/api/v1';
const scanCache = new Map();
let stats = { threatsBlocked: 0, pagesScanned: 0, mfaTriggered: 0 };

// Load stats from storage
chrome.storage.local.get(['stats'], (result) => {
    if (result.stats) {
        stats = result.stats;
        console.log('Loaded stats:', stats);
    }
});

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && shouldScanUrl(tab.url)) {
        console.log('✅ Tab loaded, scanning:', tab.url);
        scanPage(tabId, tab.url);
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

    if (message.type === 'MANUAL_SCAN') {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                console.log('🔍 Manual scan requested');
                scanPage(tabs[0].id, tabs[0].url).then(() => {
                    sendResponse({ success: true });
                });
            }
        });
        return true;
    }

    sendResponse({ success: false });
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
        console.log('🔍 Scanning URL:', url);

        const response = await fetch(`${API_BASE_URL}/test/quick-scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

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
