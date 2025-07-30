// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Correct configuration without trying to add tailwind here
export default defineConfig({
  plugins: [react()],
});


