import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0a',
        foreground: '#ffffff',
        muted: '#a0a0a0',
        border: '#2a2a2a',
        card: '#141414',
        'card-hover': '#1a1a1a',
        accent: '#3b82f6',
        'accent-hover': '#2563eb',
        success: '#22c55e',
      },
    },
  },
  plugins: [],
}
export default config
