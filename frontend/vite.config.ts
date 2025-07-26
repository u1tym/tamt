import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { readFileSync } from 'fs'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: { 
    host: '0.0.0.0', 
    port: 5173, 
    strictPort: false,
    https: {
      key: readFileSync(resolve(__dirname, 'localhost-key.pem')),
      cert: readFileSync(resolve(__dirname, 'localhost.pem')),
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false
  }
})
