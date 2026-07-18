<template>
  <div class="about-page">
    <div v-if="loading" class="loading-spinner">加载中...</div>
    <div v-else-if="!article" class="empty-state">关于页面尚未创建</div>
    <div v-else class="about-content-wrapper">
      <article class="about-content markdown-body" v-html="renderedContent"></article>
      <section v-if="socialLinks && Object.keys(socialLinks).length > 0" class="social-section">
        <h3 class="social-title">社交账号</h3>
        <div class="social-links">
          <a v-for="(url, name) in socialLinks" :key="name" :href="url" target="_blank" rel="noopener" class="social-link">
            <span>{{ name }}</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          </a>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getAbout } from '../api/blog'
import { useBlogStore } from '../stores/blog'
import { marked } from 'marked'

const blogStore = useBlogStore()
const article = ref<any>(null)
const loading = ref(true)
const socialLinks = computed(() => blogStore.siteConfig?.social_links || {})

const renderedContent = computed(() => {
  if (!article.value) return ''
  try {
    return marked.parse(article.value.content) as string
  } catch (error) {
    console.error('Markdown 渲染失败:', error)
    return article.value.content
  }
})

onMounted(async () => {
  await blogStore.fetchSiteConfig()
  try { article.value = await getAbout() } catch { /* empty */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.about-page { max-width: 900px; margin: 0 auto; }
.about-content-wrapper { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 2.5rem; }
.about-content { font-size: 1rem; line-height: 1.8; color: var(--text-h); }
.about-content :deep(h1), .about-content :deep(h2), .about-content :deep(h3) { margin-top: 1.5rem; margin-bottom: 0.75rem; }
.about-content :deep(p) { margin-bottom: 1.25rem; }
.about-content :deep(img) { max-width: 100%; border-radius: var(--radius-lg); margin: 1rem 0; }
.about-content :deep(a) { text-decoration: underline; text-underline-offset: 2px; }
.social-section { margin-top: 2.5rem; padding-top: 2rem; border-top: 1px solid var(--border); }
.social-title { font-size: 1rem; margin: 0 0 1rem; }
.social-links { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.social-link {
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.4rem 0.875rem; background: var(--accent-bg); color: var(--accent);
  border-radius: 999px; font-size: 0.82rem; font-weight: 550; text-decoration: none;
  transition: all 0.2s;
}
.social-link:hover { background: var(--accent); color: #fff; }
.social-link svg { transition: transform 0.2s; }
.social-link:hover svg { transform: translate(2px, -2px); }
@media (max-width: 768px) { .about-content-wrapper { padding: 1.25rem; } }
</style>