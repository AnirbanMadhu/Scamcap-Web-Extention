// ScamCap Popup - FINAL WORKING VERSION
console.log('Popup initializing...');

let currentTab = null;
let currentThreshold = 0.7;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded');

    // Get current tab
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    currentTab = tabs[0];

    if (!currentTab) {
        console.error('No active tab found');
        hideLoading();
        return;
    }

    // Display URL
    document.getElementById('pageUrl').textContent = currentTab.url || 'Unknown URL';

    // Load settings
    await loadSettings();

    // Load stats
    await loadStats();

    // Load scan result
    await loadScanResult();

    // Setup scan button
    document.getElementById('scanButton').addEventListener('click', manualScan);

    // Setup threshold controls
    setupThresholdControls();
});

async function loadSettings() {
    try {
        const result = await chrome.storage.local.get(['threshold']);
        if (result.threshold !== undefined) {
            currentThreshold = result.threshold;
        }
        document.getElementById('riskThreshold').value = currentThreshold;
        document.getElementById('thresholdValue').textContent = currentThreshold;
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
    const slider = document.getElementById('riskThreshold');
    const valueDisplay = document.getElementById('thresholdValue');
    const decreaseBtn = document.getElementById('decreaseThreshold');
    const increaseBtn = document.getElementById('increaseThreshold');

    // Slider change
    slider.addEventListener('input', (e) => {
        currentThreshold = parseFloat(e.target.value);
        valueDisplay.textContent = currentThreshold;
        saveSettings();
    });

    // Decrease button
    decreaseBtn.addEventListener('click', () => {
        if (currentThreshold > 0.1) {
            currentThreshold = Math.max(0.1, currentThreshold - 0.1);
            slider.value = currentThreshold;
            valueDisplay.textContent = currentThreshold;
            saveSettings();
        }
    });

    // Increase button
    increaseBtn.addEventListener('click', () => {
        if (currentThreshold < 1.0) {
            currentThreshold = Math.min(1.0, currentThreshold + 0.1);
            slider.value = currentThreshold;
            valueDisplay.textContent = currentThreshold;
            saveSettings();
        }
    });
}
    try {
        const response = await chrome.runtime.sendMessage({ type: 'GET_STATS' });

        if (response && response.success && response.stats) {
            console.log('Stats loaded:', response.stats);
            document.getElementById('threatsBlocked').textContent = response.stats.threatsBlocked || 0;
            document.getElementById('pagesScanned').textContent = response.stats.pagesScanned || 0;
            document.getElementById('mfaTriggered').textContent = response.stats.mfaTriggered || 0;
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
    const riskScorePercent = Math.round(result.risk_score * 100);
    document.querySelector('.score-value').textContent = riskScorePercent;

    // Update risk level with proper text and styling
    const riskLevelEl = document.getElementById('riskLevel');

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

    // Update status
    const statusText = document.querySelector('.status-text');
    const statusDot = document.querySelector('.status-dot');

    if (result.is_safe) {
        statusText.textContent = 'Protected';
        statusDot.className = 'status-dot active';
    } else {
        statusText.textContent = 'Threat Detected';
        statusDot.className = 'status-dot danger';
    }

    // Show threat details if unsafe
    if (!result.is_safe && result.indicators && result.indicators.length > 0) {
        const threatDetails = document.getElementById('threatDetails');
        const threatIndicators = document.getElementById('threatIndicators');

        threatIndicators.innerHTML = '';
        result.indicators.forEach(indicator => {
            const div = document.createElement('div');
            div.className = 'threat-indicator';
            div.innerHTML = `⚠️ ${indicator}`;
            threatIndicators.appendChild(div);
        });

        threatDetails.style.display = 'block';
    }
}

function showScanning() {
    hideLoading();
    document.querySelector('.score-value').textContent = '--';
    document.getElementById('riskLevel').textContent = 'Scanning...';
    document.getElementById('riskLevel').className = 'risk-level';
}

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
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
