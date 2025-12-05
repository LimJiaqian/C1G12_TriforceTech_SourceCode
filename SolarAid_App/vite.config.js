import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/jam-api': {
        target: 'https://api.jamaibase.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/jam-api/, ''),
        secure: true
      }
    }
  }
})
