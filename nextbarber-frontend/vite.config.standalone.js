import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

/**
 * Build "autonomo": gera um bundle classico (IIFE), sem <script type="module">.
 * E o que permite abrir o HTML final por duplo clique (protocolo file://),
 * sem servidor e sem npm. Use: npm run build:html
 */
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist-standalone',
    cssCodeSplit: false,
    assetsInlineLimit: 100000000,
    modulePreload: { polyfill: false },
    rollupOptions: {
      output: {
        format: 'iife',
        inlineDynamicImports: true,
        entryFileNames: 'app.js',
        assetFileNames: 'app.[ext]'
      }
    }
  }
});
