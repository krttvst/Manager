import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/auth": "http://backend:8000",
      "/users": "http://backend:8000",
      "/channels": "http://backend:8000",
      "/posts": "http://backend:8000",
      "/ai": "http://backend:8000",
      "/stats": "http://backend:8000"
    }
  }
});
