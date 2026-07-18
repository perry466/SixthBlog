<template>
  <div class="articles-page">
    <h1 class="page-title">{{ pageTitle }}</h1>

    <div class="filters">
      <div class="search-wrapper">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
        <input v-model="searchQuery" type="text" placeholder="搜索文章..." @keyup.enter="handleSearch" class="blog-input" style="border:none;background:none;padding-left:0.25rem" />
      </div>
      <select v-model="selectedCategory" @change="handleFilter" class="blog-input blog-select" style="width:auto;min-width:130px">
        <option value="">全部分类</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.slug">{{ cat.name }}</option>
      </select>
      <select v-model="sortBy" @change="handleFilter" class="blog-input blog-select" style="width:auto;min-width:130px">
        <option value="-published_at">最新发布</option>
        <option value="-view_count">最多阅读</option>
        <option value="-updated_at">最近更新</option>
        <option value="published_at">最早发布</option>
      </select>
    </div>

    <div v-if="loading" class="loading-spinner">加载中...</div>
    <div v-else-if="articles.length === 0" class="empty-state">暂无文章</div>
    <div v-else class="articles-list">
      <article v-for="article in articles" :key="article.id" class="article-card" @click="goToArticle(article.id)">
        <div class="article-body">
          <div class="article-meta-top">
            <span v-if="article.category_name" class="article-category">{{ article.category_name }}</span>
            <span class="article-date">{{ formatDate(article.created_at) }}</span>
          </div>
          <h2 class="article-title">{{ article.title }}</h2>
          <p class="article-summary">{{ article.summary }}</p>
          <div class="article-footer">
            <div class="article-stats">
              <span>{{ article.view_count }} 阅读</span>
              <span>{{ article.word_count }} 字</span>
            </div>
            <div v-if="article.tags.length" class="article-tags">
              <span v-for="tag in article.tags.slice(0,3)" :key="tag.id" class="blog-tag">#{{ tag.name }}</span>
            </div>
          </div>
        </div>
      </article>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1">上一页</button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages">下一页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBlogStore } from '../stores/blog'

const router = useRouter()
const route = useRoute()
const blogStore = useBlogStore()
const searchQuery = ref('')
const selectedCategory = ref('')  // 逗号分隔多个 slug
const sortBy = ref('-published_at')
const currentPage = ref(1)

const articles = computed(() => blogStore.articles)
const categories = computed(() => blogStore.categories)
const loading = computed(() => blogStore.loading)
const total = computed(() => blogStore.total)
const totalPages = computed(() => Math.ceil(total.value / 10))

// 页面标题：支持多分类显示
const pageTitle = computed(() => {
  if (selectedCategory.value && categories.value.length) {
    const slugs = selectedCategory.value.split(',').map(s => s.trim()).filter(Boolean)
    if (slugs.length === 1) {
      const cat = categories.value.find((c: any) => c.slug === slugs[0])
      if (cat) return cat.name
    } else if (slugs.length > 1) {
      const names = slugs
        .map(s => categories.value.find((c: any) => c.slug === s))
        .filter(Boolean)
        .map((c: any) => c.name)
      if (names.length) return names.join(' + ')
    }
  }
  return '全部文章'
})

const fetchArticles = async () => {
  const p: any = { page: currentPage.value, ordering: sortBy.value }
  if (searchQuery.value) p.search = searchQuery.value
  if (selectedCategory.value) p.category_slug = selectedCategory.value
  // 同步 URL query params
  router.replace({ query: { ...route.query, category_slug: selectedCategory.value || undefined, page: currentPage.value > 1 ? String(currentPage.value) : undefined } })
  await blogStore.fetchArticles(p)
}
const handleSearch = () => { currentPage.value = 1; fetchArticles() }
const handleFilter = () => { currentPage.value = 1; fetchArticles() }
const goToPage = (page: number) => { if (page >= 1 && page <= totalPages.value) { currentPage.value = page; fetchArticles() } }
const goToArticle = (id: number) => router.push('/article/' + id)
const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN')

// 监听外部路由变化（如点击不同分类菜单项），避免组件复用时不刷新
watch(
  () => route.query.category_slug,
  (newSlug) => {
    if (newSlug && newSlug !== selectedCategory.value) {
      selectedCategory.value = newSlug as string
      currentPage.value = 1
      if (categories.value.length) fetchArticles()
    }
  }
)

onMounted(async () => {
  await blogStore.fetchCategories()
  // 从 URL query 读取初始筛选参数（逗号分隔多分类）
  if (route.query.category_slug) {
    selectedCategory.value = route.query.category_slug as string
  }
  await fetchArticles()
})
</script>

<style scoped>
.articles-page { max-width: 900px; margin: 0 auto; }

.filters {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 2rem;
  align-items: center;
}
.search-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.875rem;
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  transition: all 0.2s;
}
.search-wrapper:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-ring); }
.search-wrapper svg { color: var(--text-muted); flex-shrink: 0; }

.articles-list { display: flex; flex-direction: column; gap: 1rem; }

.article-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.25s ease;
}
.article-card:hover {
  box-shadow: var(--shadow-md);
  border-color: transparent;
  transform: translateY(-2px);
}
.article-body { padding: 1.25rem 1.5rem; }

.article-meta-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
}
.article-category { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); background: var(--accent-bg); padding: 0.15rem 0.6rem; border-radius: 999px; }
.article-date { font-size: 0.78rem; color: var(--text-muted); }

.article-title { font-size: 1.15rem; font-weight: 650; color: var(--text-h); margin: 0 0 0.5rem; line-height: 1.4; }
.article-summary { font-size: 0.85rem; color: var(--text); line-height: 1.6; margin: 0 0 1rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

.article-footer { display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; }
.article-stats { display: flex; gap: 1rem; font-size: 0.78rem; color: var(--text-muted); }
.article-tags { display: flex; gap: 0.25rem; flex-wrap: wrap; justify-content: flex-end; }
</style>
