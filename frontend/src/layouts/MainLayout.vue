<template>
  <div class="main-layout">
    <header class="header" :class="{ 'header-scrolled': scrolled }">
      <div class="header-content">
        <router-link to="/home" class="logo">
          <span class="logo-icon"></span>
          {{ siteTitle }}
        </router-link>

        <nav class="header-nav">
          <template v-for="item in visibleMenuItems" :key="item.id">
            <!-- 有子菜单的项 → 下拉菜单 -->
            <div
              v-if="item.children && item.children.length"
              class="nav-dropdown"
              @mouseenter="openDropdown(item.id)"
              @mouseleave="closeDropdown(item.id)"
            >
              <button
                class="nav-link nav-dropdown-trigger"
                :class="{ active: isChildActive(item) }"
                @click.stop="toggleDropdown(item.id)"
              >
                {{ item.name }}
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-left:4px"><path d="M6 9l6 6 6-6"/></svg>
              </button>
              <transition name="dropdown">
                <div v-if="activeDropdown === item.id" class="dropdown-menu" @click.stop>
                  <router-link
                    v-for="child in item.children"
                    :key="child.id"
                    :to="toRoute(child.url)"
                    class="dropdown-item"
                    @click="closeDropdown(item.id)"
                  >
                    {{ child.name }}
                  </router-link>
                </div>
              </transition>
            </div>
            <!-- 普通菜单项 -->
            <router-link
              v-else
              :to="toRoute(item.url)"
              class="nav-link"
              :class="{ active: isActiveLink(item.url) }"
            >
              {{ item.name }}
            </router-link>
          </template>
        </nav>

        <button class="theme-toggle" @click="toggleTheme" :title="isDark ? '切换亮色模式' : '切换暗色模式'" aria-label="切换主题">
          <svg v-if="isDark" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
        </button>
      </div>
    </header>

    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <transition name="page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>

    <footer class="footer">
      <div class="footer-content">
        <p class="footer-copy">&copy; {{ new Date().getFullYear() }} {{ siteTitle }}. All rights reserved.</p>
        <p class="footer-powered">Powered by SixthBlog</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useBlogStore } from '../stores/blog'

const route = useRoute()
const blogStore = useBlogStore()

interface MenuItemData {
  id: number
  name: string
  url: string
  icon: string
  order: number
  is_active: boolean
  parent: number | null
  children: MenuItemData[]
}

const siteTitle = computed(() => blogStore.siteConfig?.site_title || 'My Blog')
const scrolled = ref(false)
const activeDropdown = ref<number | null>(null)

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

// 默认菜单（作为基底，始终显示）
const defaultMenuItems: MenuItemData[] = [
  { id: -1, name: '首页', url: '/home', icon: '', order: 1, is_active: true, parent: null, children: [] },
  { id: -2, name: '文章', url: '/articles', icon: '', order: 2, is_active: true, parent: null, children: [] },
  { id: -3, name: '归档', url: '/archives', icon: '', order: 3, is_active: true, parent: null, children: [] },
  { id: -4, name: '日记', url: '/diaries', icon: '', order: 4, is_active: true, parent: null, children: [] },
  { id: -5, name: '留言', url: '/guestbook', icon: '', order: 5, is_active: true, parent: null, children: [] },
  { id: -6, name: '关于', url: '/about', icon: '', order: 6, is_active: true, parent: null, children: [] },
]

// 合并：用 API 返回的菜单覆盖默认菜单，同时保留默认菜单中没有的项
const visibleMenuItems = computed<MenuItemData[]>(() => {
  const dbMenus = blogStore.menuItems as unknown as MenuItemData[]
  if (!dbMenus || dbMenus.length === 0) return defaultMenuItems

  // 用 API 菜单构建 Map（name → item）
  const dbMap = new Map<string, MenuItemData>()
  for (const item of dbMenus) {
    dbMap.set(item.name, item)
  }

  // 合并：默认菜单为基础，有同名的用 API 的替换，再加上 API 中额外的新菜单
  const merged = defaultMenuItems.map(d => dbMap.get(d.name) || d)
  for (const item of dbMenus) {
    if (!defaultMenuItems.some(d => d.name === item.name)) {
      merged.push(item)
    }
  }

  // 按 order 排序
  merged.sort((a, b) => a.order - b.order)
  return merged
})

// 判断是否有子菜单项处于活跃状态
const isChildActive = (item: MenuItemData) => {
  if (!item.children) return false
  return item.children.some(child => isActiveLink(child.url))
}

// 解析 URL 字符串，将带 query 参数的转为路由对象（Vue Router 字符串 to 不解析 query）
const toRoute = (url: string): string | { path: string; query: Record<string, string> } => {
  if (!url.includes('?')) return url
  const [path, queryString] = url.split('?')
  if (!queryString) return path
  const query: Record<string, string> = {}
  queryString.split('&').forEach(pair => {
    const [k, v] = pair.split('=')
    if (k) query[decodeURIComponent(k)] = v ? decodeURIComponent(v) : ''
  })
  return { path, query }
}

const openDropdown = (id: number) => {
  activeDropdown.value = id
}

const closeDropdown = (id: number) => {
  if (activeDropdown.value === id) {
    activeDropdown.value = null
  }
}

const toggleDropdown = (id: number) => {
  if (activeDropdown.value === id) {
    activeDropdown.value = null
  } else {
    activeDropdown.value = id
  }
}

// 判断链接是否匹配当前路由（支持 query 参数）
const isActiveLink = (url: string): boolean => {
  // 解析 URL 中的 query 参数
  const [path, queryString] = url.split('?')
  if (route.path !== path) return false
  if (!queryString) return route.path === path || route.path.startsWith(path + '/')
  // 有 query 参数时，检查是否匹配
  const params = new URLSearchParams(queryString)
  for (const [key, val] of params.entries()) {
    if (route.query[key] !== val) return false
  }
  return true
}

onMounted(() => {
  blogStore.fetchSiteConfig()
  blogStore.fetchMenuItems()

  // Restore saved theme
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme)
  }

  // Scroll shadow on header
  const onScroll = () => { scrolled.value = window.scrollY > 10 }
  window.addEventListener('scroll', onScroll, { passive: true })

  // 点击其他地方关闭下拉
  const onDocClick = () => { activeDropdown.value = null }
  document.addEventListener('click', onDocClick)
})
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: box-shadow 0.3s ease;
}
.header-scrolled {
  box-shadow: var(--shadow-sm);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 3.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-h);
  text-decoration: none;
  flex-shrink: 0;
  letter-spacing: -0.02em;
}
.logo-icon {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--gradient-primary);
  flex-shrink: 0;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.nav-link {
  padding: 0.4rem 0.85rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text);
  text-decoration: none;
  border-radius: var(--radius);
  transition: all 0.2s ease;
  white-space: nowrap;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  display: inline-flex;
  align-items: center;
}

.nav-link:hover {
  color: var(--accent);
  background: var(--accent-bg);
}

.nav-link.active {
  color: var(--accent);
  font-weight: 600;
  background: var(--accent-bg);
}

/* Dropdown */
.nav-dropdown {
  position: relative;
}

/* Bridge the gap between trigger and dropdown menu so hover doesn't break */
.nav-dropdown::before {
  content: '';
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  height: 6px;
  z-index: 1;
}

.nav-dropdown-trigger::after {
  content: '';
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  min-width: 160px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 6px;
  z-index: 200;
  animation: dropIn 0.15s ease;
}

@keyframes dropIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

.dropdown-item {
  display: block;
  padding: 0.45rem 0.85rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text);
  text-decoration: none;
  border-radius: var(--radius);
  transition: all 0.15s ease;
  white-space: nowrap;
}

.dropdown-item:hover {
  color: var(--accent);
  background: var(--accent-bg);
}

/* Dropdown transition */
.dropdown-enter-active, .dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.125rem;
  height: 2.125rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s ease;
}
.theme-toggle:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-bg);
}

.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  width: 100%;
  box-sizing: border-box;
}

.footer {
  border-top: 1px solid var(--border);
  background: var(--bg-card);
  padding: 1.5rem 0;
}
.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.footer-copy { margin: 0; font-size: 0.8rem; color: var(--text-muted); }
.footer-powered { margin: 0; font-size: 0.75rem; color: var(--text-muted); opacity: 0.6; }

/* Page transition */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from { opacity: 0; transform: translateY(8px); }
.page-leave-to { opacity: 0; transform: translateY(-4px); }

@media (max-width: 768px) {
  .header-content { padding: 0 1rem; }
  .header-nav { gap: 0; overflow-x: auto; }
  .nav-link { padding: 0.35rem 0.6rem; font-size: 0.8rem; }
  .dropdown-menu { position: static; box-shadow: none; margin-top: 0; border: none; padding-left: 1rem; }
  .footer-content { flex-direction: column; text-align: center; gap: 0.25rem; }
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
