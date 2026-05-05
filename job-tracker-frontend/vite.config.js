import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
      plugins: [react()],
      preview: {
              allowedHosts: ["job-tracker-production-9b92.up.railway.app"],
      },
});