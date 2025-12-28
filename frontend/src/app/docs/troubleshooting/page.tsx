import Link from 'next/link'
import { ArrowLeft, AlertCircle } from 'lucide-react'

const issues = [
  {
    problem: 'Extension not appearing after installation',
    solutions: [
      'Refresh the extensions page (chrome://extensions/ or edge://extensions/)',
      'Make sure Developer mode is enabled',
      'Try restarting your browser',
      'Verify the extension folder contains manifest.json',
    ],
  },
  {
    problem: 'Extension icon not showing in toolbar',
    solutions: [
      'Click the extensions puzzle icon in your toolbar',
      'Find Scamcap and click the pin icon to keep it visible',
      'Right-click the toolbar and select "Show Scamcap"',
    ],
  },
  {
    problem: 'Phishing detection not working',
    solutions: [
      'Check that real-time protection is enabled in extension settings',
      'Ensure you have an active internet connection',
      'Clear browser cache and reload the page',
      'Update to the latest version of the extension',
    ],
  },
  {
    problem: 'Extension causing browser to slow down',
    solutions: [
      'Disable other security extensions that might conflict',
      'Clear your browser cache',
      'Check for browser updates',
      'Try disabling and re-enabling the extension',
    ],
  },
  {
    problem: 'False positive warnings on safe websites',
    solutions: [
      'Click "Report False Positive" in the warning popup',
      'Add the site to your whitelist in extension settings',
      'Check if the website SSL certificate is valid',
      'Wait for the next model update which may fix the issue',
    ],
  },
  {
    problem: 'Extension settings not saving',
    solutions: [
      'Check browser permissions for the extension',
      'Clear browser storage and reconfigure',
      'Make sure you\'re not in incognito/private mode',
      'Reinstall the extension if the problem persists',
    ],
  },
  {
    problem: 'Deepfake detection not responding',
    solutions: [
      'Ensure the media file format is supported (JPG, PNG, MP4)',
      'Check file size is under 10MB',
      'Verify internet connection for cloud analysis',
      'Try analyzing a different file to test functionality',
    ],
  },
  {
    problem: 'Cannot load unpacked extension',
    solutions: [
      'Make sure you\'re selecting the correct folder (the one containing manifest.json)',
      'Check that all required files are present in the extension folder',
      'Look for error messages in the extensions page and address them',
      'Try extracting the files to a different location',
    ],
  },
]

export default function TroubleshootingPage() {
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
          Troubleshooting
        </h1>
        <p className="text-xl text-slate-600 dark:text-slate-300 mb-12">
          Solutions to common problems and issues
        </p>

        <div className="space-y-8">
          {issues.map((issue, index) => (
            <div
              key={index}
              className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-6 w-6 text-amber-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">
                    {issue.problem}
                  </h3>
                  <div className="space-y-3">
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      Try these solutions:
                    </p>
                    <ul className="space-y-2">
                      {issue.solutions.map((solution, idx) => (
                        <li
                          key={idx}
                          className="flex items-start space-x-2 text-slate-600 dark:text-slate-300"
                        >
                          <span className="text-primary-600 font-bold">•</span>
                          <span>{solution}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-amber-50 dark:bg-amber-900/20 p-8 rounded-xl border border-amber-200 dark:border-amber-800">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
            Still experiencing issues?
          </h3>
          <p className="text-slate-600 dark:text-slate-300 mb-6">
            If none of these solutions work, please contact our support team with:
          </p>
          <ul className="space-y-2 text-slate-600 dark:text-slate-300 mb-6">
            <li>• Your browser name and version</li>
            <li>• Operating system details</li>
            <li>• Extension version</li>
            <li>• Detailed description of the problem</li>
            <li>• Any error messages you see</li>
          </ul>
          <a
            href="mailto:support@scamcap.com"
            className="inline-block bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition font-medium"
          >
            Contact Support
          </a>
        </div>
      </div>
    </main>
  )
}
