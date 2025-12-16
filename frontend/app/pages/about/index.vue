<template>
  <div class="about">
    <div class="island">
      <header class="deckHeader">
        <div class="deckHeader__brand">
          <div class="hero__topline">Quantum Mountain Optimizer</div>
          <div class="deckHeader__title">Q-Sherpa</div>
        </div>

        <nav class="deckNav" aria-label="About sections">
          <button class="navPill" type="button" @click="scrollTo('intro')">
            Intro
          </button>
          <button class="navPill" type="button" @click="scrollTo('overview')">
            概要
          </button>
          <button class="navPill" type="button" @click="scrollTo('stack')">
            スタック
          </button>
          <button class="navPill" type="button" @click="scrollTo('model')">
            計算モデル
          </button>
          <button class="navPill" type="button" @click="scrollTo('roadmap')">
            今後
          </button>
        </nav>
      </header>

      <main ref="deckMainEl" class="deckMain" aria-label="Slide deck">
        <section id="intro" class="slide slide--hero" aria-label="Intro">
          <div class="hero__bg" aria-hidden="true" />
          <div class="slide__meta">
            <span class="slide__kicker">ABOUT</span>
            <span class="slide__index">1 / 5</span>
          </div>
          <h2 class="slide__title">安全な班分けと、公平な装備配分</h2>
          <p class="lead">
            登山計画で難しい「安全なチーム編成」と「不公平感のない装備分担」を、数理最適化（量子アニーリング
            / QUBO風）で支援するデモアプリです。
          </p>
          <div class="slide__hint">Scroll / Trackpad で次のスライドへ</div>
        </section>

        <section class="slide" aria-labelledby="overview">
          <div class="slide__meta">
            <span class="slide__kicker">OVERVIEW</span>
            <span class="slide__index">2 / 5</span>
          </div>
          <h2 id="overview" class="slide__title">アプリの概要</h2>
          <div class="grid">
            <article class="card">
              <h3>何を解くか</h3>
              <p>
                本システムは、メンバー属性（学年・性別・係・CL/SL資格・運転可否・通信キャリア・経験年数）を入力に、
                班分けと装備配分を段階的に最適化します。
              </p>
            </article>

            <article class="card">
              <h3>キーポイント</h3>
              <ul class="list">
                <li>
                  通信キャリアが偏らないように分散（通信途絶リスクの低減）
                </li>
                <li>ドライバー人数の偏りを抑制（車両運用の実現性）</li>
                <li>係（equipment / weather / meal）の偏りを抑制</li>
                <li>経験年数の分布を調整（チーム間の均等化、または同質化）</li>
                <li>結果は /demo でステップ形式に可視化</li>
              </ul>
            </article>

            <article class="card">
              <h3>API 連携</h3>
              <p>
                フロントは Nuxt の proxy を利用して
                <span class="mono">/api/*</span> にアクセスします。 例:
                <span class="mono">GET /api/members</span>,
                <span class="mono">POST /api/grouping</span>。
              </p>
            </article>
          </div>
        </section>

        <section class="slide" aria-labelledby="stack">
          <div class="slide__meta">
            <span class="slide__kicker">STACK</span>
            <span class="slide__index">3 / 5</span>
          </div>
          <h2 id="stack" class="slide__title">スタック</h2>
          <div class="grid grid--2">
            <article class="card">
              <h3>Frontend</h3>
              <ul class="list">
                <li>Nuxt 3/4 系（Pages ルーティング）</li>
                <li>Vue 3 + TypeScript</li>
                <li>SCSS（スコープド）</li>
                <li>
                  Proxy 経由で API を呼び出し（<span class="mono">/api/**</span
                  >）
                </li>
              </ul>
            </article>

            <article class="card">
              <h3>Backend</h3>
              <ul class="list">
                <li>FastAPI</li>
                <li>Pydantic モデル（Member / Equipment / Settings）</li>
                <li>OpenJij（Simulated Annealing）</li>
                <li>jijmodeling + OMMX（問題定式化とアダプタ）</li>
              </ul>
            </article>
          </div>
        </section>

        <section class="slide" aria-labelledby="model">
          <div class="slide__meta">
            <span class="slide__kicker">MODEL</span>
            <span class="slide__index">4 / 5</span>
          </div>
          <h2 id="model" class="slide__title">計算モデル</h2>
          <div class="grid">
            <article class="card">
              <h3>Phase 1: 班分け（Grouping）</h3>
              <p>
                決定変数は「メンバー m をチーム k
                に割り当てる」二値変数を中心に構成します。
                目的関数は、人数・学年・性別・係・ドライバー・キャリア・経験年数の偏りをペナルティとして加え、
                制約（例:
                全員は必ず1チーム、各チームにCL/SLは各1名、CLとSLは同一人物不可）を満たす解を探索します。
              </p>
              <p class="muted">
                /demo
                の「班分け設定（重み）」は、このペナルティ項の優先度を調整します。
              </p>
            </article>

            <article class="card">
              <h3>Phase 2: 装備配分（Equipment Assignment）</h3>
              <p>
                装備 e をメンバー m
                が持つかを二値で表現し、「全ての装備は誰か1人が持つ」制約のもと、
                メンバー間の負荷（重量）を平準化します。
                経験年数が高いメンバーほど多く持てるように調整パラメータ
                <span class="mono">P</span> を導入しています。
              </p>
            </article>

            <article class="card">
              <h3>なぜ“重み”が重要か</h3>
              <p>
                同じ「二乗誤差」でも、人数差（1人）と経験年数差（数年）ではスケールが異なります。
                そのため、重要制約（運転・役割など）を優先させるには、経験系の重みを相対的に小さくする等の調整が有効です。
              </p>
            </article>
          </div>
        </section>

        <section class="slide" aria-labelledby="roadmap">
          <div class="slide__meta">
            <span class="slide__kicker">ROADMAP</span>
            <span class="slide__index">5 / 5</span>
          </div>
          <h2 id="roadmap" class="slide__title">今後の展開</h2>
          <div class="grid grid--2">
            <article class="card">
              <h3>拡張アイデア</h3>
              <ul class="list">
                <li>D-Wave Leap（ハイブリッドソルバー）への接続</li>
                <li>食料消費など日毎の重量変化を考慮した動的計画</li>
                <li>フォーム連携による自動入力（運用導線の改善）</li>
              </ul>
            </article>

            <article class="card">
              <h3>課題</h3>
              <ul class="list">
                <li>
                  制約が厳しすぎると解が見つからない場合がある（試行回数や重み調整が必要）
                </li>
                <li>目的関数のスケール調整（重みの初期値・上限設計）</li>
                <li>結果の説明可能性（なぜその割当になったか）</li>
              </ul>
            </article>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: "About | Q-Sherpa",
});

useHead({
  bodyAttrs: {
    class: "about-body",
  },
});

const deckMainEl = ref<HTMLElement | null>(null);

const slideNavIds = ["intro", "overview", "stack", "model", "roadmap"];

const getActiveSlideIndex = () => {
  if (typeof document === "undefined") return 0;
  const deckEl = deckMainEl.value;
  if (!deckEl) return 0;

  const deckRect = deckEl.getBoundingClientRect();
  let bestIndex = 0;
  let bestDistance = Number.POSITIVE_INFINITY;

  for (let i = 0; i < slideNavIds.length; i += 1) {
    const targetEl = document.getElementById(slideNavIds[i]);
    if (!targetEl) continue;

    const rect = targetEl.getBoundingClientRect();
    const dist = Math.abs(rect.top - deckRect.top);
    if (dist < bestDistance) {
      bestDistance = dist;
      bestIndex = i;
    }
  }

  return bestIndex;
};

const scrollToSlideIndex = (index: number) => {
  if (typeof document === "undefined") return;
  const clamped = Math.max(0, Math.min(slideNavIds.length - 1, index));
  document.getElementById(slideNavIds[clamped])?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
};

const scrollTo = (id: string) => {
  if (typeof document === "undefined") return;
  document.getElementById(id)?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
};

const onKeyDown = (event: KeyboardEvent) => {
  if (event.defaultPrevented) return;

  if (event.metaKey || event.ctrlKey || event.altKey) return;

  const active = document.activeElement;
  if (active instanceof HTMLElement) {
    const tag = active.tagName.toLowerCase();
    if (
      tag === "input" ||
      tag === "textarea" ||
      tag === "select" ||
      active.isContentEditable
    ) {
      return;
    }
  }

  const current = getActiveSlideIndex();
  const k = event.key;

  if (k === "Home") {
    event.preventDefault();
    scrollToSlideIndex(0);
    return;
  }
  if (k === "End") {
    event.preventDefault();
    scrollToSlideIndex(slideNavIds.length - 1);
    return;
  }

  if (
    k === "ArrowDown" ||
    k === "ArrowRight" ||
    k === "PageDown" ||
    k === " "
  ) {
    event.preventDefault();
    scrollToSlideIndex(current + 1);
    return;
  }

  if (k === "ArrowUp" || k === "ArrowLeft" || k === "PageUp") {
    event.preventDefault();
    scrollToSlideIndex(current - 1);
  }
};

onMounted(() => {
  window.addEventListener("keydown", onKeyDown);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKeyDown);
});
</script>

<style scoped lang="scss">
:global(body.about-body) {
  background: $surface;
}

.about {
  max-width: 1100px;
  margin: 1.5rem auto 3rem;
}

.island {
  background: $color-bg-primary;
  border: 1px solid rgba($color-border, 0.85);
  border-radius: 16px;
  padding: 1.25rem;
  position: relative;
  overflow: hidden;

  &::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background: radial-gradient(
        900px 320px at 20% -10%,
        rgba($primary, 0.08) 0%,
        rgba($primary, 0) 65%
      ),
      radial-gradient(
        900px 320px at 80% -15%,
        rgba($secondary, 0.07) 0%,
        rgba($secondary, 0) 65%
      );
  }
}

.deckHeader {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 0.75rem 0.6rem;
  border-bottom: 1px solid rgba($color-border, 0.65);
}

.deckHeader__brand {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.deckHeader__title {
  color: $on-surface-variant;
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: 0.2px;
}

.deckNav {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.navPill {
  appearance: none;
  border: 1px solid rgba($color-border, 0.75);
  background: rgba($color-bg-primary, 0.55);
  color: $on-surface-variant;
  border-radius: 999px;
  padding: 0.35rem 0.65rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: transform 120ms ease, border-color 120ms ease;

  &:hover {
    transform: translateY(-1px);
    border-color: rgba($primary, 0.35);
  }
}

.deckMain {
  position: relative;
  z-index: 1;
  padding: 0.75rem;
  display: grid;
  gap: 0.75rem;

  max-height: calc(100svh - 220px);
  overflow-y: auto;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;

  // nicer scrolling without changing page background
  scrollbar-color: rgba($primary, 0.35) rgba($color-border, 0.25);
}

.slide {
  position: relative;
  scroll-snap-align: start;
  border: 1px solid rgba($color-border, 0.65);
  border-radius: 14px;
  padding: 1.1rem;
  background: rgba($color-bg-primary, 0.58);

  min-height: calc(100svh - 280px);
}

.slide__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.slide__kicker {
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: $on-surface;
}

.slide__index {
  font-variant-numeric: tabular-nums;
  color: $on-surface;
  font-size: 0.85rem;
}

.slide__title {
  color: $on-surface-variant;
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
}

.slide__hint {
  margin-top: 1.25rem;
  color: $on-surface;
  font-size: 0.9rem;
}

.slide--hero {
  overflow: hidden;
}

/* hero styles are used inside slide now */

.hero__topline {
  font-size: 0.8rem;
  color: $on-surface;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 0.2rem;
}

.hero__bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(
      180deg,
      rgba($primary, 0.05) 0%,
      rgba($primary, 0) 60%
    ),
    conic-gradient(
      from 210deg at 20% 85%,
      rgba($primary, 0) 0deg,
      rgba($primary, 0) 210deg,
      rgba($primary, 0.1) 250deg,
      rgba($primary, 0) 330deg,
      rgba($primary, 0) 360deg
    ),
    conic-gradient(
      from 200deg at 55% 95%,
      rgba($secondary, 0) 0deg,
      rgba($secondary, 0) 210deg,
      rgba($secondary, 0.08) 252deg,
      rgba($secondary, 0) 332deg,
      rgba($secondary, 0) 360deg
    ),
    conic-gradient(
      from 215deg at 85% 90%,
      rgba($primary, 0) 0deg,
      rgba($primary, 0) 210deg,
      rgba($primary, 0.07) 252deg,
      rgba($primary, 0) 332deg,
      rgba($primary, 0) 360deg
    );
  opacity: 1;
}

.lead {
  color: $on-surface;
  line-height: 1.65;
  max-width: 72ch;
}

/* legacy .section removed in favor of .slide */

.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.grid--2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.card {
  border: 1px solid rgba($color-border, 0.65);
  border-radius: 12px;
  padding: 1rem;
  position: relative;
  background: rgba($color-bg-primary, 0.6);

  transition: transform 120ms ease, border-color 120ms ease;

  &::before {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
    background: linear-gradient(
      90deg,
      rgba($primary, 0.65) 0%,
      rgba($secondary, 0.55) 100%
    );
    opacity: 0.35;
  }

  &:hover {
    transform: translateY(-1px);
    border-color: rgba($primary, 0.35);
  }

  h3 {
    color: $on-surface-variant;
    font-size: 1rem;
    margin-bottom: 0.35rem;
  }

  p {
    color: $on-surface-variant;
    line-height: 1.65;
  }
}

.list {
  margin: 0;
  padding-left: 1.1rem;
  color: $on-surface-variant;

  li {
    margin: 0.25rem 0;
    line-height: 1.6;
  }
}

.mono {
  font-variant-numeric: tabular-nums;
}

.muted {
  color: $on-surface;
}

@media (max-width: 960px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .grid--2 {
    grid-template-columns: 1fr;
  }

  .deckHeader {
    align-items: flex-start;
  }

  .deckMain {
    max-height: none;
  }

  .slide {
    min-height: auto;
  }
}

@media (prefers-reduced-motion: reduce) {
  .card {
    transition: none;
  }
}
</style>
