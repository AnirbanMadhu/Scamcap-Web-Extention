// ScamCap Popup - Simple Auto Version

class ScamCapPopup {
    constructor() {
        this.currentTab = null;
        this.init();
    }

    async init() {
        // Get current tab
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        this.currentTab = tabs[0];

        if (this.currentTab) {
            document.getElementById('pageUrl').textContent = this.currentTab.url;

            // Get scan result from background
            chrome.runtime.sendMessage({
                type: 'GET_SCAN_RESULT',
                url: this.currentTab.url
            }, (response) => {
                if (response && response.success && response.result) {
                    this.displayResult(response.result);
                } else {
                    this.showLoading();
                }
            });
        }

        // Setup scan button
        document.getElementById('scanButton').addEventListener('click', () => {
            this.manualScan();
        });
    }

    displayResult(result) {
        // Hide loading
        document.getElementById('loadingOverlay').style.display = 'none';

        // Update risk score
        const scoreValue = document.querySelector('.score-value');
        scoreValue.textContent = Math.round(result.risk_score * 100);

        // Update risk level
        const riskLevel = document.getElementById('riskLevel');
        riskLevel.textContent = result.risk_level;

        if (!result.is_safe) {
            if (result.risk_score >= 0.7) {
                riskLevel.className = 'risk-level high';
                riskLevel.textContent = 'HIGH RISK';
            } else if (result.risk_score >= 0.4) {
                riskLevel.className = 'risk-level medium';
                riskLevel.textContent = 'MEDIUM RISK';
            } else {
                riskLevel.className = 'risk-level low';
                riskLevel.textContent = 'LOW RISK';
            }
        } else {
            riskLevel.className = 'risk-level safe';
            riskLevel.textContent = 'SAFE';
        }

        // Show threat details if not safe
        if (!result.is_safe && result.indicators) {
            const threatDetails = document.getElementById('threatDetails');
            const threatIndicators = document.getElementById('threatIndicators');

            threatIndicators.innerHTML = '';
            result.indicators.forEach(indicator => {
                const indicatorElem = document.createElement('div');
                indicatorElem.className = 'threat-indicator';
                indicatorElem.innerHTML = `⚠️ ${indicator}`;
                threatIndicators.appendChild(indicatorElem);
            });

            threatDetails.style.display = 'block';
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
    }

    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    async manualScan() {
        this.showLoading();

        chrome.runtime.sendMessage({
            type: 'MANUAL_SCAN'
        }, (response) => {
            if (response && response.success) {
                // Wait a moment for scan to complete
                setTimeout(() => {
                    chrome.runtime.sendMessage({
                        type: 'GET_SCAN_RESULT',
                        url: this.currentTab.url
                    }, (response) => {
                        this.hideLoading();
                        if (response && response.success && response.result) {
                            this.displayResult(response.result);
                        }
                    });
                }, 1000);
            } else {
                this.hideLoading();
                alert('Scan failed. Please try again.');
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ScamCapPopup();
});

// Add custom styles for threat indicators
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

    .risk-level.safe {
        color: #4CAF50;
    }

    .risk-level.low {
        color: #FFC107;
    }

    .risk-level.medium {
        color: #FF9800;
    }

    .risk-level.high {
        color: #F44336;
        font-weight: bold;
    }

    .status-dot.danger {
        background-color: #F44336;
    }
`;
document.head.appendChild(styles);
