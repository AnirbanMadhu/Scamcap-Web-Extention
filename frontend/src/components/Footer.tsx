'use client'

import Link from 'next/link'
import { Shield, Github, Twitter, Mail } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <Shield className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-slate-900 dark:text-white">Scamcap</span>
            </div>
            <p className="text-slate-600 dark:text-slate-300 text-sm">
              Advanced browser security extension protecting you from online threats.
            </p>
          </div>

          <div>
            <h3 className="font-bold text-slate-900 dark:text-white mb-4">Product</h3>
            <ul className="space-y-2">
              <li>
                <Link href="#features" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 text-sm">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#download" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 text-sm">
                  Download
                </Link>
              </li>
              <li>
                <Link href="/docs" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 text-sm">
                  Documentation
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-slate-900 dark:text-white mb-4">Support</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/docs/installation" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 text-sm">
                  Installation Guide
                </Link>
              </li>
              <li>
                <Link href="/docs/faq" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 text-sm">
                  FAQ
                </Link>
              </li>
              <li>
                <Link href="/docs/troubleshooting" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 text-sm">
                  Troubleshooting
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-slate-900 dark:text-white mb-4">Connect</h3>
            <div className="flex space-x-4">
              <a href="https://github.com" className="text-slate-600 dark:text-slate-300 hover:text-primary-600">
                <Github className="h-5 w-5" />
              </a>
              <a href="https://twitter.com" className="text-slate-600 dark:text-slate-300 hover:text-primary-600">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="mailto:support@scamcap.com" className="text-slate-600 dark:text-slate-300 hover:text-primary-600">
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-200 dark:border-slate-800 pt-8 text-center text-sm text-slate-600 dark:text-slate-400">
          <p>&copy; {new Date().getFullYear()} Scamcap. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
