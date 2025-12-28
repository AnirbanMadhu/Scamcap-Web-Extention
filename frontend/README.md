# Scamcap Frontend

A modern, responsive Next.js website for the Scamcap browser extension. This site serves as a landing page where users can learn about the extension's features and download it.

## Features

- 🎨 Modern UI with Tailwind CSS
- 🌙 Dark mode support
- 📱 Fully responsive design
- 📄 Comprehensive documentation pages
- ⚡ Fast performance with Next.js 14
- 🎯 SEO optimized
- ♿ Accessible components

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Deployment**: Can be deployed to Vercel, Netlify, or any Node.js hosting

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── docs/           # Documentation pages
│   │   ├── globals.css     # Global styles
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Home page
│   └── components/         # Reusable components
│       ├── Navbar.tsx
│       ├── Hero.tsx
│       ├── Features.tsx
│       ├── HowItWorks.tsx
│       ├── Download.tsx
│       └── Footer.tsx
├── public/                 # Static assets
├── tailwind.config.ts      # Tailwind configuration
├── next.config.js          # Next.js configuration
└── package.json
```

## Pages

- **Home** (`/`) - Landing page with hero, features, and download sections
- **Documentation** (`/docs`) - Overview of all documentation
- **Installation Guide** (`/docs/installation`) - Step-by-step installation instructions
- **FAQ** (`/docs/faq`) - Frequently asked questions
- **Troubleshooting** (`/docs/troubleshooting`) - Common issues and solutions

## Customization

### Colors

Edit the color scheme in [tailwind.config.ts](tailwind.config.ts):

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      },
    },
  },
}
```

### Content

Update content in the component files located in `src/components/`:
- Hero section: [src/components/Hero.tsx](src/components/Hero.tsx)
- Features: [src/components/Features.tsx](src/components/Features.tsx)
- etc.

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import your repository on [Vercel](https://vercel.com)
3. Vercel will automatically detect Next.js and deploy

### Manual Deployment

```bash
npm run build
npm start
```

The application will be available on port 3000.

## Environment Variables

Currently, no environment variables are required. If you add API integrations, create a `.env.local` file:

```
NEXT_PUBLIC_API_URL=your_api_url
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is part of the Scamcap extension suite.

## Support

For issues or questions:
- Email: support@scamcap.com
- GitHub: Create an issue in the repository
