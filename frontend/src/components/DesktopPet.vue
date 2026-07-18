<template>
  <div
    class="desktop-pet"
    @mousedown.prevent="startDrag"
    @click.stop="handleClick"
  >
    <div class="pet-body" :class="{ 'pet-bounce': isBouncing }">
      <div class="pet-face">
        <div class="pet-eyes">
          <span class="eye" :class="{ 'eye-blink': isBlinking }"></span>
          <span class="eye" :class="{ 'eye-blink': isBlinking }"></span>
        </div>
        <div class="pet-mouth">{{ mood }}</div>
      </div>
    </div>
    <div v-if="showBubble" class="speech-bubble">
      {{ currentMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const messages = [
  '你好呀！',
  '今天天气真好~',
  '来看看文章吧！',
  '加油加油！',
  '记得多喝水哦~',
  '你好久没来看我了！',
  '欢迎回来！',
  '今天也要开心哦！',
]

const offsetX = ref(0)
const offsetY = ref(0)
const isDragging = ref(false)
const isBouncing = ref(false)
const isBlinking = ref(false)
const showBubble = ref(false)
const currentMessage = ref('')
const hasMoved = ref(false)
const dragStartPos = ref({ x: 0, y: 0 })

const petStyle = computed(() => ({
  transform: `translate(${offsetX.value}px, ${offsetY.value}px)`,
}))

const mood = computed(() => {
  if (isBouncing.value) return '^_^'
  return '◕‿◕'
})

const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  hasMoved.value = false
  dragStartPos.value = { x: e.clientX, y: e.clientY }
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  const dx = e.clientX - dragStartPos.value.x
  const dy = e.clientY - dragStartPos.value.y
  // 移动超过 5px 才算拖拽，避免误触
  if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
    hasMoved.value = true
  }
  offsetX.value += dx
  offsetY.value += dy
  dragStartPos.value = { x: e.clientX, y: e.clientY }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

const handleClick = () => {
  // 如果发生了拖拽移动，不触发点击互动
  if (hasMoved.value) return
  isBouncing.value = true
  setTimeout(() => { isBouncing.value = false }, 500)

  currentMessage.value = messages[Math.floor(Math.random() * messages.length)]
  showBubble.value = true
  setTimeout(() => { showBubble.value = false }, 3000)
}

let blinkInterval: ReturnType<typeof setInterval>
let messageInterval: ReturnType<typeof setInterval>

onMounted(() => {
  // 随机眨眼
  blinkInterval = setInterval(() => {
    isBlinking.value = true
    setTimeout(() => { isBlinking.value = false }, 150)
  }, 3000 + Math.random() * 2000)

  // 随机说话
  messageInterval = setInterval(() => {
    if (!showBubble.value && !isDragging.value) {
      currentMessage.value = messages[Math.floor(Math.random() * messages.length)]
      showBubble.value = true
      setTimeout(() => { showBubble.value = false }, 3000)
    }
  }, 15000)
})

onUnmounted(() => {
  clearInterval(blinkInterval)
  clearInterval(messageInterval)
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.desktop-pet {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  cursor: grab;
  user-select: none;
  touch-action: none;
}

.desktop-pet:active {
  cursor: grabbing;
}

.pet-body {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: transform 0.3s;
}

.pet-body:hover {
  transform: scale(1.1);
}

.pet-bounce {
  animation: pet-bounce 0.5s ease;
}

@keyframes pet-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.pet-face {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.pet-eyes {
  display: flex;
  gap: 12px;
}

.eye {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  display: block;
  transition: all 0.15s;
}

.eye-blink {
  height: 2px;
  border-radius: 2px;
}

.pet-mouth {
  font-size: 10px;
  color: white;
  font-weight: bold;
}

.speech-bubble {
  position: absolute;
  bottom: 70px;
  right: 0;
  background: white;
  color: #333;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  animation: bubble-pop 0.3s ease;
}

.speech-bubble::after {
  content: '';
  position: absolute;
  bottom: -6px;
  right: 20px;
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid white;
}

@keyframes bubble-pop {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

@media (max-width: 768px) {
  .pet-body {
    width: 45px;
    height: 45px;
  }

  .eye {
    width: 6px;
    height: 6px;
  }

  .pet-eyes {
    gap: 8px;
  }
}
</style>
