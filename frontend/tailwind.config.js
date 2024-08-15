/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        'space': "url('/space-background1.png')",
      },
      backgroundColor: {
        'background-default': 'var(--background-default)',
      },
      keyframes: {
        tiltAnimation: {
          '0%, 100%': { transform: 'rotate(-10deg)' },
          '50%': { transform: 'rotate(10deg)' },
        },
      },
      animation: {
        'tilt': 'tiltAnimation 2s infinite',
      },
    },
  },
  plugins: [],
};
