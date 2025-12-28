import Link from 'next/link'
import { ArrowLeft, HelpCircle } from 'lucide-react'

const faqs = [
  {
    question: 'Is Scamcap really free?',
    answer: 'Yes! Scamcap is completely free to use with no hidden costs, subscriptions, or premium tiers. We believe everyone deserves access to online security.',
  },
  {
    question: 'How does Scamcap detect phishing websites?',
    answer: 'Scamcap uses advanced machine learning algorithms trained on millions of known phishing sites. It analyzes URL patterns, page content, SSL certificates, and other indicators to identify potential threats in real-time.',
  },
  {
    question: 'Does Scamcap collect my browsing data?',
    answer: 'No. Scamcap is privacy-first. All analysis happens locally on your device. We do not collect, store, or transmit your browsing history or personal data.',
  },
  {
    question: 'What is deepfake detection?',
    answer: 'Our deepfake detection feature uses AI to identify manipulated images and videos. It helps you spot fake content that could be used for misinformation or scams.',
  },
  {
    question: 'How accurate is the threat detection?',
    answer: 'Scamcap maintains a 99.9% accuracy rate in detecting known threats. Our models are continuously updated with new threat patterns to stay ahead of emerging scams.',
  },
  {
    question: 'Can I use Scamcap on mobile browsers?',
    answer: 'Currently, Scamcap is available for desktop browsers (Chrome, Edge, Firefox). Mobile support is in development and will be released soon.',
  },
  {
    question: 'What should I do if I encounter a false positive?',
    answer: 'If Scamcap incorrectly flags a safe website, you can report it through the extension popup. Our team will review and update the detection models accordingly.',
  },
  {
    question: 'Does Scamcap slow down my browser?',
    answer: 'No. Scamcap is optimized for performance with minimal impact on browsing speed. Most scans complete in milliseconds without any noticeable delay.',
  },
  {
    question: 'How often is Scamcap updated?',
    answer: 'We release updates regularly to improve detection accuracy and add new features. The extension automatically checks for updates and notifies you when new versions are available.',
  },
  {
    question: 'Can I contribute to Scamcap?',
    answer: 'Absolutely! Scamcap is open source. You can contribute code, report bugs, or suggest features on our GitHub repository.',
  },
]

export default function FAQPage() {
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
          Frequently Asked Questions
        </h1>
        <p className="text-xl text-slate-600 dark:text-slate-300 mb-12">
          Find answers to common questions about Scamcap
        </p>

        <div className="space-y-6">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <HelpCircle className="h-6 w-6 text-primary-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-3">
                    {faq.question}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-300">
                    {faq.answer}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-primary-50 dark:bg-primary-900/20 p-8 rounded-xl border border-primary-200 dark:border-primary-800 text-center">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
            Still have questions?
          </h3>
          <p className="text-slate-600 dark:text-slate-300 mb-6">
            Can't find what you're looking for? Reach out to our support team.
          </p>
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
