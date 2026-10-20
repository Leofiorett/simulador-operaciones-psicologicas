import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Para GitHub Pages la app se sirve bajo /<repo>/. Vite inyecta BASE_URL;
// el router debe usar ese prefijo. En build se define VITE_BASE_PATH.
export default defineConfig({
  base: process.env.VITE_BASE_PATH || '/',
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://localhost:8001' }
  }
})
