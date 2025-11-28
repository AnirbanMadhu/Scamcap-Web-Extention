// ScamCap Popup JavaScript
// Manages the extension popup interface and user interactions

class ScamCapPopup {
    constructor() {
        this.currentTab = null;
        this.settings = {};
        this.stats = {
            threatsBlocked: 0,
            pagesScanned: 0,
            mfaTriggered: 0
        };
        
        this.initialize();
    }

    async initialize() {
        console.log('Initializing ScamCap popup...');
        
        // Get current tab
        await this.getCurrentTab();
        
        // Load settings and stats
        await this.loadSettings();
        await this.loadStats();
        
        // Update UI
        this.updateUI();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Perform initial page analysis
        this.analyzeCurrentPage();
    }

    async getCurrentTab() {
        try {
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            this.currentTab = tabs[0];
            
            if (this.currentTab) {
                document.getElementById('pageUrl').textContent = this.currentTab.url;
            }
        } catch (error) {
            console.error('Failed to get current tab:', error);
        }
    }

    async loadSettings() {
        try {
            const response = await this.sendMessage({ type: 'GET_SETTINGS' });
            this.settings = response || {};
            
            // Set default values
            this.settings.enabled = this.settings.enabled !== false;
            this.settings.mfaEnabled = this.settings.mfaEnabled || false;
            this.settings.riskThreshold = this.settings.riskThreshold || 0.7;
            
        } catch (error) {
            console.error('Failed to load settings:', error);
            this.settings = {
                enabled: true,
                mfaEnabled: false,
                riskThreshold: 0.7
            };
        }
    }

    async loadStats() {
        try {
            // Load stats from storage
            const result = await chrome.storage.local.get([
                'threatsBlocked', 'pagesScanned', 'mfaTriggered'
            ]);
            
            this.stats = {
                threatsBlocked: result.threatsBlocked || 0,
                pagesScanned: result.pagesScanned || 0,
                mfaTriggered: result.mfaTriggered || 0
            };
            
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    updateUI() {
        // Update status indicator
        const statusIndicator = document.getElementById('statusIndicator');
        const statusDot = statusIndicator.querySelector('.status-dot');
        const statusText = statusIndicator.querySelector('.status-text');
        
        if (this.settings.enabled) {
            statusDot.className = 'status-dot active';
            statusText.textContent = 'Protected';
        } else {
            statusDot.className = 'status-dot inactive';
            statusText.textContent = 'Disabled';
        }

        // Update settings checkboxes
        document.getElementById('enableProtection').checked = this.settings.enabled;
        document.getElementById('enableMFA').checked = this.settings.mfaEnabled;
        
        // Update risk threshold
        const thresholdSlider = document.getElementById('riskThreshold');
        const thresholdValue = document.getElementById('thresholdValue');
        thresholdSlider.value = this.settings.riskThreshold;
        thresholdValue.textContent = this.settings.riskThreshold.toFixed(1);
        
        // Update stats
        document.getElementById('threatsBlocked').textContent = this.stats.threatsBlocked;
        document.getElementById('pagesScanned').textContent = this.stats.pagesScanned;
        document.getElementById('mfaTriggered').textContent = this.stats.mfaTriggered;
    }

    setupEventListeners() {
        // Scan button
        document.getElementById('scanButton').addEventListener('click', () => {
            this.scanCurrentPage();
        });

        // Settings checkboxes
        document.getElementById('enableProtection').addEventListener('change', (e) => {
            this.updateSetting('enabled', e.target.checked);
        });

        document.getElementById('enableMFA').addEventListener('change', (e) => {
            this.updateSetting('mfaEnabled', e.target.checked);
        });

        // Risk threshold slider
        document.getElementById('riskThreshold').addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            document.getElementById('thresholdValue').textContent = value.toFixed(1);
            this.updateSetting('riskThreshold', value);
        });

        // Footer buttons
        document.getElementById('openOptions').addEventListener('click', () => {
            chrome.runtime.openOptionsPage();
        });

        document.getElementById('viewHistory').addEventListener('click', () => {
            chrome.tabs.create({ url: chrome.runtime.getURL('popup/history.html') });
        });

        document.getElementById('reportIssue').addEventListener('click', () => {
            chrome.tabs.create({ url: 'https://github.com/scamcap/extension/issues' });
        });
    }

    async updateSetting(key, value) {
        try {
            this.settings[key] = value;
            
            await this.sendMessage({
                type: 'SAVE_SETTINGS',
                settings: this.settings
            });
            
            this.updateUI();
            
        } catch (error) {
            console.error('Failed to update setting:', error);
        }
    }

    async scanCurrentPage() {
        if (!this.currentTab) {
            this.showError('No active tab found');
            return;
        }

        const scanButton = document.getElementById('scanButton');
        const buttonText = scanButton.querySelector('.button-text');
        const originalText = buttonText.textContent;
        
        try {
            // Show loading state
            this.showLoading();
            scanButton.disabled = true;
            buttonText.textContent = 'Scanning...';

            // Send scan message to content script
            const result = await chrome.tabs.sendMessage(this.currentTab.id, {
                type: 'QUICK_SCAN'
            });

            if (result && result.success) {
                // Update stats
                await this.incrementStat('pagesScanned');
                
                // Show scan result
                this.showScanResult({
                    success: true,
                    message: 'Page scan completed successfully'
                });
            } else {
                this.showError('Scan failed: ' + (result?.error || 'Unknown error'));
            }

        } catch (error) {
            console.error('Scan failed:', error);
            this.showError('Failed to scan page: ' + error.message);
        } finally {
            this.hideLoading();
            scanButton.disabled = false;
            buttonText.textContent = originalText;
        }
    }

    async analyzeCurrentPage() {
        if (!this.currentTab || !this.settings.enabled) {
            return;
        }

        try {
            // Get current page analysis from background
            const result = await this.sendMessage({
                type: 'ANALYZE_CURRENT_PAGE',
                tabId: this.currentTab.id
            });

            if (result && result.success) {
                this.displayPageAnalysis(result.data);
            }

        } catch (error) {
            console.error('Failed to analyze current page:', error);
        }
    }

    displayPageAnalysis(analysisData) {
        const riskScore = analysisData.risk_score || 0;
        const isPhishing = analysisData.is_phishing || false;
        
        // Update risk score display
        const scoreValue = document.querySelector('.score-value');
        const riskLevel = document.getElementById('riskLevel');
        
        scoreValue.textContent = Math.round(riskScore * 100);
        
        // Update risk level
        if (riskScore >= 0.8) {
            riskLevel.textContent = 'High Risk';
            riskLevel.className = 'risk-level high';
        } else if (riskScore >= 0.5) {
            riskLevel.textContent = 'Medium Risk';
            riskLevel.className = 'risk-level medium';
        } else {
            riskLevel.textContent = 'Safe';
            riskLevel.className = 'risk-level';
        }

        // Show threat details if phishing detected
        if (isPhishing && analysisData.threat_indicators) {
            this.showThreatDetails(analysisData);
        }
    }

    showThreatDetails(threatData) {
        const threatDetails = document.getElementById('threatDetails');
        const threatIndicators = document.getElementById('threatIndicators');
        const recommendations = document.getElementById('recommendations');
        
        // Show threat indicators
        threatIndicators.innerHTML = '';
        if (threatData.threat_indicators) {
            threatData.threat_indicators.forEach(indicator => {
                const span = document.createElement('span');
                span.className = 'threat-indicator';
                span.textContent = indicator;
                threatIndicators.appendChild(span);
            });
        }

        // Show recommendations
        recommendations.innerHTML = '';
        if (threatData.safe_alternatives) {
            const recList = document.createElement('ul');
            recList.style.fontSize = '12px';
            recList.style.marginTop = '10px';
            
            threatData.safe_alternatives.forEach(alt => {
                const li = document.createElement('li');
                li.textContent = alt;
                recList.appendChild(li);
            });
            
            const title = document.createElement('div');
            title.textContent = 'Recommended alternatives:';
            title.style.fontWeight = 'bold';
            title.style.fontSize = '12px';
            
            recommendations.appendChild(title);
            recommendations.appendChild(recList);
        }

        threatDetails.style.display = 'block';
        threatDetails.classList.add('fade-in');
    }

    async loadRecentThreats() {
        try {
            // Load recent threats from storage
            const result = await chrome.storage.local.get('recentThreats');
            const threats = result.recentThreats || [];
            
            const threatList = document.getElementById('threatList');
            threatList.innerHTML = '';
            
            if (threats.length === 0) {
                threatList.innerHTML = '<div class="no-threats">No threats detected recently</div>';
                return;
            }

            threats.slice(0, 5).forEach(threat => {
                const threatItem = document.createElement('div');
                threatItem.className = `threat-item ${threat.type}`;
                
                const title = document.createElement('div');
                title.className = 'threat-title';
                title.textContent = `${threat.type.toUpperCase()} - Risk: ${Math.round(threat.risk_score * 100)}%`;
                
                const time = document.createElement('div');
                time.className = 'threat-time';
                time.textContent = this.formatTime(threat.timestamp);
                
                threatItem.appendChild(title);
                threatItem.appendChild(time);
                threatList.appendChild(threatItem);
            });

        } catch (error) {
            console.error('Failed to load recent threats:', error);
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            return `${Math.floor(diff / 60000)} min ago`;
        } else if (diff < 86400000) { // Less than 1 day
            return `${Math.floor(diff / 3600000)} hours ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    async incrementStat(statName) {
        try {
            this.stats[statName]++;
            await chrome.storage.local.set({ [statName]: this.stats[statName] });
            this.updateUI();
        } catch (error) {
            console.error('Failed to increment stat:', error);
        }
    }

    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    showError(message) {
        // Simple error display - in production you'd want a proper notification system
        console.error('ScamCap Error:', message);
        
        // You could show a toast notification here
        this.showToast('error', 'Error', message);
    }

    showScanResult(result) {
        if (result.success) {
            this.showToast('success', 'Scan Complete', result.message);
        } else {
            this.showToast('error', 'Scan Failed', result.message);
        }
    }

    showToast(type, title, message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        `;
        
        // Add to document
        document.body.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    async sendMessage(message) {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage(message, (response) => {
                resolve(response);
            });
        });
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ScamCapPopup();
});

// Add toast styles if not already present
const toastStyles = `
.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-radius: 6px;
    padding: 12px 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 1001;
    max-width: 280px;
    font-size: 12px;
    animation: slideIn 0.3s ease-out;
}

.toast.success {
    border-left: 4px solid #4caf50;
}

.toast.error {
    border-left: 4px solid #f44336;
}

.toast-title {
    font-weight: bold;
    margin-bottom: 4px;
}

.toast-message {
    color: #666;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
`;

// Inject toast styles
const styleSheet = document.createElement('style');
styleSheet.textContent = toastStyles;
document.head.appendChild(styleSheet);
