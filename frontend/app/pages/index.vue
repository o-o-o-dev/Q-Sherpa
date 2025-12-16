<script setup lang="ts">
import gsap from "gsap";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { ScrollTrigger } from "gsap/ScrollTrigger";

useSeoMeta({
  title: "ホーム",
});

gsap.registerPlugin(DrawSVGPlugin, ScrollTrigger);

const mountain = ref(null);
const sun = ref(null);
const heroTitle = ref(null);
const heroSubtitle = ref(null);
const heroButton = ref(null);

const playAnimation = () => {
  gsap.fromTo(
    mountain.value,
    { drawSVG: "0%" },
    { drawSVG: "100%", duration: 2, stagger: 2, ease: "power1.in" },
  );

  gsap.fromTo(
    sun.value,
    { drawSVG: "0%" },
    {
      drawSVG: "100%",
      duration: 0.8,
      stagger: 2,
      ease: "power1.inOut",
      delay: 1.5,
    },
  );
};

const fadeUp = (element: string | Element, options = {}) => {
  const defaultOptions = {
    duration: 1.5,
    y: 48,
    opacity: 0,
    delay: 0,
    opacityEnd: 1,
    ease: "power3.out",
    ...options,
  };
  return gsap.fromTo(
    element,
    {
      opacity: 0,
      y: defaultOptions.y,
    },
    {
      opacity: defaultOptions.opacityEnd,
      y: 0,
      duration: defaultOptions.duration,
      ease: defaultOptions.ease,
      delay: defaultOptions.delay,
      scrollTrigger: {
        trigger: element,
        start: "top 80%",
        toggleActions: "play none none pause",
      },
    },
  );
};

const fadeIn = (element: string, option = {}) => {
  const defaultOptions = {
    duration: 1.5,
    opacity: 0,
    opacityEnd: 1,
    delay: 0,
    ease: "power3.out",
    ...option,
  };

  return gsap.fromTo(
    element,
    {
      opacity: 0,
    },
    {
      opacity: defaultOptions.opacityEnd,
      duration: defaultOptions.duration,
      ease: defaultOptions.ease,
      delay: defaultOptions.delay,
      scrollTrigger: {
        trigger: element,
        start: "top 80%",
        toggleActions: "play none none pause",
      },
    },
  );
};

onMounted(() => {
  playAnimation();
  if (heroTitle.value) {
    fadeUp(heroTitle.value, { delay: 0.3 });
  }

  if (heroSubtitle.value) {
    fadeUp(heroSubtitle.value, { delay: 0.3 });
  }

  if (heroButton.value) {
    fadeIn(heroButton.value, { delay: 0.8 });
  }
});
</script>

<template>
  <div class="hero">
    <div class="hero-wrapper">
      <div class="hero-content">
        <h1 ref="heroTitle" class="hero-title">
          <span class="hero-accent">量子</span>の揺らぎで、<br />
          <span style="color: green">自然</span>との調和を。
        </h1>
        <p ref="heroSubtitle" class="hero-subtitle">
          量子アニーリング技術で、登山の班編成と装備分配を最適化。
        </p>
        <div ref="heroButton" class="hero-action">
          <button>試す</button>
        </div>
      </div>
      <div class="hero-visual">
        <svg
          viewBox="0 0 24 24"
          class="hero-icon"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            ref="sun"
            cx="18"
            cy="6"
            r="3"
            style="
              fill: none;
              stroke: #fc9003;
              stroke-linecap: round;
              stroke-linejoin: round;
              stroke-width: 2px;
            "
          />
          <path
            id="mountain-path"
            ref="mountain"
            d="M4,21h7l2.37-4.86-2.49-4.62a1,1,0,0,0-1.76,0Zm14.4,0H11l4.5-9.23,3.8,7.79A1,1,0,0,1,18.4,21Z"
            style="
              fill: none;
              stroke: #038a3b;
              stroke-linecap: round;
              stroke-linejoin: round;
              stroke-width: 2px;
            "
          />
        </svg>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use "sass:color";
.hero {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 120px);
}

.hero-wrapper {
  display: flex;
  max-width: 100%;
  gap: 5rem;
  align-items: center;
}

.hero-content {
  flex: 1;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 1.5rem;
  color: $on-surface-variant;
  word-break: keep-all;
  overflow-wrap: break-word;
}

.hero-accent {
  display: inline-block;
  background: linear-gradient(
    90deg,
    rgba(42, 123, 155, 1) 19%,
    rgba(136, 103, 235, 1) 56%
  );
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: $on-surface;
  line-height: 1.6;
}

.hero-visual {
  flex: 1;
  display: flex;
  height: 100%;
  align-items: center;
  justify-content: center;
}

.hero-icon {
  width: 100%;
  max-width: 500px;
  max-height: 500px;
}

.hero-action {
  margin-top: 1rem;
  button {
    padding: 0.75rem 1.5rem;
    font-size: 1.125rem;
    border: none;
    border-radius: 0.375rem;
    background-color: $secondary;
    color: $on-secondary;
    cursor: pointer;
    transition: background-color 0.3s ease;
    &:hover {
      background-color: color.adjust($secondary, $lightness: -10%);
    }
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@media (max-width: 800px) {
  .hero-wrapper {
    flex-direction: column-reverse;
    text-align: center;
    gap: 0.5rem;
  }

  .hero-content {
    max-width: 100%;
  }

  .hero-icon {
    max-width: 500px;
  }
}
@media (max-width: 1200px) {
  .hero-wrapper {
    padding: 2rem 1.5rem;
    gap: 2rem;
  }
}
</style>
