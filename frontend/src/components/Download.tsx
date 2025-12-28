'use client'

import { Download, Chrome, Globe, CheckCircle, X, ExternalLink } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function DownloadSection() {
  const [showInstructions, setShowInstructions] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [browser, setBrowser] = useState<'chrome' | 'edge' | 'firefox' | 'other'>('other')

  useEffect(() => {
    // Detect browser
    const userAgent = navigator.userAgent.toLowerCase()
    if (userAgent.includes('edg/')) {
      setBrowser('edge')
    } else if (userAgent.includes('chrome')) {
      setBrowser('chrome')
    } else if (userAgent.includes('firefox')) {
      setBrowser('firefox')
    }
  }, [])

  const getExtensionUrl = () => {
    switch (browser) {
      case 'chrome':
        return 'chrome://extensions/'
      case 'edge':
        return 'edge://extensions/'
      case 'firefox':
        return 'about:debugging#/runtime/this-firefox'
      default:
        return 'chrome://extensions/'
    }
  }

  const getBrowserName = () => {
    switch (browser) {
      case 'chrome':
        return 'Chrome'
      case 'edge':
        return 'Edge'
      case 'firefox':
        return 'Firefox'
      default:
        return 'your browser'
    }
  }

  const handleQuickInstall = async () => {
    setDownloading(true)
    
    try {
      // Step 1: Download the extension
      const response = await fetch('/api/download')
      if (!response.ok) throw new Error('Download failed')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'scamcap-extension.zip'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      // Step 2: Wait a moment then open extensions page
      setTimeout(() => {
        // Try to open the extensions page
        const extensionUrl = getExtensionUrl()
        const newWindow = window.open(extensionUrl, '_blank')
        
        // Show instructions
        setShowInstructions(true)
        setDownloading(false)
        
        // If popup was blocked, show message
        if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
          console.log('Popup blocked - showing instructions')
        }
      }, 1000)
      
    } catch (error) {
      console.error('Download error:', error)
      alert('Download failed. Please try again.')
      setDownloading(false)
    }
  }

  return (
    <section id="download" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-gradient-to-br from-primary-600 to-primary-800 rounded-3xl p-12 md:p-16 text-center text-white">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Stay Protected?
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Download Scamcap now and experience peace of mind while browsing the internet
          </p>

          <button
            onClick={handleQuickInstall}
            disabled={downloading}
            className="bg-white text-primary-600 px-8 py-4 rounded-lg hover:bg-slate-50 transition font-bold text-lg shadow-xl hover:shadow-2xl inline-flex items-center space-x-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="h-6 w-6" />
            <span>{downloading ? 'Preparing...' : 'Add to Your Browser'}</span>
          </button>

          <div className="mt-12 pt-12 border-t border-white/20">
            <p className="text-sm opacity-75 mb-6">Compatible with:</p>
            <div className="flex items-center justify-center space-x-8">
              <div className="flex flex-col items-center">
                <div className="bg-white/10 p-4 rounded-lg mb-2">
                  <Chrome className="h-8 w-8" />
                </div>
                <span className="text-sm">Chrome</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="bg-white/10 p-4 rounded-lg mb-2">
                  <Globe className="h-8 w-8" />
                </div>
                <span className="text-sm">Edge</span>
              </div>
              <div className="flex flex-col items-center">
                <div className="bg-white/10 p-4 rounded-lg mb-2">
                  <Globe className="h-8 w-8" />
                </div>
                <span className="text-sm">Firefox</span>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <a
              href="/docs/installation"
              className="text-white/90 hover:text-white underline"
            >
              Need help with installation? View our guide →
            </a>
          </div>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
            <div className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Free Forever</div>
            <p className="text-slate-600 dark:text-slate-300">No hidden costs or subscriptions</p>
          </div>
          <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
            <div className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Open Source</div>
            <p className="text-slate-600 dark:text-slate-300">Transparent and community-driven</p>
          </div>
          <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
            <div className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Regular Updates</div>
            <p className="text-slate-600 dark:text-slate-300">Always improving and evolving</p>
          </div>
        </div>
      </div>

      {/* Installation Instructions Modal */}
      {showInstructions && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-8 relative">
            <button
              onClick={() => setShowInstructions(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="h-6 w-6" />
            </button>

            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full mb-4">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                Almost There!
              </h3>
              <p className="text-slate-600 dark:text-slate-300">
                Complete these quick steps to activate Scamcap in {getBrowserName()}
              </p>
            </div>

            <div className="bg-primary-50 dark:bg-primary-900/20 p-6 rounded-xl mb-6 border border-primary-200 dark:border-primary-800">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-bold text-slate-900 dark:text-white">
                  Extension Page
                </h4>
                <button
                  onClick={() => window.open(getExtensionUrl(), '_blank')}
                  className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  <span>Open Now</span>
                  <ExternalLink className="h-4 w-4" />
                </button>
              </div>
              <p className="text-slate-600 dark:text-slate-300 text-sm mb-2">
                Click above to open your extensions page, or copy this URL:
              </p>
              <code className="block bg-white dark:bg-slate-900 px-3 py-2 rounded text-xs font-mono border border-slate-200 dark:border-slate-700">
                {getExtensionUrl()}
              </code>
            </div>

            <div className="space-y-4">
              <div className="flex items-start space-x-4 bg-slate-50 dark:bg-slate-900/50 p-4 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                  1
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-slate-900 dark:text-white mb-1 text-sm">
                    Extract ZIP File
                  </h4>
                  <p className="text-slate-600 dark:text-slate-300 text-sm">
                    Find the downloaded <code className="bg-slate-200 dark:bg-slate-700 px-1 rounded text-xs">scamcap-extension.zip</code> and extract it
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4 bg-slate-50 dark:bg-slate-900/50 p-4 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                  2
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-slate-900 dark:text-white mb-1 text-sm">
                    Enable Developer Mode
                  </h4>
                  <p className="text-slate-600 dark:text-slate-300 text-sm">
                    In the extensions page, toggle <strong>Developer mode</strong> ON (top-right corner)
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4 bg-slate-50 dark:bg-slate-900/50 p-4 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                  3
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-slate-900 dark:text-white mb-1 text-sm">
                    Load Extension
                  </h4>
                  <p className="text-slate-600 dark:text-slate-300 text-sm">
                    Click <strong>"Load unpacked"</strong> and select the <code className="bg-slate-200 dark:bg-slate-700 px-1 rounded text-xs">scamcap-extension</code> folder
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4 bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                <div className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                  ✓
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-slate-900 dark:text-white mb-1 text-sm">
                    Done! Pin the Extension
                  </h4>
                  <p className="text-slate-600 dark:text-slate-300 text-sm">
                    Click the puzzle icon in your toolbar and pin Scamcap for easy access
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => window.open(getExtensionUrl(), '_blank')}
                  className="flex-1 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition font-medium inline-flex items-center justify-center space-x-2"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span>Open Extensions Page</span>
                </button>
                <a
                  href="/docs/installation"
                  className="flex-1 bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white px-6 py-3 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition font-medium text-center"
                >
                  Detailed Guide
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
