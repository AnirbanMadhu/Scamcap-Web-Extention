import Link from 'next/link'
import { ArrowLeft, Book, FileQuestion, Wrench } from 'lucide-react'

const docSections = [
  {
    icon: Book,
    title: 'Installation Guide',
    description: 'Step-by-step instructions to install Scamcap extension',
    href: '/docs/installation',
  },
  {
    icon: FileQuestion,
    title: 'Frequently Asked Questions',
    description: 'Common questions and answers about Scamcap',
    href: '/docs/faq',
  },
  {
    icon: Wrench,
    title: 'Troubleshooting',
    description: 'Solutions to common issues and problems',
    href: '/docs/troubleshooting',
  },
]

export default function DocsPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <Link
          href="/"
          className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700 mb-8"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Home</span>
        </Link>

        <h1 className="text-5xl font-bold text-slate-900 dark:text-white mb-4">
          Documentation
        </h1>
        <p className="text-xl text-slate-600 dark:text-slate-300 mb-12">
          Everything you need to know about Scamcap
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {docSections.map((section, index) => (
            <Link
              key={index}
              href={section.href}
              className="bg-white dark:bg-slate-800 p-8 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-lg transition group"
            >
              <div className="bg-primary-50 dark:bg-primary-900/20 w-14 h-14 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition">
                <section.icon className="h-7 w-7 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
                {section.title}
              </h3>
              <p className="text-slate-600 dark:text-slate-300">
                {section.description}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </main>
  )
}
