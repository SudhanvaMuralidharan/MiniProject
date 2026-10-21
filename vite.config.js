import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The frontend lives in ./frontend; the single package.json stays at the project root.
export default defineConfig({
  root: 'frontend',
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8000' },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
