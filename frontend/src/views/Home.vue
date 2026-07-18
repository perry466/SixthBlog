<template>
  <div class="home-page">
    <!-- Hero / Welcome -->
    <section class="hero-section">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <h1 class="hero-title">{{ welcomeMessage }}</h1>
        <p class="hero-subtitle">{{ siteDescription }}</p>
        <div class="hero-search">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <input v-model="searchQuery" type="text" placeholder="搜索文章..." @keyup.enter="handleSearch" />
        </div>
      </div>
    </section>

    <!-- Category filter -->
    <section class="filter-section">
      <button @click="handleCategoryClick(null)" :class="['filter-chip', { active: !selectedCategory }]">全部</button>
      <button v-for="cat in categories" :key="cat.id" @click="handleCategoryClick(cat.slug)" :class="['filter-chip', { active: selectedCategory === cat.slug }]">{{ cat.name }}</button>
    </section>

    <!-- Article grid -->
    <section class="articles-section">
      <div class="section-header">
        <h2 class="section-title">最新文章</h2>
        <router-link to="/articles" class="section-more">查看全部 &rarr;</router-link>
      </div>

      <div v-if="loading" class="loading-spinner">加载中...</div>
      <div v-else-if="articles.length === 0" class="empty-state">暂无文章</div>
      <div v-else class="articles-grid">
        <article v-for="article in articles" :key="article.id" class="article-card" @click="goToArticle(article.id)">
          <div v-if="article.cover_image" class="article-cover">
            <img :src="article.cover_image" :alt="article.title" loading="lazy" />
          </div>
          <div class="article-content">
            <div class="article-meta-top">
              <span v-if="article.category_name" class="article-category">{{ article.category_name }}</span>
              <span class="article-date">{{ formatDate(article.published_at || article.created_at) }}</span>
            </div>
            <h3 class="article-title">{{ article.title }}</h3>
            <p class="article-summary">{{ article.summary || article.title }}</p>
            <div class="article-footer">
              <div class="article-stats">
                <span class="stat"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>{{ article.view_count }}</span>
                <span class="stat"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>{{ article.comment_count }}</span>
                <span class="stat"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>{{ article.word_count }}</span>
              </div>
              <div v-if="article.tags.length" class="article-tags">
                <span v-for="tag in article.tags.slice(0, 3)" :key="tag.id" class="blog-tag">#{{ tag.name }}</span>
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
    </section>

    <!-- Stats -->
    <section v-if="stats" class="stats-section">
      <div class="stats-grid">
        <div class="stat-card"><span class="stat-number">{{ stats.total_articles }}</span><span class="stat-label">文章</span></div>
        <div class="stat-card"><span class="stat-number">{{ stats.total_comments }}</span><span class="stat-label">评论</span></div>
        <div class="stat-card"><span class="stat-number">{{ stats.total_categories }}</span><span class="stat-label">分类</span></div>
        <div class="stat-card"><span class="stat-number">{{ stats.total_tags }}</span><span class="stat-label">标签</span></div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBlogStore } from '../stores/blog'

const router = useRouter()
const blogStore = useBlogStore()

const searchQuery = ref('')
const selectedCategory = ref<string | null>(null)
const currentPage = ref(1)

const articles = computed(() => blogStore.articles)
const categories = computed(() => blogStore.categories)
const loading = computed(() => blogStore.loading)
const total = computed(() => blogStore.total)
const stats = computed(() => blogStore.stats)
const siteDescription = computed(() => blogStore.siteConfig?.site_description || '')
const totalPages = computed(() => Math.ceil(total.value / 10))

const welcomeMessages = ['欢迎来到我的博客', '记录思考，分享知识', '用文字连接世界', '每一篇都是一次探索']
const welcomeMessage = ref(welcomeMessages[Math.floor(Math.random() * welcomeMessages.length)])

const fetchArticles = async () => {
  const params: any = { page: currentPage.value }
  if (searchQuery.value) params.search = searchQuery.value
  if (selectedCategory.value) params.category__slug = selectedCategory.value
  await blogStore.fetchArticles(params)
}

const handleSearch = () => { currentPage.value = 1; fetchArticles() }
const handleCategoryClick = (slug: string | null) => { selectedCategory.value = slug; currentPage.value = 1; fetchArticles() }
const goToPage = (page: number) => { if (page >= 1 && page <= totalPages.value) { currentPage.value = page; fetchArticles() } }
const goToArticle = (id: number) => { router.push('/article/' + id) }
const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })

onMounted(async () => {
  await blogStore.fetchCategories()
  await blogStore.fetchStats()
  await fetchArticles()
})
</script>

<style scoped>
.home-page { max-width: 1200px; margin: 0 auto; }

/* Hero */
.hero-section {
  position: relative;
  text-align: center;
  padding: 4rem 2rem 3.5rem;
  margin-bottom: 2.5rem;
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border);
}
.hero-bg {
  position: absolute;
  inset: 0;
  background: var(--gradient-header);
  opacity: 0.04;
  pointer-events: none;
}
.hero-content { position: relative; max-width: 640px; margin: 0 auto; }
.hero-title {
  font-size: 2.25rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  color: var(--text-h);
  margin: 0 0 0.75rem;
}
.hero-subtitle {
  font-size: 1.05rem;
  color: var(--text-muted);
  margin: 0 0 1.75rem;
  line-height: 1.6;
}
.hero-search {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  max-width: 440px;
  margin: 0 auto;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 999px;
  padding: 0.5rem 1.25rem;
  transition: all 0.25s ease;
}
.hero-search:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-ring);
  background: var(--bg-card);
}
.hero-search .search-icon { color: var(--text-muted); flex-shrink: 0; }
.hero-search input {
  flex: 1;
  border: none;
  background: none;
  font-size: 0.925rem;
  color: var(--text-h);
  outline: none;
  font-family: inherit;
}
.hero-search input::placeholder { color: var(--text-muted); }

/* Filter chips */
.filter-section {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-bottom: 2.5rem;
}
.filter-chip {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 550;
  border: 1.5px solid var(--border);
  border-radius: 999px;
  background: var(--bg-card);
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-chip:hover { border-color: var(--accent); color: var(--accent); }
.filter-chip.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

/* Section header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.section-title {
  font-size: 1.25rem;
  font-weight: 650;
  margin: 0;
}
.section-more {
  font-size: 0.85rem;
  color: var(--accent);
  font-weight: 550;
  transition: gap 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.section-more:hover { gap: 0.5rem; }

/* Article grid */
.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.5rem;
}
.article-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s ease;
}
.article-card:hover {
  box-shadow: var(--shadow-md);
  border-color: transparent;
  transform: translateY(-3px);
}
.article-cover {
  height: 200px;
  overflow: hidden;
  background: var(--code-bg);
}
.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.article-card:hover .article-cover img { transform: scale(1.05); }

.article-content { padding: 1.25rem 1.5rem 1.5rem; }

.article-meta-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}
.article-category {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent);
  background: var(--accent-bg);
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
}
.article-date {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.article-title {
  font-size: 1.15rem;
  font-weight: 650;
  color: var(--text-h);
  margin: 0 0 0.5rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-summary {
  font-size: 0.85rem;
  color: var(--text);
  line-height: 1.6;
  margin: 0 0 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}
.article-stats {
  display: flex;
  gap: 0.75rem;
}
.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}
.stat svg { width: 13px; height: 13px; }

.article-tags {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

/* Stats section */
.stats-section {
  margin-top: 3rem;
  padding: 2rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}
.stat-card {
  text-align: center;
  padding: 0.5rem;
}
.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 750;
  color: var(--accent);
  letter-spacing: -0.02em;
  margin-bottom: 0.25rem;
}
.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 550;
}

@media (max-width: 768px) {
  .hero-section { padding: 2.5rem 1.25rem 2rem; }
  .hero-title { font-size: 1.625rem; }
  .hero-subtitle { font-size: 0.925rem; }
  .articles-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 1rem; }
  .stat-number { font-size: 1.5rem; }
}
</style>
