<script setup lang="ts">
useHead({
  titleTemplate: "%s - 班編成・装備分配最適化ツール",
  script: [
    {
      id: "MathJax-script",
      async: true,
      src: "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js",
    },
  ],
});
useSeoMeta({
  title: "班編成・装備分配最適化ツール",
  description: "大人数の登山における半編成と装備分配を最適化するツールです。",
});
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <!-- <div> -->
  <!--   <NuxtRouteAnnouncer /> -->
  <!--   <NuxtWelcome /> -->
  <!-- </div> -->
</template>
