'use client'

import { Shield, Sparkles, Zap } from 'lucide-react'

export default function Hero() {
  return (
    <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center">
          <div className="inline-flex items-center space-x-2 bg-primary-50 dark:bg-primary-900/20 px-4 py-2 rounded-full mb-6">
            <Sparkles className="h-4 w-4 text-primary-600" />
            <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
              Advanced AI-Powered Protection
            </span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-slate-900 dark:text-white mb-6">
            Stay Safe Online with
            <span className="block text-primary-600 dark:text-primary-400">Scamcap</span>
          </h1>
          
          <p className="text-xl text-slate-600 dark:text-slate-300 mb-8 max-w-3xl mx-auto">
            Protect yourself from phishing attacks, deepfake content, and online threats with our 
            cutting-edge browser extension powered by machine learning and AI.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <a
              href="#download"
              className="bg-primary-600 text-white px-8 py-4 rounded-lg hover:bg-primary-700 transition font-medium text-lg shadow-lg hover:shadow-xl flex items-center space-x-2"
            >
              <Shield className="h-5 w-5" />
              <span>Download Extension</span>
            </a>
            <a
              href="#features"
              className="bg-white dark:bg-slate-800 text-slate-900 dark:text-white px-8 py-4 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition font-medium text-lg border border-slate-200 dark:border-slate-700"
            >
              Learn More
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="text-3xl font-bold text-primary-600 mb-2">99.9%</div>
              <div className="text-slate-600 dark:text-slate-300">Detection Accuracy</div>
            </div>
            <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="text-3xl font-bold text-primary-600 mb-2">50K+</div>
              <div className="text-slate-600 dark:text-slate-300">Active Users</div>
            </div>
            <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="text-3xl font-bold text-primary-600 mb-2">24/7</div>
              <div className="text-slate-600 dark:text-slate-300">Real-time Protection</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
