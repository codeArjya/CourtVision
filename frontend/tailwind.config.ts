import type { Config } from "tailwindcss";
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./styles/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0D0D0D",
        surface: "#1A1A1A",
        surfaceHigh: "#242424",
        border: "#2E2E2E",
        orange: "#E87722",
        "orange-light": "#FF9A45",
        "orange-dim": "#3D2200",
        primary: "#F0F0F0",
        secondary: "#9A9A9A",
        dim: "#555555",
        success: "#27AE60",
        danger: "#E74C3C",
        warn: "#F1C40F",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      keyframes: {
        slideUp: {
          from: { opacity: "0", transform: "translateY(10px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
      animation: {
        "pulse-live": "pulse 1.5s cubic-bezier(0.4,0,0.6,1) infinite",
        "slide-up": "slideUp 0.25s ease-out forwards",
        "fade-in": "fadeIn 0.2s ease-out forwards",
      },
    },
  },
  plugins: [],
};
export default config;
