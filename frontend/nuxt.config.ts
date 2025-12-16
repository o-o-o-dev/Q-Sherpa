// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: ["@nuxt/eslint", "@nuxt/ui"],
  runtimeConfig: {
    public: {
      apiBase: "/api",
    },
  },
  routeRules: {
    // バックエンドAPIへのプロキシ設定
    "/api/**": { proxy: "https://api.q-sherpa.o-o-o.dev/**" },
    // "/api/**": { proxy: "http://127.0.0.1:8000/**" },
  },
  css: ["~/assets/scss/main.scss", "~/assets/css/main.css"],
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: '@use "~/assets/scss/_variables.scss" as *;',
        },
      },
    },
  },
});
