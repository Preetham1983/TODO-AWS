import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// =============================================================================
// Vite Configuration
// Dev  : vite --port 3000  (proxy /api/* → localhost backend services)
// Prod : vite build → dist/, served by nginx via Docker
// =============================================================================

export default defineConfig({
  plugins: [
    react(),
  ],

  // ── Development server ─────────────────────────────────────────────────────
  server: {
    port: 3000,
    strictPort: true,
    proxy: {
      "/api/v1/todos": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/api/v1/attachments": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
      "/api/v1/notifications": {
        target: "http://localhost:8003",
        changeOrigin: true,
      },
    },
  },

  // ── Preview server (used in Docker) ────────────────────────────────────────
  preview: {
    port: 3000,
    host: true,
    strictPort: true,
  },
});
