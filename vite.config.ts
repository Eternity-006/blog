import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'
import { postApi } from './scripts/post-api'

export default defineConfig({
  base: '/blog/',
  plugins: [vue(), tailwindcss(), postApi()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
})
