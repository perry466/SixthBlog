<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="admin-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <router-link to="/sixth-admin" class="sidebar-logo">
          <div class="logo-icon"></div>
          <span v-if="!sidebarCollapsed" class="logo-text">SixthBlog</span>
        </router-link>
        <button class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 19l-7-7 7-7M18 19l-7-7 7-7"/></svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/sixth-admin" class="nav-item" :class="{ active: $route.path === '/sixth-admin' }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
          <span v-if="!sidebarCollapsed">仪表盘</span>
        </router-link>

        <router-link to="/sixth-admin/articles" class="nav-item" :class="{ active: $route.path.startsWith('/sixth-admin/articles') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          <span v-if="!sidebarCollapsed">文章管理</span>
        </router-link>

        <router-link to="/sixth-admin/comments" class="nav-item" :class="{ active: $route.path.startsWith('/sixth-admin/comments') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
          <span v-if="!sidebarCollapsed">评论管理</span>
        </router-link>

        <router-link to="/sixth-admin/guestbook" class="nav-item" :class="{ active: $route.path.startsWith('/sixth-admin/guestbook') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          <span v-if="!sidebarCollapsed">留言审核</span>
        </router-link>

        <router-link to="/sixth-admin/categories" class="nav-item" :class="{ active: $route.path.startsWith('/sixth-admin/categories') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 4h6v6H4zM4 14h6v6H4zM14 4h6v6h-6zM14 14h6v6h-6z"/></svg>
          <span v-if="!sidebarCollapsed">分类管理</span>
        </router-link>

        <router-link to="/sixth-admin/menus" class="nav-item" :class="{ active: $route.path.startsWith('/sixth-admin/menus') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
          <span v-if="!sidebarCollapsed">菜单管理</span>
        </router-link>

        <router-link to="/sixth-admin/settings" class="nav-item" :class="{ active: $route.path.startsWith('/sixth-admin/settings') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
          <span v-if="!sidebarCollapsed">站点设置</span>
        </router-link>

        <router-link to="/sixth-admin/users" class="nav-item" :class="{ active: $route.path.startsWith('/sixth-admin/users') }">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
          <span v-if="!sidebarCollapsed">用户管理</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="nav-item theme-item" @click="toggleTheme">
          <svg v-if="isDark" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
          <span v-if="!sidebarCollapsed">{{ isDark ? '亮色模式' : '暗色模式' }}</span>
        </button>

        <div class="sidebar-user">
          <span v-if="!sidebarCollapsed" class="sidebar-username">{{ user?.username }}</span>
          <button @click="handleLogout" class="nav-item logout-item" :title="sidebarCollapsed ? '退出' : ''">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4m7 14l5-5-5-5m5 5H9"/></svg>
            <span v-if="!sidebarCollapsed">退出登录</span>
          </button>
        </div>

        <router-link to="/home" class="nav-item">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
          <span v-if="!sidebarCollapsed">返回前台</span>
        </router-link>
      </div>
    </aside>

    <!-- 主区域 -->
    <div class="admin-main">
      <main class="admin-content">
        <!-- 验证登录中 -->
        <div v-if="checking" class="loading-spinner">验证登录状态...</div>
        <!-- 已登录 -->
        <router-view v-else v-slot="{ Component: C }">
          <transition name="page" mode="out-in">
            <component :is="C" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const user = computed(() => userStore.user)
const isLoggedIn = computed(() => userStore.isLoggedIn)
const sidebarCollapsed = ref(false)
const checking = ref(true)  // 正在验证登录状态

const isDark = computed(() => {
  return document.documentElement.getAttribute('data-theme') === 'dark'
    || (!document.documentElement.getAttribute('data-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)
})

function toggleTheme() {
  const root = document.documentElement
  const current = root.getAttribute('data-theme')
  const next = current === 'dark' ? 'light' : 'dark'
  root.setAttribute('data-theme', next)
  localStorage.setItem('theme', next)
}

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}

// 恢复登录状态 + 鉴权
onMounted(async () => {
  // 先从 localStorage 恢复用户名（仅用于显示）
  userStore.restoreFromStorage()
  // 异步验证 session 是否有效
  await userStore.fetchCurrentUser()
  checking.value = false
  if (!userStore.isLoggedIn) {
    router.push('/login')
  }
})

// 监听登出（如 session 过期），自动跳转
watch(isLoggedIn, (val) => {
  if (!val && route.path.startsWith('/sixth-admin')) {
    router.push('/login')
  }
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

/* ===== Sidebar ===== */
.admin-sidebar {
  width: 240px;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 50;
  transition: width 0.25s ease;
  overflow: hidden;
}

.admin-sidebar.collapsed { width: 68px; }

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border);
  height: 56px;
  box-sizing: border-box;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  min-width: 0;
}

.logo-icon {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--gradient-primary);
  flex-shrink: 0;
}

.logo-text {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-h);
  letter-spacing: -0.02em;
  white-space: nowrap;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.sidebar-toggle:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-bg); }

.collapsed .sidebar-toggle svg { transform: rotate(180deg); }

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: var(--radius);
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--text);
  text-decoration: none;
  transition: all 0.2s;
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover { background: var(--accent-bg); color: var(--accent); }

.nav-item.active {
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 600;
}

.nav-item svg { flex-shrink: 0; }

.sidebar-footer {
  padding: 10px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.theme-item { background: none; border: none; width: 100%; cursor: pointer; font-family: inherit; font-size: 0.88rem; }

.sidebar-user { padding: 8px 6px; }

.sidebar-username {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 550;
  padding: 0 8px 6px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.logout-item { width: 100%; background: none; border: none; cursor: pointer; font-family: inherit; font-size: 0.88rem; }
.logout-item:hover { color: #ef4444 !important; background: #fef2f2 !important; }

/* ===== Main ===== */
.admin-main {
  flex: 1;
  margin-left: 240px;
  transition: margin-left 0.25s ease;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.admin-sidebar.collapsed + .admin-main { margin-left: 68px; }

.admin-content {
  flex: 1;
  padding: 28px;
  background: var(--bg);
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  font-size: 0.9rem;
  gap: 0.5rem;
}
.loading-spinner::before {
  content: '';
  width: 20px;
  height: 20px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Page transition */
.page-enter-active, .page-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.page-enter-from { opacity: 0; transform: translateY(6px); }
.page-leave-to { opacity: 0; transform: translateY(-3px); }

/* ===== Mobile ===== */
@media (max-width: 768px) {
  .admin-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    width: 260px !important;
    box-shadow: var(--shadow-lg);
    transition: transform 0.3s ease;
  }
  .admin-sidebar.collapsed { transform: translateX(0); }
  .admin-sidebar.collapsed .sidebar-toggle svg { transform: rotate(0); }

  .admin-main { margin-left: 0 !important; }

  .admin-content { padding: 16px; }
}
</style>
