// ScamCap Popup - FINAL WORKING VERSION
console.log('Popup initializing...');

let currentTab = null;

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

    // Load stats
    await loadStats();

    // Load scan result
    await loadScanResult();

    // Setup scan button
    document.getElementById('scanButton').addEventListener('click', manualScan);
});

async function loadStats() {
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

    // Update risk level with proper text
    const riskLevelEl = document.getElementById('riskLevel');

    // Determine risk level based on score
    if (result.risk_score >= 0.7) {
        riskLevelEl.className = 'risk-level high';
        riskLevelEl.textContent = '⚠️ HIGH RISK';
        riskLevelEl.style.color = '#F44336';
    } else if (result.risk_score >= 0.4) {
        riskLevelEl.className = 'risk-level medium';
        riskLevelEl.textContent = '⚠️ MEDIUM RISK';
        riskLevelEl.style.color = '#FF9800';
    } else if (result.risk_score >= 0.2) {
        riskLevelEl.className = 'risk-level low';
        riskLevelEl.textContent = '✓ LOW RISK';
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
    .status-dot.danger { background-color: #F44336; }
`;
document.head.appendChild(styles);

console.log('Popup script loaded');
