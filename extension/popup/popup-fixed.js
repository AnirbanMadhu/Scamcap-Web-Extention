// ScamCap Popup - FIXED VERSION
console.log('Popup initializing...');

let currentTab = null;
let currentResult = null;

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

    // Try to get scan result
    await loadScanResult();

    // Setup scan button
    document.getElementById('scanButton').addEventListener('click', manualScan);
});

async function loadScanResult() {
    try {
        console.log('Requesting scan result for:', currentTab.url);

        const response = await chrome.runtime.sendMessage({
            type: 'GET_SCAN_RESULT',
            url: currentTab.url
        });

        console.log('Response:', response);

        if (response && response.success && response.result) {
            displayResult(response.result);
        } else {
            // No result yet, wait a bit and try again
            setTimeout(async () => {
                const response2 = await chrome.runtime.sendMessage({
                    type: 'GET_SCAN_RESULT',
                    url: currentTab.url
                });

                if (response2 && response2.success && response2.result) {
                    displayResult(response2.result);
                } else {
                    showNoResult();
                }
            }, 2000);
        }
    } catch (error) {
        console.error('Error loading result:', error);
        showNoResult();
    }
}

function displayResult(result) {
    console.log('Displaying result:', result);
    currentResult = result;

    hideLoading();

    // Update risk score
    document.querySelector('.score-value').textContent = Math.round(result.risk_score * 100);

    // Update risk level
    const riskLevelEl = document.getElementById('riskLevel');
    riskLevelEl.textContent = result.risk_level;

    // Set color based on risk
    if (!result.is_safe) {
        if (result.risk_score >= 0.7) {
            riskLevelEl.className = 'risk-level high';
            riskLevelEl.textContent = 'HIGH RISK';
        } else if (result.risk_score >= 0.4) {
            riskLevelEl.className = 'risk-level medium';
            riskLevelEl.textContent = 'MEDIUM RISK';
        } else {
            riskLevelEl.className = 'risk-level low';
            riskLevelEl.textContent = 'LOW RISK';
        }
    } else {
        riskLevelEl.className = 'risk-level safe';
        riskLevelEl.textContent = 'SAFE';
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

function showNoResult() {
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

        // Wait for scan to complete
        setTimeout(async () => {
            await loadScanResult();
        }, 2000);
    } catch (error) {
        console.error('Manual scan error:', error);
        hideLoading();
        alert('Scan failed. Make sure the backend is running at http://localhost:8000');
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
    .risk-level.safe { color: #4CAF50; }
    .risk-level.low { color: #FFC107; }
    .risk-level.medium { color: #FF9800; }
    .risk-level.high { color: #F44336; font-weight: bold; }
    .status-dot.danger { background-color: #F44336; }
`;
document.head.appendChild(styles);

console.log('Popup script loaded');
