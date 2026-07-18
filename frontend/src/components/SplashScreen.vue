<template>
  <Transition name="splash-fade" @after-leave="$emit('finished')">
    <div v-if="visible" class="splash-screen" :style="splashStyle">
      <!-- 背景装饰 -->
      <div class="splash-bg">
        <div class="bg-orb orb-1"></div>
        <div class="bg-orb orb-2"></div>
        <div class="bg-orb orb-3"></div>
        <div class="bg-grid"></div>
      </div>

      <!-- 主内容 -->
      <div class="splash-content">
        <!-- 图标/Logo -->
        <div class="splash-logo">
          <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="4" width="72" height="72" rx="20" stroke="currentColor" stroke-width="2.5" class="logo-rect" />
            <path d="M24 52V28l16 16 16-16v24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="logo-path" />
          </svg>
        </div>

        <!-- 标题 -->
        <h1 class="splash-title" :class="themeClass">
          <span v-for="(char, i) in chars" :key="i" class="title-char" :style="{ animationDelay: i * 0.06 + 's' }">{{ char }}</span>
        </h1>

        <!-- 副标题 -->
        <p class="splash-subtitle">加载中...</p>

        <!-- 进度条 -->
        <div class="splash-progress">
          <div class="progress-bar" :style="{ width: progress + '%' }"></div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{
  text?: string
  bg?: string
  theme?: string
}>()

defineEmits(['finished'])

const visible = ref(true)
const progress = ref(0)
const animationText = computed(() => props.text || 'Welcome')
const chars = computed(() => animationText.value.split(''))
const themeClass = computed(() => `theme-${props.theme || 'default'}`)

const splashStyle = computed(() => ({
  backgroundColor: props.bg || '#0f0f1a',
}))

onMounted(() => {
  // 模拟加载进度
  const duration = 2200
  const interval = 30
  const steps = duration / interval
  let step = 0

  const timer = setInterval(() => {
    step++
    // 使用缓出曲线模拟进度
    const p = Math.min(100, (step / steps) * 100)
    progress.value = Math.round(p * (1 + Math.sin((p / 100) * Math.PI) * 0.3))
    if (step >= steps) {
      clearInterval(timer)
      progress.value = 100
      setTimeout(() => {
        visible.value = false
      }, 300)
    }
  }, interval)
})
</script>

<style scoped>
.splash-screen {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  overflow: hidden;
}

/* ===== 背景装饰 ===== */
.splash-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

/* 光晕球 */
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  animation: orb-drift 8s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: var(--orb-1, #667eea);
  top: -10%;
  left: -15%;
  animation-delay: 0s;
}

.orb-2 {
  width: 350px;
  height: 350px;
  background: var(--orb-2, #764ba2);
  bottom: -15%;
  right: -10%;
  animation-delay: -3s;
}

.orb-3 {
  width: 250px;
  height: 250px;
  background: var(--orb-3, #4facfe);
  top: 50%;
  left: 60%;
  animation-delay: -6s;
  opacity: 0.1;
}

@keyframes orb-drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.1); }
  66% { transform: translate(-20px, 10px) scale(0.9); }
}

/* 网格背景 */
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
}

/* ===== 主内容 ===== */
.splash-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  z-index: 1;
}

/* Logo */
.splash-logo {
  width: 80px;
  height: 80px;
  color: var(--logo-color, #a78bfa);
  animation: logo-in 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.splash-logo svg {
  width: 100%;
  height: 100%;
}

.logo-rect {
  stroke-dasharray: 240;
  stroke-dashoffset: 240;
  animation: logo-draw-rect 1.2s ease-out 0.3s forwards;
}

.logo-path {
  stroke-dasharray: 80;
  stroke-dashoffset: 80;
  animation: logo-draw-path 0.8s ease-out 0.9s forwards;
}

@keyframes logo-in {
  from { opacity: 0; transform: scale(0.8) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

@keyframes logo-draw-rect {
  to { stroke-dashoffset: 0; }
}

@keyframes logo-draw-path {
  to { stroke-dashoffset: 0; }
}

/* 标题 */
.splash-title {
  font-size: 3rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  display: flex;
  gap: 0.04em;
  margin: 0;
}

.title-char {
  display: inline-block;
  animation: char-in 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
  opacity: 0;
}

@keyframes char-in {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.6);
    filter: blur(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
}

/* 主题颜色 */
.theme-default {
  color: #fff;
  text-shadow: 0 0 40px rgba(167, 139, 250, 0.4), 0 0 80px rgba(167, 139, 250, 0.2);
  --orb-1: #667eea;
  --orb-2: #764ba2;
  --orb-3: #4facfe;
  --logo-color: #a78bfa;
}

.theme-warm {
  color: #ffa07a;
  text-shadow: 0 0 40px rgba(255, 107, 107, 0.4), 0 0 80px rgba(255, 107, 107, 0.2);
  --orb-1: #ff6b6b;
  --orb-2: #ffa07a;
  --orb-3: #feca57;
  --logo-color: #ff6b6b;
}

.theme-cool {
  color: #67e8f9;
  text-shadow: 0 0 40px rgba(78, 205, 196, 0.4), 0 0 80px rgba(78, 205, 196, 0.2);
  --orb-1: #4ecdc4;
  --orb-2: #22d3ee;
  --orb-3: #67e8f9;
  --logo-color: #4ecdc4;
}

.theme-purple {
  color: #c084fc;
  text-shadow: 0 0 40px rgba(168, 85, 247, 0.4), 0 0 80px rgba(168, 85, 247, 0.2);
  --orb-1: #a855f7;
  --orb-2: #7c3aed;
  --orb-3: #c084fc;
  --logo-color: #c084fc;
}

/* 副标题 */
.splash-subtitle {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 0.3em;
  text-transform: uppercase;
  margin: 0;
  animation: subtitle-pulse 2s ease-in-out infinite;
}

@keyframes subtitle-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

/* 进度条 */
.splash-progress {
  width: 200px;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--logo-color, #a78bfa);
  border-radius: 2px;
  transition: width 0.1s linear;
  box-shadow: 0 0 8px var(--logo-color, #a78bfa);
}

/* ===== 过渡 ===== */
.splash-fade-enter-active {
  transition: opacity 0.4s ease;
}

.splash-fade-leave-active {
  transition: opacity 0.6s ease;
}

.splash-fade-enter-from,
.splash-fade-leave-to {
  opacity: 0;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .splash-title {
    font-size: 2rem;
  }
  .splash-logo {
    width: 60px;
    height: 60px;
  }
  .splash-progress {
    width: 160px;
  }
  .bg-orb {
    filter: blur(60px);
    opacity: 0.1;
  }
}
</style>
