import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: "./" → relative asset paths so the static build works under any GitHub Pages subpath.
// /api is proxied to the FastAPI chassis (uvicorn chassis.app:app --port 8000) for the live platform.
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: { proxy: { "/api": "http://localhost:8000" } },
});
