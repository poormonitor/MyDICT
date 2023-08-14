import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";

import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { NaiveUiResolver } from "unplugin-vue-components/resolvers";

import { VitePWA } from "vite-plugin-pwa";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        vueJsx(),
        AutoImport({
            imports: [
                "vue",
                {
                    "naive-ui": [
                        "useDialog",
                        "useMessage",
                        "useNotification",
                        "useLoadingBar",
                    ],
                },
            ],
        }),
        Components({
            resolvers: [NaiveUiResolver()],
        }),
        VitePWA({
            registerType: "autoUpdate",
            manifest: {
                name: "MyDICT",
                short_name: "MyDICT",
                description: "A universal dictionary tool",
                theme_color: "#ffffff",
                icons: [
                    {
                        src: "favicon.png",
                        sizes: "256x256",
                        type: "image/png",
                    },
                ],
            },
            workbox: {
                sourcemap: true,
            },
        }),
    ],
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },
});
