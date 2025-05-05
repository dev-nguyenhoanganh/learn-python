import { defineConfig, loadEnv, ProxyOptions } from "vite";
import path from "node:path";
import react from "@vitejs/plugin-react";
import checker from "vite-plugin-checker";
import tsconfigPaths from "vite-tsconfig-paths";

// Config proxy for development mode
const getProxyOptions = (mode: string) => {
  if (mode === "development") {
    return {
      "/api": {
        target: "BACKEND_URL",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    } as Record<string, ProxyOptions>;
  }
};

export default ({ mode }: { mode: string }) => {
  // https://vitejs.dev/config/
  return defineConfig({
    plugins: [react(), checker({ typescript: true }), tsconfigPaths()],
    base: "",
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    server: {
      port: Number(process.env.PORT) || 9000,
      open: true,
      proxy: getProxyOptions(mode),
    },
    define: {
      "process.env": { ...loadEnv(mode, process.cwd(), "ENV_") },
    },
    publicDir: "public",
    build: {
      sourcemap: true,
      rollupOptions: {
        input: {
          app: "./index.html",
        },
        output: {
          manualChunks(id) {
            if (id.includes("node_modules")) {
              return id.toString().split("node_modules/")[1].split("/")[0].toString();
            }
          },
        },
      },
    },
  });
};

