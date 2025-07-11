/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounce 1s infinite',
      },
      colors: {
        'sf-blue': '#0176d3',
        'sf-dark': '#032d60',
        'jira-blue': '#0052cc',
        'jira-dark': '#0043a6',
      }
    },
  },
  plugins: [],
}