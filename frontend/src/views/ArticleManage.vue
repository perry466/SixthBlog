<template>
  <div class="manage-page">
    <div class="page-header">
      <h1 class="page-title">文章管理</h1>
      <router-link to="/sixth-admin/articles/new" class="btn-create">+ 创建文章</router-link>
    </div>

    <div v-if="toast" :class="['toast', toastType]">{{ toast }}</div>

    <!-- 筛选栏 -->
    <div class="filters">
      <select v-model="filterStatus" @change="fetchArticles">
        <option value="">全部状态</option>
        <option value="published">已发布</option>
        <option value="draft">草稿</option>
        <option value="archived">已归档</option>
      </select>
      <select v-model="filterType" @change="fetchArticles">
        <option value="">全部类型</option>
        <option value="article">文章</option>
        <option value="diary">日记</option>
        <option value="about">关于</option>
      </select>
      <input v-model="searchQuery" type="text" placeholder="搜索标题..." @keyup.enter="fetchArticles" class="search-input" />
      <button @click="fetchArticles" class="btn-search">搜索</button>
    </div>

    <!-- 文章列表 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="articles.length === 0" class="empty">暂无文章</div>
    <div v-else class="article-table">
      <div v-for="article in articles" :key="article.id" class="article-row">
        <div class="article-info">
          <h3 class="article-title">{{ article.title }}</h3>
          <div class="article-meta">
            <span :class="['status-badge', article.status]">{{ statusLabel(article.status) }}</span>
            <span class="type-badge">{{ typeLabel(article.article_type) }}</span>
            <span v-if="article.is_featured" class="featured-badge">置顶</span>
            <span v-if="article.category_name">{{ article.category_name }}</span>
            <span>{{ formatDate(article.created_at) }}</span>
            <span>{{ article.view_count }} 阅读</span>
            <span>{{ article.word_count }} 字</span>
          </div>
        </div>
        <div class="article-actions">
          <button @click="editArticle(article.id)" class="btn-action btn-edit">编辑</button>
          <button v-if="article.status !== 'published'" @click="changeStatus(article.id, 'published')" class="btn-action btn-publish">发布</button>
          <button v-if="article.status !== 'archived'" @click="changeStatus(article.id, 'archived')" class="btn-action btn-archive">归档</button>
          <button v-if="article.status !== 'draft'" @click="changeStatus(article.id, 'draft')" class="btn-action btn-draft">草稿</button>
          <button @click="toggleFeatured(article.id, article.is_featured)" class="btn-action btn-feature">
            {{ article.is_featured ? '取消置顶' : '置顶' }}
          </button>
          <button @click="confirmDelete(article.id, article.title)" class="btn-action btn-delete">删除</button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1">上一页</button>
      <span>第 {{ currentPage }} / {{ totalPages }} 页 (共 {{ total }} 篇)</span>
      <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages">下一页</button>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showDeleteDialog" class="modal-overlay" @click.self="showDeleteDialog = false">
      <div class="modal">
        <h3>确认删除</h3>
        <p>确定要删除文章「{{ deleteTarget.title }}」吗？此操作不可恢复。</p>
        <div class="modal-actions">
          <button @click="doDelete" class="btn-delete-confirm">确认删除</button>
          <button @click="showDeleteDialog = false" class="btn-cancel">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { getArticles, updateArticle, deleteArticle } from '../api/blog'

const router = useRouter()
const userStore = useUserStore()

const articles = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const filterStatus = ref('')
const filterType = ref('')
const searchQuery = ref('')
const toast = ref('')
const toastType = ref('')

const showDeleteDialog = ref(false)
const deleteTarget = ref({ id: 0, title: '' })

const totalPages = computed(() => Math.ceil(total.value / 10))

const showToast = (msg: string, type = 'success') => {
  toast.value = msg
  toastType.value = type
  setTimeout(() => { toast.value = '' }, 3000)
}

const statusLabel = (s: string) => ({ published: '已发布', draft: '草稿', archived: '已归档' }[s] || s)
const typeLabel = (t: string) => ({ article: '文章', diary: '日记', about: '关于' }[t] || t)
const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN')

const fetchArticles = async () => {
  loading.value = true
  const params: any = { page: currentPage.value, scope: 'all' }
  if (filterStatus.value) params.status = filterStatus.value
  if (filterType.value) params.article_type = filterType.value
  if (searchQuery.value) params.search = searchQuery.value
  try {
    const data = await getArticles(params) as any
    articles.value = data.results || []
    total.value = data.count || 0
  } catch {
    showToast('获取文章列表失败', 'error')
  } finally {
    loading.value = false
  }
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchArticles()
  }
}

const editArticle = (id: number) => router.push(`/sixth-admin/articles/${id}/edit`)

const changeStatus = async (id: number, status: string) => {
  try {
    await updateArticle(id, { status })
    showToast('状态已更新')
    fetchArticles()
  } catch {
    showToast('更新失败', 'error')
  }
}

const toggleFeatured = async (id: number, current: boolean) => {
  try {
    await updateArticle(id, { is_featured: !current })
    showToast(current ? '已取消置顶' : '已置顶')
    fetchArticles()
  } catch {
    showToast('操作失败', 'error')
  }
}

const confirmDelete = (id: number, title: string) => {
  deleteTarget.value = { id, title }
  showDeleteDialog.value = true
}

const doDelete = async () => {
  try {
    await deleteArticle(deleteTarget.value.id)
    showToast('文章已删除')
    showDeleteDialog.value = false
    fetchArticles()
  } catch {
    showToast('删除失败', 'error')
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  fetchArticles()
})
</script>

<style scoped>
.manage-page { max-width: 1200px; margin: 0 auto; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title { color: var(--text-h); margin: 0; }

.btn-create {
  padding: 10px 20px;
  background: var(--accent);
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
}

.toast {
  padding: 12px 24px;
  border-radius: 8px;
  margin-bottom: 16px;
  text-align: center;
  font-size: 14px;
}
.toast.success { background: #d4edda; color: #155724; }
.toast.error { background: #f8d7da; color: #721c24; }

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filters select, .search-input {
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text-h);
  font-size: 14px;
}

.search-input { flex: 1; min-width: 200px; }

.btn-search {
  padding: 8px 16px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.loading, .empty {
  text-align: center;
  padding: 48px;
  color: var(--text);
  font-size: 18px;
}

.article-table { display: flex; flex-direction: column; gap: 12px; }

.article-row {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.article-info { flex: 1; min-width: 0; }

.article-title {
  font-size: 18px;
  color: var(--text-h);
  margin: 0 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: var(--text);
}

.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}
.status-badge.published { background: #d4edda; color: #155724; }
.status-badge.draft { background: #fff3cd; color: #856404; }
.status-badge.archived { background: #e2e3e5; color: #383d41; }

.type-badge, .featured-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  background: var(--accent-bg);
  color: var(--accent);
}

.article-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.btn-action {
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg);
  color: var(--text);
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}
.btn-action:hover { background: var(--accent-bg); }
.btn-edit { color: var(--accent); border-color: var(--accent); }
.btn-delete { color: #dc3545; border-color: #dc3545; }

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}
.pagination button {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
  cursor: pointer;
}
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg);
  border-radius: 12px;
  padding: 32px;
  max-width: 400px;
  width: 90%;
}
.modal h3 { margin: 0 0 16px; color: var(--text-h); }
.modal p { color: var(--text); margin-bottom: 24px; }

.modal-actions { display: flex; gap: 12px; justify-content: flex-end; }

.btn-delete-confirm {
  padding: 8px 20px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-cancel {
  padding: 8px 20px;
  background: var(--social-bg);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .article-row { flex-direction: column; align-items: flex-start; }
  .article-actions { width: 100%; justify-content: flex-start; }
}
</style>
