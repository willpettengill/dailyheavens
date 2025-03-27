import type { Config } from "tailwindcss"

const config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        background: "#1A1A1A",
        foreground: "#FFFFFF",
        muted: "#CCCCCC",
        "accent-pink": "#FF6EC7",
        "accent-purple": "#9D6AFF",
        "accent-teal": "#00FFD1",
        "accent-yellow": "#FFD700",
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
      },
      fontFamily: {
        montserrat: ["var(--font-montserrat)", "sans-serif"],
        raleway: ["var(--font-raleway)", "sans-serif"],
        "fira-code": ["var(--font-fira-code)", "monospace"],
      },
      boxShadow: {
        "neon-pink": "0 0 5px #FF6EC7, 0 0 10px #FF6EC7",
        "neon-purple": "0 0 5px #9D6AFF, 0 0 10px #9D6AFF",
        "neon-teal": "0 0 5px #00FFD1, 0 0 10px #00FFD1",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config 