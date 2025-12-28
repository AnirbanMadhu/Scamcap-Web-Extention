// ScamCap Content Script - Simple Auto Version
// Displays warnings when threats are detected

console.log('ScamCap content script loaded');

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    try {
        if (message.type === 'SHOW_WARNING') {
            if (message.result) {
                showPageWarning(message.result);
            }
            sendResponse({ success: true });
        } else {
            sendResponse({ success: false, error: 'Unknown message type' });
        }
    } catch (error) {
        console.error('ScamCap content script error:', error);
        sendResponse({ success: false, error: error.message });
    }
    return true;
});

function showPageWarning(result) {
    try {
        // Validate result object
        if (!result || typeof result.risk_score === 'undefined') {
            console.warn('ScamCap: Invalid result object');
            return;
        }

        // Remove any existing warning
        const existingWarning = document.getElementById('scamcap-page-warning');
        if (existingWarning) {
            existingWarning.remove();
        }

        // Ensure indicators is an array
        const indicators = Array.isArray(result.indicators) ? result.indicators : ['Potential threat detected'];
        const message = result.message || 'Security Warning';

        // Create warning banner at top of page
        const warning = document.createElement('div');
        warning.id = 'scamcap-page-warning';
        warning.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: ${result.risk_score >= 0.7 ? '#F44336' : '#FF9800'};
            color: white;
            padding: 15px 20px;
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: slideDown 0.3s ease-out;
        `;

        const messageEl = document.createElement('div');
        messageEl.innerHTML = `
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 24px;">⚠️</span>
                <div>
                    <strong style="font-size: 16px;">${message}</strong>
                    <div style="font-size: 12px; margin-top: 4px; opacity: 0.9;">
                        ${indicators.join(' • ')}
                    </div>
                </div>
            </div>
        `;

    const closeBtn = document.createElement('button');
    closeBtn.textContent = '✕';
    closeBtn.style.cssText = `
        background: rgba(255,255,255,0.3);
        border: none;
        color: white;
        padding: 5px 10px;
        font-size: 18px;
        cursor: pointer;
        border-radius: 3px;
        margin-left: 20px;
    `;
    closeBtn.onmouseover = () => closeBtn.style.background = 'rgba(255,255,255,0.5)';
    closeBtn.onmouseout = () => closeBtn.style.background = 'rgba(255,255,255,0.3)';
    closeBtn.onclick = () => {
        if (warning && warning.parentNode) {
            warning.remove();
        }
    };

    warning.appendChild(messageEl);
    warning.appendChild(closeBtn);

    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideDown {
            from {
                transform: translateY(-100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
    `;
    if (document.head) {
        document.head.appendChild(style);
    }

    // Insert at the beginning of body
    if (document.body) {
        document.body.insertBefore(warning, document.body.firstChild);
    } else {
        // If body doesn't exist yet, wait for it
        document.addEventListener('DOMContentLoaded', () => {
            if (document.body) {
                document.body.insertBefore(warning, document.body.firstChild);
            }
        });
    }

    // Auto-hide after 10 seconds for medium risk
    if (result.risk_score < 0.7) {
        setTimeout(() => {
            if (warning && warning.parentNode) {
                warning.style.transition = 'opacity 0.5s';
                warning.style.opacity = '0';
                setTimeout(() => {
                    if (warning && warning.parentNode) {
                        warning.remove();
                    }
                }, 500);
            }
        }, 10000);
    }
  } catch (error) {
        console.error('ScamCap: Error showing warning:', error);
    }
}

// Initial page load - let background know we're ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('ScamCap: Page loaded, ready for scanning');
    });
} else {
    console.log('ScamCap: Page already loaded, ready for scanning');
}
