<template>
  <div class="dashboard">
    <h1 class="dash-title">仪表盘</h1>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background:linear-gradient(135deg,#6366f1,#8b5cf6)">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <div class="stat-body">
          <span class="stat-value">{{ stats.total_articles || 0 }}</span>
          <span class="stat-label">文章总数</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background:linear-gradient(135deg,#10b981,#34d399)">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        </div>
        <div class="stat-body">
          <span class="stat-value">{{ stats.total_comments || 0 }}</span>
          <span class="stat-label">评论总数</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background:linear-gradient(135deg,#f59e0b,#fbbf24)">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
        </div>
        <div class="stat-body">
          <span class="stat-value">{{ stats.total_categories || 0 }}</span>
          <span class="stat-label">分类数量</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background:linear-gradient(135deg,#ec4899,#f472b6)">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
        </div>
        <div class="stat-body">
          <span class="stat-value">{{ stats.total_tags || 0 }}</span>
          <span class="stat-label">标签数量</span>
        </div>
      </div>
    </div>

    <!-- 快捷操作 + 最新文章 -->
    <div class="dash-grid">
      <!-- 快捷操作 -->
      <div class="dash-card">
        <h2 class="card-title">快捷操作</h2>
        <div class="quick-actions">
          <router-link to="/sixth-admin/articles/new" class="action-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            <span>写文章</span>
          </router-link>
          <router-link to="/sixth-admin/comments" class="action-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
            <span>审核评论</span>
          </router-link>
          <router-link to="/sixth-admin/guestbook" class="action-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            <span>审核留言</span>
          </router-link>
          <router-link to="/sixth-admin/users" class="action-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
            <span>添加用户</span>
          </router-link>
        </div>
      </div>

      <!-- 最近文章 -->
      <div class="dash-card">
        <h2 class="card-title">最近文章</h2>
        <div v-if="recentArticles.length" class="recent-list">
          <div v-for="a in recentArticles" :key="a.id" class="recent-item">
            <div class="recent-info">
              <span class="recent-title">{{ a.title }}</span>
              <span class="recent-meta">
                <span :class="['status-dot', a.status]"></span>
                {{ statusLabel(a.status) }} · {{ formatDate(a.created_at) }}
              </span>
            </div>
            <router-link :to="'/sixth-admin/articles/' + a.id + '/edit'" class="recent-edit">编辑</router-link>
          </div>
        </div>
        <div v-else class="empty-hint">暂无文章</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getStats, getArticles } from '../../api/blog'

const stats = ref<any>({})
const recentArticles = ref<any[]>([])

const statusLabel = (s: string) => ({ published: '已发布', draft: '草稿', archived: '已归档' }[s] || s)
const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN')

onMounted(async () => {
  try { stats.value = await getStats() } catch { /* empty */ }
  try {
    const data = await getArticles({ page: 1, ordering: '-created_at' }) as any
    recentArticles.value = (data.results || []).slice(0, 6)
  } catch { /* empty */ }
})
</script>

<style scoped>
.dashboard { max-width: 1200px; }

.dash-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-h);
  margin: 0 0 24px;
  letter-spacing: -0.02em;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.25s;
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  border-color: transparent;
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body { display: flex; flex-direction: column; }

.stat-value {
  font-size: 1.5rem;
  font-weight: 750;
  color: var(--text-h);
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 2px;
}

/* Dash grid */
.dash-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
}

.dash-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-h);
  margin: 0 0 16px;
}

/* Quick actions */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 550;
  transition: all 0.2s;
}

.action-item:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-bg);
  transform: translateY(-1px);
}

/* Recent articles */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: var(--radius);
  transition: background 0.15s;
}

.recent-item:hover { background: var(--bg-subtle); }

.recent-info { display: flex; flex-direction: column; gap: 4px; min-width: 0; }

.recent-title {
  font-size: 0.88rem;
  font-weight: 550;
  color: var(--text-h);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-meta { font-size: 0.75rem; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.published { background: #10b981; }
.status-dot.draft { background: #f59e0b; }
.status-dot.archived { background: #94a3b8; }

.recent-edit {
  padding: 5px 12px;
  font-size: 0.78rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-muted);
  text-decoration: none;
  flex-shrink: 0;
  transition: all 0.2s;
}

.recent-edit:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-bg);
}

.empty-hint {
  text-align: center;
  padding: 32px;
  color: var(--text-muted);
  font-size: 0.85rem;
}

@media (max-width: 1024px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .dash-grid { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
  .stats-grid { grid-template-columns: 1fr; }
  .quick-actions { grid-template-columns: 1fr; }
}
</style>
