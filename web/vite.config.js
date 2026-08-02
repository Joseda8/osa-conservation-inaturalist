import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const configuredBasePath = process.env.VITE_BASE_PATH ?? "/";
const basePath = configuredBasePath.endsWith("/") ? configuredBasePath : `${configuredBasePath}/`;

export default defineConfig({
  base: basePath,
  plugins: [react()],
});
