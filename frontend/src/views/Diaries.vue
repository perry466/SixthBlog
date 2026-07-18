<template>
  <div class="diaries-page">
    <h1 class="page-title">日记</h1>

    <div v-if="loading" class="loading-spinner">加载中...</div>
    <div v-else-if="diaries.length === 0" class="empty-state">暂无日记</div>
    <div v-else class="diaries-list">
      <article v-for="diary in diaries" :key="diary.id" class="diary-card" @click="goToDiary(diary.id)" style="cursor: pointer;">
        <div class="diary-date">{{ formatDate(diary.published_at || diary.created_at) }}</div>
        <h2 class="diary-title">{{ diary.title }}</h2>
        <p class="diary-summary">{{ diary.summary }}</p>
        <div class="diary-footer">
          <span>{{ diary.word_count }} 字</span>
          <span>{{ diary.view_count }} 次阅读</span>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDiaries } from '../api/blog'

const router = useRouter()
const diaries = ref<any[]>([])
const loading = ref(true)
const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })

const goToDiary = (id: number) => {
  router.push('/diary/' + id)
}

onMounted(async () => {
  try { const data = await getDiaries() as any; diaries.value = data.results || data } catch { /* empty */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.diaries-page { max-width: 800px; margin: 0 auto; }

.diaries-list { display: flex; flex-direction: column; gap: 1rem; }

.diary-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 1.5rem;
  transition: all 0.25s ease;
  position: relative;
  padding-left: 5rem;
}
.diary-card:hover { box-shadow: var(--shadow-md); border-color: transparent; transform: translateY(-2px); }

.diary-date {
  position: absolute; left: 1.25rem; top: 1.5rem;
  writing-mode: vertical-rl;
  font-size: 0.72rem; font-weight: 600; color: var(--accent);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.diary-title { font-size: 1.15rem; font-weight: 650; color: var(--text-h); margin: 0 0 0.5rem; line-height: 1.4; }
.diary-summary { font-size: 0.85rem; color: var(--text); line-height: 1.6; margin: 0 0 0.75rem; }
.diary-footer { display: flex; gap: 1rem; font-size: 0.78rem; color: var(--text-muted); }

@media (max-width: 768px) { .diary-card { padding: 1.25rem; padding-left: 3.5rem; } }
</style>
