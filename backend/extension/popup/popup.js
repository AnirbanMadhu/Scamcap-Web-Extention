// ScamCap Popup - FINAL WORKING VERSION
console.log('Popup initializing...');

let currentTab = null;
let currentThreshold = 0.7;

// Safe element getter to prevent crashes
function getElement(id) {
    const el = document.getElementById(id);
    if (!el) {
        console.warn(`Element with id '${id}' not found`);
    }
    return el;
}

// Safe query selector
function querySelector(selector) {
    const el = document.querySelector(selector);
    if (!el) {
        console.warn(`Element matching '${selector}' not found`);
    }
    return el;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded');

    try {
        // Get current tab
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        currentTab = tabs[0];

        if (!currentTab) {
            console.error('No active tab found');
            hideLoading();
            return;
        }

        // Display URL
        const pageUrlEl = getElement('pageUrl');
        if (pageUrlEl) {
            pageUrlEl.textContent = currentTab.url || 'Unknown URL';
        }

        // Load settings
        await loadSettings();

        // Load stats
        await loadStats();

        // Load scan result
        await loadScanResult();

        // Setup scan button
        const scanButton = getElement('scanButton');
        if (scanButton) {
            scanButton.addEventListener('click', manualScan);
        }

        // Setup threshold controls
        setupThresholdControls();
    } catch (error) {
        console.error('Initialization error:', error);
        hideLoading();
    }
});

async function loadSettings() {
    try {
        const result = await chrome.storage.local.get(['threshold']);
        if (result.threshold !== undefined) {
            currentThreshold = result.threshold;
        }
        const thresholdSlider = getElement('riskThreshold');
        const thresholdValue = getElement('thresholdValue');
        if (thresholdSlider) thresholdSlider.value = currentThreshold;
        if (thresholdValue) thresholdValue.textContent = currentThreshold.toFixed(1);
        console.log('Settings loaded:', { threshold: currentThreshold });
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function saveSettings() {
    try {
        await chrome.storage.local.set({ threshold: currentThreshold });
        console.log('Settings saved:', { threshold: currentThreshold });
    } catch (error) {
        console.error('Error saving settings:', error);
    }
}

function setupThresholdControls() {
    const slider = getElement('riskThreshold');
    const valueDisplay = getElement('thresholdValue');
    const decreaseBtn = getElement('decreaseThreshold');
    const increaseBtn = getElement('increaseThreshold');

    // Slider change
    if (slider) {
        slider.addEventListener('input', (e) => {
            currentThreshold = parseFloat(e.target.value);
            if (valueDisplay) valueDisplay.textContent = currentThreshold.toFixed(1);
            saveSettings();
        });
    }

    // Decrease button
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', () => {
            if (currentThreshold > 0.1) {
                currentThreshold = Math.max(0.1, Math.round((currentThreshold - 0.1) * 10) / 10);
                if (slider) slider.value = currentThreshold;
                if (valueDisplay) valueDisplay.textContent = currentThreshold.toFixed(1);
                saveSettings();
            }
        });
    }

    // Increase button
    if (increaseBtn) {
        increaseBtn.addEventListener('click', () => {
            if (currentThreshold < 1.0) {
                currentThreshold = Math.min(1.0, Math.round((currentThreshold + 0.1) * 10) / 10);
                if (slider) slider.value = currentThreshold;
                if (valueDisplay) valueDisplay.textContent = currentThreshold.toFixed(1);
                saveSettings();
            }
        });
    }
}

async function loadStats() {
    try {
        const response = await chrome.runtime.sendMessage({ type: 'GET_STATS' });

        if (response && response.success && response.stats) {
            console.log('Stats loaded:', response.stats);
            const threatsEl = getElement('threatsBlocked');
            const pagesEl = getElement('pagesScanned');
            const mfaEl = getElement('mfaTriggered');
            if (threatsEl) threatsEl.textContent = response.stats.threatsBlocked || 0;
            if (pagesEl) pagesEl.textContent = response.stats.pagesScanned || 0;
            if (mfaEl) mfaEl.textContent = response.stats.mfaTriggered || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadScanResult() {
    try {
        console.log('Requesting scan result for:', currentTab.url);

        const response = await chrome.runtime.sendMessage({
            type: 'GET_SCAN_RESULT',
            url: currentTab.url
        });

        if (response && response.success && response.result) {
            displayResult(response.result);
        } else {
            // Wait and try again
            setTimeout(async () => {
                const response2 = await chrome.runtime.sendMessage({
                    type: 'GET_SCAN_RESULT',
                    url: currentTab.url
                });

                if (response2 && response2.success && response2.result) {
                    displayResult(response2.result);
                } else {
                    showScanning();
                }
            }, 1500);
        }
    } catch (error) {
        console.error('Error loading result:', error);
        showScanning();
    }
}

function displayResult(result) {
    console.log('Displaying result:', result);

    hideLoading();

    // Update risk score
    const riskScorePercent = Math.round((result.risk_score || 0) * 100);
    const scoreValueEl = querySelector('.score-value');
    if (scoreValueEl) scoreValueEl.textContent = riskScorePercent;

    // Update risk level with proper text and styling
    const riskLevelEl = getElement('riskLevel');

    if (riskLevelEl) {
        // Clear existing classes
        riskLevelEl.className = 'risk-level';

        // Determine risk level based on score and level
        if (result.risk_level === 'CRITICAL') {
            riskLevelEl.className = 'risk-level critical';
            riskLevelEl.textContent = '🚨 CRITICAL THREAT';
            riskLevelEl.style.color = '#D32F2F';
            riskLevelEl.style.fontWeight = 'bold';
            riskLevelEl.style.fontSize = '16px';
        } else if (result.risk_level === 'HIGH') {
            riskLevelEl.className = 'risk-level high';
            riskLevelEl.textContent = '⚠️ HIGH RISK';
            riskLevelEl.style.color = '#F44336';
        } else if (result.risk_level === 'MEDIUM') {
            riskLevelEl.className = 'risk-level medium';
            riskLevelEl.textContent = '⚠️ MEDIUM RISK';
            riskLevelEl.style.color = '#FF9800';
        } else if (result.risk_level === 'LOW') {
            riskLevelEl.className = 'risk-level low';
            riskLevelEl.textContent = '⚠️ LOW RISK';
            riskLevelEl.style.color = '#FFC107';
        } else {
            riskLevelEl.className = 'risk-level safe';
            riskLevelEl.textContent = '✓ SAFE';
            riskLevelEl.style.color = '#4CAF50';
        }
    }

    // Update status
    const statusText = querySelector('.status-text');
    const statusDot = querySelector('.status-dot');

    if (result.is_safe) {
        if (statusText) statusText.textContent = 'Protected';
        if (statusDot) statusDot.className = 'status-dot active';
    } else {
        if (statusText) statusText.textContent = 'Threat Detected';
        if (statusDot) statusDot.className = 'status-dot danger';
    }

    // Show threat details if unsafe
    if (!result.is_safe && result.indicators && result.indicators.length > 0) {
        const threatDetails = getElement('threatDetails');
        const threatIndicators = getElement('threatIndicators');

        if (threatIndicators) {
            threatIndicators.innerHTML = '';
            result.indicators.forEach(indicator => {
                const div = document.createElement('div');
                div.className = 'threat-indicator';
                div.innerHTML = `⚠️ ${indicator}`;
                threatIndicators.appendChild(div);
            });
        }

        if (threatDetails) threatDetails.style.display = 'block';
    }
}

function showScanning() {
    hideLoading();
    const scoreValueEl = querySelector('.score-value');
    const riskLevelEl = getElement('riskLevel');
    if (scoreValueEl) scoreValueEl.textContent = '--';
    if (riskLevelEl) {
        riskLevelEl.textContent = 'Scanning...';
        riskLevelEl.className = 'risk-level';
    }
}

function showLoading() {
    const overlay = getElement('loadingOverlay');
    if (overlay) overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = getElement('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}

async function manualScan() {
    console.log('Manual scan triggered');
    showLoading();

    try {
        await chrome.runtime.sendMessage({ type: 'MANUAL_SCAN' });

        // Wait for scan and reload
        setTimeout(async () => {
            await loadScanResult();
            await loadStats();
        }, 1500);
    } catch (error) {
        console.error('Manual scan error:', error);
        hideLoading();
        alert('Scan failed. Backend may not be running at http://localhost:8000');
    }
}

// Add custom styles
const styles = document.createElement('style');
styles.textContent = `
    .threat-indicator {
        background: #ffebee;
        border-left: 3px solid #f44336;
        padding: 8px 12px;
        margin: 5px 0;
        font-size: 12px;
        border-radius: 4px;
    }
    .risk-level.safe { color: #4CAF50; font-weight: bold; }
    .risk-level.low { color: #FFC107; }
    .risk-level.medium { color: #FF9800; font-weight: bold; }
    .risk-level.high { color: #F44336; font-weight: bold; }
    .risk-level.critical {
        color: #D32F2F;
        font-weight: bold;
        font-size: 16px;
        text-shadow: 0 0 3px rgba(211, 47, 47, 0.3);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .status-dot.danger { background-color: #F44336; }
`;
document.head.appendChild(styles);

console.log('Popup script loaded');
