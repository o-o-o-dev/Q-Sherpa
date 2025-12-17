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
    "/api/**": { proxy: process.env.API_PROXY },
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
