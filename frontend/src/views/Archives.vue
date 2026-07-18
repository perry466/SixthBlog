<template>
  <div class="archives-page">
    <h1 class="page-title">文章归档</h1>

    <div v-if="loading" class="loading-spinner">加载中...</div>
    <div v-else-if="archives.length === 0" class="empty-state">暂无归档</div>

    <div v-else class="archives-container">
      <div v-for="(archive, index) in archives" :key="archive.month" class="archive-group">
        <div class="archive-year-header" v-if="showYearHeader(index, archive.month)">
          {{ getYear(archive.month) }}
        </div>
        <div
          class="archive-month-bar"
          :class="{ expanded: openMonth === archive.month }"
          @click="toggleMonth(archive.month)"
        >
          <div class="archive-month-left">
            <div class="archive-dot" :class="{ active: openMonth === archive.month }"></div>
            <div class="timeline-line" v-if="index < archives.length - 1"></div>
            <span class="archive-month-name">{{ formatMonth(archive.month) }}</span>
          </div>
          <div class="archive-month-right">
            <span class="archive-count">{{ archive.count }} 篇</span>
            <svg
              class="archive-chevron"
              :class="{ rotated: openMonth === archive.month }"
              width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
            ><polyline points="6 9 12 15 18 9"/></svg>
          </div>
        </div>
        <transition name="article-slide">
          <div v-if="openMonth === archive.month" class="archive-articles">
            <div
              v-for="(art, artIdx) in (archive.articles || [])"
              :key="art.id"
              class="archive-article-item"
              :style="{ animationDelay: artIdx * 0.05 + 's' }"
              @click.stop="goToArticle(art.id)"
            >
              <span class="article-item-dot"></span>
              <span class="article-item-title">{{ art.title }}</span>
              <svg class="article-item-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getArchives } from '../api/blog'

const router = useRouter()
const archives = ref<any[]>([])
const loading = ref(true)
const openMonth = ref<string | null>(null)

function getYear(monthStr: string) { return monthStr.split('-')[0] }
function showYearHeader(index: number, monthStr: string): boolean {
  if (index === 0) return true
  return getYear(monthStr) !== getYear(archives.value[index - 1].month)
}
function formatMonth(monthStr: string) {
  const d = new Date(monthStr)
  return d.getFullYear() + '年' + (d.getMonth() + 1) + '月'
}
function toggleMonth(month: string) {
  openMonth.value = openMonth.value === month ? null : month
}
function goToArticle(id: number) {
  router.push('/article/' + id)
}

onMounted(async () => {
  try { archives.value = await getArchives() } catch { /* empty */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.archives-page { max-width: 700px; margin: 0 auto; }

.archives-container { display: flex; flex-direction: column; gap: 0; }

.archive-year-header {
  font-size: 1.5rem;
  font-weight: 750;
  color: var(--text-h);
  letter-spacing: -0.02em;
  padding: 1.5rem 0 1rem;
  position: relative;
}
.archive-year-header:not(:first-child) {
  margin-top: 0.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

.archive-month-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  margin: 0.25rem 0;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  z-index: 1;
  background: var(--bg-card);
  border: 1px solid var(--border);
}
.archive-month-bar:hover {
  border-color: var(--accent);
  box-shadow: var(--shadow-sm);
}
.archive-month-bar.expanded {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.archive-month-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
}
.archive-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--border);
  border: 2px solid var(--bg);
  flex-shrink: 0;
  transition: all 0.3s ease;
}
.archive-dot.active {
  background: var(--accent);
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-ring);
}
.timeline-line {
  display: none;
}

.archive-month-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-h);
}

.archive-month-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.archive-count {
  font-size: 0.78rem;
  color: var(--accent);
  background: var(--accent-bg);
  padding: 0.2rem 0.75rem;
  border-radius: 999px;
  font-weight: 600;
}
.archive-chevron {
  color: var(--text-muted);
  transition: transform 0.3s ease;
}
.archive-chevron.rotated {
  transform: rotate(180deg);
  color: var(--accent);
}

/* Animated article list */
.archive-articles {
  overflow: hidden;
  padding: 0.25rem 0 0.5rem 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.archive-article-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 1rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s ease;
  animation: articleItemIn 0.3s ease backwards;
  background: var(--bg-subtle);
  border: 1px solid transparent;
}
.archive-article-item:hover {
  background: var(--accent-bg);
  border-color: var(--accent);
  transform: translateX(4px);
}

@keyframes articleItemIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

.article-item-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
  opacity: 0.5;
}
.archive-article-item:hover .article-item-dot {
  opacity: 1;
}

.article-item-title {
  flex: 1;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text);
  line-height: 1.4;
  transition: color 0.2s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.archive-article-item:hover .article-item-title {
  color: var(--accent);
}

.article-item-arrow {
  color: var(--text-muted);
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s;
  flex-shrink: 0;
}
.archive-article-item:hover .article-item-arrow {
  opacity: 1;
  transform: translateX(0);
  color: var(--accent);
}

/* Transition */
.article-slide-enter-active,
.article-slide-leave-active {
  transition: all 0.3s ease;
}
.article-slide-enter-from,
.article-slide-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
.article-slide-enter-to,
.article-slide-leave-from {
  opacity: 1;
  max-height: 500px;
}

@media (max-width: 768px) {
  .archive-articles { padding-left: 1.5rem; }
}
</style>
