'use client'

import { Download, Settings, Shield, CheckCircle } from 'lucide-react'

const steps = [
  {
    icon: Download,
    title: 'Download Extension',
    description: 'Click the download button and add Scamcap to your browser in seconds.',
  },
  {
    icon: Settings,
    title: 'Configure Settings',
    description: 'Customize your security preferences and enable the features you need.',
  },
  {
    icon: Shield,
    title: 'Browse Safely',
    description: 'Surf the web with confidence as Scamcap protects you in real-time.',
  },
  {
    icon: CheckCircle,
    title: 'Stay Protected',
    description: 'Receive alerts and reports about threats blocked and your safety status.',
  },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 px-4 sm:px-6 lg:px-8 bg-white dark:bg-slate-800">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-4">
            How It Works
          </h2>
          <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">
            Get started with Scamcap in just a few simple steps
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="text-center">
                <div className="bg-primary-100 dark:bg-primary-900/30 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <step.icon className="h-10 w-10 text-primary-600" />
                </div>
                <div className="absolute top-10 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <div className="bg-primary-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm">
                    {index + 1}
                  </div>
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
                  {step.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-300">
                  {step.description}
                </p>
              </div>
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-10 left-full w-full h-0.5 bg-primary-200 dark:bg-primary-800 -translate-y-1/2" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
