import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // すべてのIPアドレスでアクセス可能
    port: 5173,
    strictPort: false, // ポートが使用中の場合は自動的に次のポートを使用
  },
})
