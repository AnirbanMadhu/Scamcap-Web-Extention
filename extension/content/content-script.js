// ScamCap Content Script - Main
// Monitors webpage content and coordinates security scans

class ScamCapContentScript {
    constructor() {
        this.isEnabled = true;
        this.scanInProgress = false;
        this.lastScanTime = 0;
        this.scanCooldown = 5000; // 5 seconds between scans
        
        this.observer = null;
        this.mediaObserver = null;
        
        this.initialize();
    }

    async initialize() {
        console.log('ScamCap content script initializing...');
        
        // Get settings from background
        const settings = await this.getSettings();
        this.isEnabled = settings.enabled !== false;
        
        if (this.isEnabled) {
            this.startMonitoring();
            this.scanCurrentPage();
        }
        
        // Listen for messages from background script
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Keep channel open for async response
        });
    }

    async getSettings() {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({ type: 'GET_SETTINGS' }, (response) => {
                resolve(response || {});
            });
        });
    }

    handleMessage(message, sender, sendResponse) {
        switch (message.type) {
            case 'SCAN_PAGE':
                this.scanCurrentPage().then(() => {
                    sendResponse({ success: true });
                });
                break;

            case 'QUICK_SCAN':
                this.performQuickScan().then((result) => {
                    sendResponse(result);
                });
                break;

            case 'TOGGLE_PROTECTION':
                this.isEnabled = message.enabled;
                if (this.isEnabled) {
                    this.startMonitoring();
                } else {
                    this.stopMonitoring();
                }
                sendResponse({ success: true });
                break;

            default:
                sendResponse({ success: false, error: 'Unknown message type' });
        }
    }

    startMonitoring() {
        console.log('Starting ScamCap monitoring...');
        
        // Monitor DOM changes
        this.observer = new MutationObserver((mutations) => {
            this.handleDOMChanges(mutations);
        });
        
        this.observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['src', 'href']
        });

        // Monitor media uploads
        this.startMediaMonitoring();
        
        // Monitor form submissions
        this.monitorForms();
        
        // Monitor downloads
        this.monitorDownloads();
    }

    stopMonitoring() {
        console.log('Stopping ScamCap monitoring...');
        
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
        
        if (this.mediaObserver) {
            this.mediaObserver.disconnect();
            this.mediaObserver = null;
        }
    }

    async scanCurrentPage() {
        if (this.scanInProgress || Date.now() - this.lastScanTime < this.scanCooldown) {
            return;
        }

        this.scanInProgress = true;
        this.lastScanTime = Date.now();

        try {
            console.log('Scanning current page for threats...');
            
            // Collect page data
            const pageData = this.collectPageData();
            
            // Analyze for phishing
            const phishingResult = await this.analyzePhishing(pageData);
            
            if (phishingResult.success && phishingResult.data.is_phishing) {
                await this.handleThreatDetected({
                    threat_type: 'phishing',
                    risk_score: phishingResult.data.risk_score,
                    confidence: phishingResult.data.confidence,
                    details: phishingResult.data,
                    url: window.location.href
                });
            }
            
            // Scan for suspicious media
            await this.scanPageMedia();
            
            console.log('Page scan completed');
            
        } catch (error) {
            console.error('Page scan failed:', error);
        } finally {
            this.scanInProgress = false;
        }
    }

    collectPageData() {
        const pageData = {
            url: window.location.href,
            title: document.title,
            content: this.extractPageText(),
            links: this.extractLinks(),
            forms: this.extractForms(),
            metadata: this.extractMetadata()
        };

        return pageData;
    }

    extractPageText() {
        // Extract visible text content
        const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, div, a');
        const textContent = Array.from(textElements)
            .map(el => el.textContent.trim())
            .filter(text => text.length > 0)
            .join(' ');
        
        return textContent.substring(0, 5000); // Limit to 5KB
    }

    extractLinks() {
        const links = Array.from(document.querySelectorAll('a[href]'))
            .map(link => ({
                href: link.href,
                text: link.textContent.trim(),
                rel: link.rel,
                target: link.target
            }))
            .slice(0, 50); // Limit to 50 links
        
        return links;
    }

    extractForms() {
        const forms = Array.from(document.querySelectorAll('form'))
            .map(form => ({
                action: form.action,
                method: form.method,
                inputs: Array.from(form.querySelectorAll('input'))
                    .map(input => ({
                        type: input.type,
                        name: input.name,
                        placeholder: input.placeholder
                    }))
            }))
            .slice(0, 10); // Limit to 10 forms
        
        return forms;
    }

    extractMetadata() {
        const metadata = {};
        
        // Extract meta tags
        const metaTags = document.querySelectorAll('meta');
        metaTags.forEach(meta => {
            const name = meta.name || meta.property;
            const content = meta.content;
            if (name && content) {
                metadata[name] = content;
            }
        });

        // Extract page language
        metadata.language = document.documentElement.lang || 'unknown';
        
        // Check for HTTPS
        metadata.isHTTPS = window.location.protocol === 'https:';
        
        return metadata;
    }

    async analyzePhishing(pageData) {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({
                type: 'ANALYZE_PHISHING',
                url: pageData.url,
                content: pageData.content,
                headers: null // Headers would need to be collected differently
            }, (response) => {
                resolve(response || { success: false });
            });
        });
    }

    async scanPageMedia() {
        const images = document.querySelectorAll('img');
        const videos = document.querySelectorAll('video');
        
        // Scan suspicious images (those loaded via data URLs or suspicious domains)
        for (const img of images) {
            if (this.isSuspiciousMediaSource(img.src)) {
                await this.analyzeImageForDeepfake(img);
            }
        }

        // Scan videos
        for (const video of videos) {
            if (this.isSuspiciousMediaSource(video.src)) {
                await this.analyzeVideoForDeepfake(video);
            }
        }
    }

    isSuspiciousMediaSource(src) {
        if (!src) return false;
        
        // Check for data URLs (base64 encoded media)
        if (src.startsWith('data:')) return true;
        
        // Check for suspicious domains (simplified)
        const suspiciousDomains = [
            'tempfileupload', 'anonymousfiles', 'filebin',
            'transfersh', 'gofile', 'filedropper'
        ];
        
        return suspiciousDomains.some(domain => src.includes(domain));
    }

    async analyzeImageForDeepfake(imgElement) {
        try {
            // Convert image to blob for analysis
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = imgElement.naturalWidth;
            canvas.height = imgElement.naturalHeight;
            ctx.drawImage(imgElement, 0, 0);
            
            canvas.toBlob(async (blob) => {
                if (blob && blob.size < 10 * 1024 * 1024) { // Max 10MB
                    const result = await this.analyzeDeepfake(blob, 'image');
                    
                    if (result.success && result.data.is_deepfake) {
                        await this.handleThreatDetected({
                            threat_type: 'deepfake',
                            risk_score: result.data.risk_score,
                            confidence: result.data.confidence,
                            details: result.data,
                            element: imgElement
                        });
                    }
                }
            });
            
        } catch (error) {
            console.error('Image analysis failed:', error);
        }
    }

    async analyzeVideoForDeepfake(videoElement) {
        try {
            // For videos, we'd need to extract frames
            // This is a simplified version
            if (videoElement.src && !videoElement.src.startsWith('blob:')) {
                // Could fetch and analyze the video file
                console.log('Video deepfake analysis not implemented for external sources');
            }
        } catch (error) {
            console.error('Video analysis failed:', error);
        }
    }

    async analyzeDeepfake(file, fileType) {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({
                type: 'ANALYZE_DEEPFAKE',
                file: file,
                fileType: fileType
            }, (response) => {
                resolve(response || { success: false });
            });
        });
    }

    async handleThreatDetected(threatData) {
        console.warn('Threat detected:', threatData);
        
        // Send to background for processing
        chrome.runtime.sendMessage({
            type: 'THREAT_DETECTED',
            threatData: threatData
        });

        // Check if MFA is needed
        if (threatData.risk_score >= 0.7) {
            chrome.runtime.sendMessage({
                type: 'TRIGGER_MFA',
                riskScore: threatData.risk_score,
                threatType: threatData.threat_type
            });
        }

        // Highlight suspicious elements
        if (threatData.element) {
            this.highlightSuspiciousElement(threatData.element);
        }
    }

    highlightSuspiciousElement(element) {
        element.style.border = '3px solid red';
        element.style.boxShadow = '0 0 10px red';
        element.title = 'ScamCap: Potential deepfake detected';
        
        // Add warning overlay
        const warning = document.createElement('div');
        warning.style.cssText = `
            position: absolute;
            background: rgba(255, 0, 0, 0.9);
            color: white;
            padding: 5px;
            font-size: 12px;
            z-index: 1000;
            border-radius: 3px;
        `;
        warning.textContent = '⚠️ Suspicious Media';
        
        const rect = element.getBoundingClientRect();
        warning.style.top = (rect.top + window.scrollY) + 'px';
        warning.style.left = (rect.left + window.scrollX) + 'px';
        
        document.body.appendChild(warning);
        
        // Remove warning after 5 seconds
        setTimeout(() => {
            warning.remove();
        }, 5000);
    }

    handleDOMChanges(mutations) {
        let shouldScan = false;
        
        mutations.forEach(mutation => {
            // Check for new links or forms
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'A' || node.tagName === 'FORM' || 
                            node.querySelector && (node.querySelector('a') || node.querySelector('form'))) {
                            shouldScan = true;
                        }
                    }
                });
            }
            
            // Check for src/href changes
            if (mutation.type === 'attributes') {
                shouldScan = true;
            }
        });

        if (shouldScan && !this.scanInProgress) {
            // Debounce scanning
            clearTimeout(this.scanTimeout);
            this.scanTimeout = setTimeout(() => {
                this.scanCurrentPage();
            }, 1000);
        }
    }

    startMediaMonitoring() {
        // Monitor file inputs
        document.addEventListener('change', (event) => {
            if (event.target.type === 'file') {
                this.handleFileUpload(event.target);
            }
        });

        // Monitor drag and drop
        document.addEventListener('drop', (event) => {
            if (event.dataTransfer && event.dataTransfer.files) {
                Array.from(event.dataTransfer.files).forEach(file => {
                    this.handleFileUpload({ files: [file] });
                });
            }
        });
    }

    async handleFileUpload(fileInput) {
        if (!fileInput.files || fileInput.files.length === 0) return;

        for (const file of fileInput.files) {
            if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
                if (file.size < 100 * 1024 * 1024) { // Max 100MB
                    const result = await this.analyzeDeepfake(file, file.type);
                    
                    if (result.success && result.data.is_deepfake) {
                        await this.handleThreatDetected({
                            threat_type: 'deepfake',
                            risk_score: result.data.risk_score,
                            confidence: result.data.confidence,
                            details: result.data,
                            filename: file.name
                        });
                    }
                }
            }
        }
    }

    monitorForms() {
        document.addEventListener('submit', (event) => {
            const form = event.target;
            if (form.tagName === 'FORM') {
                this.analyzeFormSubmission(form);
            }
        });
    }

    async analyzeFormSubmission(form) {
        // Check if form is suspicious (asking for sensitive info)
        const inputs = form.querySelectorAll('input');
        const suspiciousFields = ['password', 'ssn', 'social security', 'credit card', 'cvv'];
        
        let suspiciousScore = 0;
        inputs.forEach(input => {
            const fieldName = (input.name + ' ' + input.placeholder).toLowerCase();
            suspiciousFields.forEach(field => {
                if (fieldName.includes(field)) {
                    suspiciousScore += 0.2;
                }
            });
        });

        if (suspiciousScore > 0.4) {
            await this.handleThreatDetected({
                threat_type: 'phishing',
                risk_score: Math.min(suspiciousScore, 1.0),
                confidence: 0.8,
                details: { form_analysis: 'Suspicious form detected' },
                element: form
            });
        }
    }

    monitorDownloads() {
        // Monitor download links
        document.addEventListener('click', (event) => {
            const link = event.target.closest('a');
            if (link && link.href) {
                const url = new URL(link.href);
                const filename = url.pathname.split('/').pop();
                
                // Check for suspicious file extensions
                const suspiciousExtensions = [
                    '.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs', '.js'
                ];
                
                if (suspiciousExtensions.some(ext => filename.toLowerCase().endsWith(ext))) {
                    event.preventDefault();
                    this.showDownloadWarning(link.href, filename);
                }
            }
        });
    }

    showDownloadWarning(url, filename) {
        const proceed = confirm(
            `ScamCap Warning: You're about to download "${filename}" which could be potentially harmful.\n\n` +
            `Only proceed if you trust the source.\n\n` +
            `Click OK to continue or Cancel to stop the download.`
        );

        if (proceed) {
            window.location.href = url;
        }
    }

    async performQuickScan() {
        console.log('Performing quick scan...');
        
        try {
            await this.scanCurrentPage();
            
            return {
                success: true,
                message: 'Quick scan completed',
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Initialize content script when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ScamCapContentScript();
    });
} else {
    new ScamCapContentScript();
}

console.log('ScamCap content script loaded');
