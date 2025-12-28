'use client'

import { Shield, Eye, Lock, Zap, Globe, Bell } from 'lucide-react'

const features = [
  {
    icon: Shield,
    title: 'Phishing Detection',
    description: 'Advanced AI algorithms scan websites in real-time to identify and block phishing attempts before they can harm you.',
  },
  {
    icon: Eye,
    title: 'Deepfake Detection',
    description: 'State-of-the-art machine learning models detect manipulated images and videos to protect you from misinformation.',
  },
  {
    icon: Lock,
    title: 'Multi-Factor Authentication',
    description: 'Built-in MFA support adds an extra layer of security to your accounts with seamless integration.',
  },
  {
    icon: Zap,
    title: 'Real-Time Scanning',
    description: 'Lightning-fast analysis happens as you browse, ensuring zero delay in your online experience.',
  },
  {
    icon: Globe,
    title: 'Privacy First',
    description: 'Your data stays yours. All scanning happens locally with optional cloud analysis for enhanced protection.',
  },
  {
    icon: Bell,
    title: 'Instant Alerts',
    description: 'Get immediate notifications when threats are detected, with detailed explanations and safety recommendations.',
  },
]

export default function Features() {
  return (
    <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-4">
            Powerful Features for Complete Protection
          </h2>
          <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">
            Comprehensive security tools designed to keep you safe while browsing the web
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white dark:bg-slate-800 p-8 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-lg transition group"
            >
              <div className="bg-primary-50 dark:bg-primary-900/20 w-14 h-14 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition">
                <feature.icon className="h-7 w-7 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
                {feature.title}
              </h3>
              <p className="text-slate-600 dark:text-slate-300">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
