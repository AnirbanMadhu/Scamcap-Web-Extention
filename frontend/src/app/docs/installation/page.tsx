import Link from 'next/link'
import { ArrowLeft, Chrome, Globe, Download } from 'lucide-react'

export default function InstallationPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <Link
          href="/docs"
          className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700 mb-8"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Documentation</span>
        </Link>

        <h1 className="text-5xl font-bold text-slate-900 dark:text-white mb-4">
          Installation Guide
        </h1>
        <p className="text-xl text-slate-600 dark:text-slate-300 mb-12">
          Follow these simple steps to install Scamcap on your browser
        </p>

        <div className="space-y-8">
          {/* Chrome Installation */}
          <div className="bg-white dark:bg-slate-800 p-8 rounded-xl border border-slate-200 dark:border-slate-700">
            <div className="flex items-center space-x-3 mb-6">
              <Chrome className="h-8 w-8 text-primary-600" />
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                Google Chrome / Microsoft Edge
              </h2>
            </div>
            
            <ol className="space-y-4 text-slate-600 dark:text-slate-300">
              <li className="flex space-x-3">
                <span className="font-bold text-primary-600">1.</span>
                <div>
                  <p className="font-medium mb-2">Download the Extension</p>
                  <p>Click the download button on the homepage to get the extension package</p>
                </div>
              </li>
              <li className="flex space-x-3">
                <span className="font-bold text-primary-600">2.</span>
                <div>
                  <p className="font-medium mb-2">Extract the Files</p>
                  <p>Unzip the downloaded file to a location on your computer</p>
                </div>
              </li>
              <li className="flex space-x-3">
                <span className="font-bold text-primary-600">3.</span>
                <div>
                  <p className="font-medium mb-2">Open Extensions Page</p>
                  <p>Navigate to <code className="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">chrome://extensions/</code> in Chrome or <code className="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">edge://extensions/</code> in Edge</p>
                </div>
              </li>
              <li className="flex space-x-3">
                <span className="font-bold text-primary-600">4.</span>
                <div>
                  <p className="font-medium mb-2">Enable Developer Mode</p>
                  <p>Toggle the "Developer mode" switch in the top right corner</p>
                </div>
              </li>
              <li className="flex space-x-3">
                <span className="font-bold text-primary-600">5.</span>
                <div>
                  <p className="font-medium mb-2">Load Unpacked Extension</p>
                  <p>Click "Load unpacked" and select the extracted extension folder</p>
                </div>
              </li>
              <li className="flex space-x-3">
                <span className="font-bold text-primary-600">6.</span>
                <div>
                  <p className="font-medium mb-2">Pin the Extension</p>
                  <p>Click the extensions icon in your toolbar and pin Scamcap for easy access</p>
                </div>
              </li>
            </ol>
          </div>

          {/* Firefox Installation */}
          <div className="bg-white dark:bg-slate-800 p-8 rounded-xl border border-slate-200 dark:border-slate-700">
            <div className="flex items-center space-x-3 mb-6">
              <Globe className="h-8 w-8 text-primary-600" />
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                Mozilla Firefox
              </h2>
            </div>
            
            <ol className="space-y-4 text-slate-600 dark:text-slate-300">
              <li className="flex space-x-3">
                <span className="font-bold text-primary-600">1.</span>
                <div>
                  <p className="font-medium mb-2">Download the Extension</p>
                  <p>Get the Firefox-compatible version from the homepage</p>
                </div>
              </li>
              <li className="flex space-x-3">
                <span className="font-bold text-primary-600">2.</span>
                <div>
                  <p className="font-medium mb-2">Navigate to Debug Page</p>
                  <p>Type <code className="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">about:debugging#/runtime/this-firefox</code> in the address bar</p>
                </div>
              </li>
              <li className="flex space-x-3">
                <span className="font-bold text-primary-600">3.</span>
                <div>
                  <p className="font-medium mb-2">Load Temporary Add-on</p>
                  <p>Click "Load Temporary Add-on" and select the manifest.json file from the extracted folder</p>
                </div>
              </li>
            </ol>
          </div>

          {/* Verification */}
          <div className="bg-primary-50 dark:bg-primary-900/20 p-8 rounded-xl border border-primary-200 dark:border-primary-800">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
              ✓ Verify Installation
            </h3>
            <p className="text-slate-600 dark:text-slate-300 mb-4">
              After installation, you should see the Scamcap icon in your browser toolbar. Click it to:
            </p>
            <ul className="space-y-2 text-slate-600 dark:text-slate-300">
              <li>• Configure your security settings</li>
              <li>• Enable real-time protection features</li>
              <li>• View your protection dashboard</li>
            </ul>
          </div>

          <div className="text-center">
            <Link
              href="/docs/troubleshooting"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Having trouble? Check our troubleshooting guide →
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}
