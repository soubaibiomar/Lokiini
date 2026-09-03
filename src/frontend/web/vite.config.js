import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/vitest.setup.js',
    include: ['src/**/*.spec.{js,jsx}'],
    restoreMocks: true,
    clearMocks: true,
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    watch: {
      usePolling: true
    },
    proxy: {
      '/api': {
        target: process.env.API_PROXY_TARGET || 'http://localhost:8001',
        changeOrigin: true
      }
    }
  }
});
