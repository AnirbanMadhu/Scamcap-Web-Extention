'use client'

import Link from 'next/link'
import { Shield } from 'lucide-react'

export default function Navbar() {
  return (
    <nav className="fixed top-0 w-full bg-white/80 dark:bg-slate-900/80 backdrop-blur-md z-50 border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <Shield className="h-8 w-8 text-primary-600" />
            <span className="text-2xl font-bold text-slate-900 dark:text-white">
              Scamcap
            </span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            <Link href="#features" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-400 transition">
              Features
            </Link>
            <Link href="#how-it-works" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-400 transition">
              How It Works
            </Link>
            <Link href="#download" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-400 transition">
              Download
            </Link>
            <Link href="/docs" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-400 transition">
              Docs
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <a
              href="#download"
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition font-medium"
            >
              Get Started
            </a>
          </div>
        </div>
      </div>
    </nav>
  )
}
