/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: 'rgb(var(--color-canvas) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        ink: 'rgb(var(--color-ink) / <alpha-value>)',
        muted: 'rgb(var(--color-muted) / <alpha-value>)',
        border: 'rgb(var(--color-border) / <alpha-value>)',
        primary: {
          DEFAULT: 'rgb(var(--color-primary) / <alpha-value>)',
          hover: 'rgb(var(--color-primary-hover) / <alpha-value>)',
          subtle: 'rgb(var(--color-primary-subtle) / <alpha-value>)',
        },
        action: {
          DEFAULT: 'rgb(var(--color-action) / <alpha-value>)',
          hover: 'rgb(var(--color-action-hover) / <alpha-value>)',
          subtle: 'rgb(var(--color-action-subtle) / <alpha-value>)',
        },
        success: {
          DEFAULT: 'rgb(var(--color-success) / <alpha-value>)',
          subtle: 'rgb(var(--color-success-subtle) / <alpha-value>)',
        },
        warning: {
          DEFAULT: 'rgb(var(--color-warning) / <alpha-value>)',
          subtle: 'rgb(var(--color-warning-subtle) / <alpha-value>)',
        },
        error: {
          DEFAULT: 'rgb(var(--color-error) / <alpha-value>)',
          subtle: 'rgb(var(--color-error-subtle) / <alpha-value>)',
        },
        info: {
          DEFAULT: 'rgb(var(--color-info) / <alpha-value>)',
          subtle: 'rgb(var(--color-info-subtle) / <alpha-value>)',
        },
        lokiini: {
          teal: 'rgb(var(--color-primary) / <alpha-value>)',
          'teal-dark': 'rgb(var(--color-primary-hover) / <alpha-value>)',
          'teal-light': 'rgb(var(--color-primary-subtle) / <alpha-value>)',
          terracotta: 'rgb(var(--color-action) / <alpha-value>)',
          'terracotta-dark': 'rgb(var(--color-action-hover) / <alpha-value>)',
          'terracotta-light': 'rgb(var(--color-action-subtle) / <alpha-value>)',
          sand: 'rgb(var(--color-canvas) / <alpha-value>)',
          charcoal: 'rgb(var(--color-ink) / <alpha-value>)',
          amber: 'rgb(var(--color-warning) / <alpha-value>)',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Noto Sans Arabic', 'sans-serif'],
        display: ['Outfit', 'Noto Sans Arabic', 'sans-serif'],
      },
      fontSize: {
        'display-sm': ['2.25rem', { lineHeight: '1.1', letterSpacing: '-0.025em', fontWeight: '700' }],
        'display-md': ['3rem', { lineHeight: '1.05', letterSpacing: '-0.035em', fontWeight: '700' }],
      },
      borderRadius: {
        control: 'var(--radius-control)',
        card: 'var(--radius-card)',
        modal: 'var(--radius-modal)',
      },
      boxShadow: {
        subtle: 'var(--shadow-subtle)',
        card: 'var(--shadow-card)',
        raised: 'var(--shadow-raised)',
        focus: 'var(--shadow-focus)',
      },
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
      },
      transitionDuration: {
        180: '180ms',
      },
    },
  },
  plugins: [],
}
