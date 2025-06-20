import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path'; // <-- импорт path

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@components': path.resolve(__dirname, 'frontend/src/components'),
      '@items': path.resolve(__dirname, 'frontend/src/items'),
      '@utils': path.resolve(__dirname, 'frontend/src/utils'),
    },
  },
});
