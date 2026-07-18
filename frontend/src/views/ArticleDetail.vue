<template>
  <div class="article-detail-page">
    <div v-if="loading" class="loading-spinner">加载中...</div>
    <div v-else-if="!article" class="empty-state">文章不存在</div>

    <article v-else class="article-container">
      <!-- Header -->
      <header class="article-header">
        <div class="article-breadcrumb">
          <router-link to="/home">首页</router-link>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          <router-link v-if="article.category_name" :to="'/articles?category=' + article.category">{{ article.category_name }}</router-link>
          <span>{{ article.title }}</span>
        </div>
        <h1 class="article-title">{{ article.title }}</h1>
        <div class="article-meta">
          <span class="meta-item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>{{ article.author_name }}</span>
          <span class="meta-sep">·</span>
          <span class="meta-item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>{{ formatDate(article.created_at) }}</span>
          <template v-if="article.created_at !== article.updated_at">
            <span class="meta-sep">·</span>
            <span class="meta-item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>更新于 {{ formatDate(article.updated_at) }}</span>
          </template>
          <span class="meta-sep">·</span>
          <span class="meta-item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>{{ article.view_count }} 阅读</span>
          <span class="meta-sep">·</span>
          <span class="meta-item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>{{ article.word_count }} 字</span>
        </div>
        <div v-if="article.tags.length" class="article-tags">
          <span v-for="tag in article.tags" :key="tag.id" class="blog-tag">#{{ tag.name }}</span>
        </div>
      </header>

      <!-- Cover image -->
      <div v-if="article.cover_image" class="article-cover">
        <img :src="article.cover_image" :alt="article.title" />
      </div>

      <div class="article-layout">
        <!-- TOC sidebar -->
        <aside v-if="article.table_of_contents.length" class="toc-sidebar">
          <div class="toc-inner">
            <h4 class="toc-title">目录</h4>
            <nav class="toc-links">
              <a v-for="item in article.table_of_contents" :key="item.id" :href="'#' + item.id" :style="{ paddingLeft: (item.level - 1) * 12 + 'px' }" class="toc-link">{{ item.text }}</a>
            </nav>
          </div>
        </aside>

        <!-- Content -->
        <div class="article-content markdown-body" v-html="renderedContent"></div>
      </div>

      <!-- Previous / Next navigation -->
      <nav class="article-nav" v-if="article.previous_article || article.next_article">
        <router-link
          v-if="article.previous_article"
          :to="'/' + (article.article_type === 'diary' ? 'diary' : 'article') + '/' + article.previous_article.id"
          class="article-nav-link prev"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          <div class="nav-text">
            <span class="nav-label">上一篇</span>
            <span class="nav-title">{{ article.previous_article.title }}</span>
          </div>
        </router-link>
        <span v-else class="article-nav-link placeholder"></span>

        <router-link
          v-if="article.next_article"
          :to="'/' + (article.article_type === 'diary' ? 'diary' : 'article') + '/' + article.next_article.id"
          class="article-nav-link next"
        >
          <div class="nav-text">
            <span class="nav-label">下一篇</span>
            <span class="nav-title">{{ article.next_article.title }}</span>
          </div>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </router-link>
        <span v-else class="article-nav-link placeholder"></span>
      </nav>

      <!-- Comments -->
      <section class="comments-section">
        <h3 class="comments-title"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>评论 ({{ article.comments.length }})</h3>

        <form @submit.prevent="submitComment" class="comment-form">
          <div class="form-row">
            <input v-model="commentForm.nickname" type="text" placeholder="昵称 *" required class="blog-input" />
            <input v-model="commentForm.email" type="email" placeholder="邮箱 *" required class="blog-input" />
          </div>
          <textarea v-model="commentForm.content" placeholder="写下你的评论..." required class="blog-input" style="min-height:100px;resize:vertical;margin-bottom:0.75rem"></textarea>
          <button type="submit" class="blog-btn blog-btn-primary">发表评论</button>
        </form>

        <div class="comments-list">
          <div v-for="comment in article.comments" :key="comment.id" class="comment-item">
            <div class="comment-avatar">{{ comment.nickname.charAt(0).toUpperCase() }}</div>
            <div class="comment-body">
              <div class="comment-header">
                <span class="comment-nickname">{{ comment.nickname }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              </div>
              <p class="comment-content">{{ comment.content }}</p>
              <div v-if="comment.replies.length" class="replies">
                <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                  <div class="comment-header">
                    <span class="comment-nickname">{{ reply.nickname }}</span>
                    <span class="comment-date">{{ formatDate(reply.created_at) }}</span>
                  </div>
                  <p class="comment-content">{{ reply.content }}</p>
                </div>
              </div>
            </div>
          </div>
          <div v-if="article.comments.length === 0" class="empty-state" style="padding:2rem">暂无评论，快来发表第一条评论吧</div>
        </div>
      </section>
    </article>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useBlogStore } from '../stores/blog'
import { createComment } from '../api/blog'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

const route = useRoute()
const blogStore = useBlogStore()

const commentForm = ref({ nickname: '', email: '', content: '' })
const article = computed(() => blogStore.currentArticle)
const loading = computed(() => blogStore.loading)

const renderedContent = computed(() => {
  if (!article.value) return ''
  try {
    return marked.parse(article.value.content) as string
  } catch (error) {
    console.error('Markdown 渲染失败:', error)
    return article.value.content
  }
})

const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })

const submitComment = async () => {
  try {
    await createComment({ article: article.value!.id, ...commentForm.value })
    commentForm.value = { nickname: '', email: '', content: '' }
    await blogStore.fetchArticleDetail(Number(route.params.id))
  } catch (e) { console.error('评论失败:', e) }
}

onMounted(async () => { await blogStore.fetchArticleDetail(Number(route.params.id)) })

watch(article, (a) => {
  if (a) {
    document.title = (a.seo_title || a.title) + ' - ' + (blogStore.siteConfig?.site_title || 'Blog')
    let md = document.querySelector('meta[name="description"]') as HTMLMetaElement
    if (!md) { md = document.createElement('meta'); md.setAttribute('name', 'description'); document.head.appendChild(md) }
    md.setAttribute('content', a.seo_description || a.summary || a.title)
  }
}, { immediate: true })
</script>

<style scoped>
.article-detail-page { max-width: 900px; margin: 0 auto; }

.article-container {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 2.5rem;
}

/* Breadcrumb */
.article-breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
  flex-wrap: wrap;
}
.article-breadcrumb a { color: var(--text-muted); }
.article-breadcrumb a:hover { color: var(--accent); }
.article-breadcrumb svg { flex-shrink: 0; }
.article-breadcrumb span { color: var(--text); font-weight: 500; }

/* Header */
.article-header { margin-bottom: 1.5rem; }
.article-title { font-size: 2rem; font-weight: 750; margin: 0 0 1rem; letter-spacing: -0.02em; line-height: 1.3; }
.article-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}
.meta-item { display: inline-flex; align-items: center; gap: 0.25rem; }
.meta-sep { color: var(--border); }
.article-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }

/* Cover */
.article-cover { margin-bottom: 2rem; border-radius: var(--radius-lg); overflow: hidden; }
.article-cover img { width: 100%; display: block; }

/* Layout with optional TOC */
.article-layout { display: flex; gap: 2rem; }
.article-content { flex: 1; min-width: 0; }
.toc-sidebar {
  display: none;
  width: 200px;
  flex-shrink: 0;
}
.toc-inner {
  position: sticky;
  top: 5.5rem;
}
.toc-title { font-size: 0.75rem; font-weight: 650; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin: 0 0 0.75rem; }
.toc-links { display: flex; flex-direction: column; gap: 0.25rem; }
.toc-link {
  font-size: 0.8rem;
  color: var(--text);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  transition: all 0.15s;
  text-decoration: none;
  line-height: 1.4;
  border-left: 2px solid transparent;
}
.toc-link:hover { color: var(--accent); background: var(--accent-bg); border-left-color: var(--accent); }

@media (min-width: 1100px) {
  .toc-sidebar { display: block; }
}

/* Content typography */
.article-content { font-size: 1rem; line-height: 1.8; color: var(--text-h); }
.article-content :deep(p) { margin-bottom: 1.25rem; }
.article-content :deep(h1), .article-content :deep(h2), .article-content :deep(h3), .article-content :deep(h4) { margin-top: 2rem; margin-bottom: 0.75rem; scroll-margin-top: 4.5rem; }
.article-content :deep(h2) { font-size: 1.375rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }
.article-content :deep(blockquote) { margin: 1.5rem 0; padding: 0.75rem 1.25rem; border-left: 3px solid var(--accent); background: var(--accent-bg); border-radius: 0 var(--radius) var(--radius) 0; }
.article-content :deep(blockquote p) { margin: 0; color: var(--text); }
.article-content :deep(ul), .article-content :deep(ol) { padding-left: 1.5rem; margin-bottom: 1.25rem; }
.article-content :deep(li) { margin-bottom: 0.25rem; }
.article-content :deep(pre) { margin: 1.25rem 0; border-radius: var(--radius); font-size: 0.85rem; }
.article-content :deep(img) { margin: 1.5rem 0; border-radius: var(--radius-lg); }
.article-content :deep(a) { text-decoration: underline; text-underline-offset: 2px; }
.article-content :deep(table) { width: 100%; border-collapse: collapse; margin: 1.25rem 0; font-size: 0.875rem; }
.article-content :deep(th), .article-content :deep(td) { border: 1px solid var(--border); padding: 0.5rem 0.75rem; text-align: left; }
.article-content :deep(th) { background: var(--accent-bg); font-weight: 600; }

/* Article nav (prev/next) */
.article-nav {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 2.5rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border);
}
.article-nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  text-decoration: none;
  transition: all 0.2s;
}
.article-nav-link:hover { border-color: var(--accent); background: var(--accent-bg); }
.article-nav-link.prev { text-align: left; }
.article-nav-link.next { text-align: right; justify-content: flex-end; }
.article-nav-link.placeholder { visibility: hidden; }
.nav-text { display: flex; flex-direction: column; min-width: 0; }
.nav-label { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem; }
.nav-title { font-size: 0.85rem; font-weight: 550; color: var(--text-h); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 250px; }
.article-nav-link svg { flex-shrink: 0; color: var(--text-muted); }
.article-nav-link:hover svg { color: var(--accent); }

/* Comments */
.comments-section { margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); }
.comments-title { display: flex; align-items: center; gap: 0.5rem; font-size: 1.15rem; margin: 0 0 1.5rem; color: var(--text-h); }
.comments-title svg { color: var(--accent); }

.comment-form { margin-bottom: 2rem; }
.form-row { display: flex; gap: 0.75rem; margin-bottom: 0.75rem; }
.form-row .blog-input { flex: 1; }
.comment-form .blog-btn { margin-top: 0.5rem; }

.comments-list { display: flex; flex-direction: column; gap: 1rem; }
.comment-item { display: flex; gap: 0.75rem; padding: 1rem; background: var(--bg-subtle); border-radius: var(--radius); }
.comment-avatar {
  width: 36px; height: 36px; border-radius: 50%; background: var(--gradient-primary);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem; font-weight: 700; flex-shrink: 0;
}
.comment-body { flex: 1; min-width: 0; }
.comment-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.comment-nickname { font-weight: 600; font-size: 0.85rem; color: var(--text-h); }
.comment-date { font-size: 0.75rem; color: var(--text-muted); }
.comment-content { font-size: 0.875rem; color: var(--text); line-height: 1.6; margin: 0; }
.replies { margin-top: 0.75rem; padding-left: 1rem; border-left: 2px solid var(--border); display: flex; flex-direction: column; gap: 0.75rem; }
.reply-item { padding: 0.75rem; background: var(--bg-card); border-radius: var(--radius-sm); }

@media (max-width: 768px) {
  .article-container { padding: 1.25rem; border-radius: var(--radius); }
  .article-title { font-size: 1.5rem; }
  .article-meta { gap: 0.2rem; }
  .form-row { flex-direction: column; }
  .comment-avatar { width: 30px; height: 30px; font-size: 0.7rem; }
}
</style>
