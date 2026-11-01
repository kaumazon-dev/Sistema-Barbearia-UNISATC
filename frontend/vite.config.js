import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Em dev o Vite repassa /api para o Flask: front e API ficam na mesma origem
// e o CORS nem entra em jogo. Em producao quem faz isso e o nginx
// (nginx.conf) ou, no Vercel, a variavel VITE_API_URL.
const API = process.env.VITE_PROXY_API || 'http://localhost:5000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: API, changeOrigin: true }
    }
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['tests/setup.js']
  }
});
