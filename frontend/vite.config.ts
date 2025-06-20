import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@components': path.resolve(__dirname, 'src/components'),
      '@items': path.resolve(__dirname, 'src/items'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@route': path.resolve(__dirname, 'src/route'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@pages': path.resolve(__dirname, 'src/pages'),
    },
  },
});
