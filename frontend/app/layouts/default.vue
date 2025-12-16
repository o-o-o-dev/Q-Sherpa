<template>
  <div class="default-layout">
    <main class="default-main">
      <slot />
    </main>
    <footer class="default-footer">
      <div class="footer-content">
        <img
          class="club-logo"
          src="/jishinkai_logo.webp"
          alt="Jishinkai Club Logo"
          width="100"
        />
        <p>
          &copy; 2025 自然に親しむ会, Soma Terao, Morio Chiba, Tatsuhiro Araki.
          All rights reserved.
        </p>
      </div>
    </footer>
  </div>
</template>

<style lang="scss" scoped>
.default-layout {
  display: flex;
  flex-direction: column;
  margin: 0 1rem;
  min-height: 100vh;
  footer {
    margin-top: 2rem;
    .footer-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin-bottom: 1rem;
      img {
        margin-bottom: 0.5rem;
        opacity: 0.3;
        width: 30px;
      }
      p {
        font-size: 0.875rem;
        color: $on-surface;
      }
    }
  }
}

.default-main {
  flex: 1;
  width: 100%;
}
</style>
