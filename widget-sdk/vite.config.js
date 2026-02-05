import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
  },
  build: {
    lib: {
      entry: 'src/index.jsx',
      name: 'WebScraperChat',
      fileName: 'widget',
      formats: ['umd'],
    },
    rollupOptions: {
      // We bundle everything for the widget to ensure it's plug-and-play
      external: [],
      output: {
        globals: {},
        exports: 'named'
      },
    },
  },
})
