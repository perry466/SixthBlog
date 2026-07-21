<template>
  <div class="editor-page">
    <!-- ===== 顶部操作栏 (sticky) ===== -->
    <header class="editor-topbar">
      <div class="topbar-left">
        <button class="topbar-back blog-btn blog-btn-ghost" @click="goBack" title="返回文章列表">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span class="back-text">返回</span>
        </button>
      </div>
      <div class="topbar-center">
        <span class="topbar-title">{{ isEdit ? '编辑文章' : '创建文章' }}</span>
      </div>
      <div class="topbar-right">
        <span v-if="draftSaved" class="draft-indicator" title="草稿已缓存到浏览器本地，未提交到服务器">💾 草稿已缓存</span>
        <button class="blog-btn blog-btn-ghost" @click="saveArticle('draft')" :disabled="saving">
          保存草稿
        </button>
        <button class="blog-btn blog-btn-primary" @click="saveArticle('published')" :disabled="saving">
          {{ saving ? '保存中...' : '发布' }}
        </button>
      </div>
    </header>

    <!-- ===== 标题输入 (sticky) ===== -->
    <div class="editor-title-bar">
      <input
        ref="titleInputRef"
        v-model="form.title"
        type="text"
        placeholder="输入文章标题..."
        :class="['title-input', { 'field-error-input': fieldErrors.title }]"
        @keydown.enter.prevent
        @input="clearFieldError('title')"
      />
      <Transition name="field-error-fade">
        <span v-if="fieldErrors.title" class="field-error-msg">{{ fieldErrors.title }}</span>
      </Transition>
    </div>

    <!-- ===== 主体区域：编辑器 + 右侧面板 ===== -->
    <div class="editor-body">
      <!-- 左侧：Milkdown WYSIWYG 编辑器 -->
      <div ref="contentErrorRef" class="editor-left">
        <MilkdownEditor
          v-model="form.content"
          @image-uploaded="showToast('图片上传成功')"
        />
        <Transition name="field-error-fade">
          <span v-if="fieldErrors.content" class="field-error-msg" style="padding:0 24px 12px">{{ fieldErrors.content }}</span>
        </Transition>
      </div>

      <!-- 右侧：预览 / 设置 (tab 切换) -->
      <div class="editor-right">
        <div class="right-tabs">
          <button
            :class="{ active: rightTab === 'preview' }"
            @click="rightTab = 'preview'"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            预览
          </button>
          <button
            :class="{ active: rightTab === 'settings' }"
            @click="rightTab = 'settings'"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
            文章设置
          </button>
        </div>

        <!-- 预览面板 -->
        <div v-show="rightTab === 'preview'" class="tab-content">
          <div v-if="!form.content" class="preview-empty">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <p>在左侧输入内容后<br/>这里将显示实时预览</p>
          </div>
          <div v-else class="preview markdown-body" v-html="previewHtml"></div>
        </div>

        <!-- 设置面板 -->
        <div v-show="rightTab === 'settings'" class="tab-content settings-panel">
          <div class="setting-group">
            <label class="setting-label">文章类型</label>
            <select v-model="form.article_type" class="blog-input blog-select">
              <option value="article">文章</option>
              <option value="diary">日记</option>
              <option value="about">关于</option>
            </select>
          </div>

          <div class="setting-group">
            <label class="setting-label">分类</label>
            <select v-model="form.category" class="blog-input blog-select">
              <option :value="null">无分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>

          <div class="setting-group">
            <label class="setting-label">标签</label>
            <input
              v-model="tagInput"
              type="text"
              placeholder="多个标签用逗号分隔，如 Vue, Python"
              :class="['blog-input', { 'field-error-input': fieldErrors.tags }]"
              @input="clearFieldError('tags')"
            />
            <Transition name="field-error-fade">
              <span v-if="fieldErrors.tags" class="field-error-msg">{{ fieldErrors.tags }}</span>
            </Transition>
          </div>

          <div class="setting-group">
            <label class="setting-label">状态</label>
            <select v-model="form.status" class="blog-input blog-select">
              <option value="draft">草稿</option>
              <option value="published">已发布</option>
              <option value="archived">已归档</option>
            </select>
          </div>

          <div class="setting-group">
            <label class="setting-label">封面图片</label>
            <div class="cover-area">
              <div class="cover-preview-wrap" @click="triggerCoverUpload">
                <img v-if="coverPreview" :src="coverPreview" class="cover-preview-img" />
                <div v-else class="cover-placeholder">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                  <span>点击上传封面</span>
                </div>
              </div>
              <div class="cover-actions">
                <button type="button" class="blog-btn blog-btn-ghost" style="font-size:0.78rem" @click="showCoverMediaSelector = true">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                  从媒体库选择
                </button>
                <button v-if="coverPreview" type="button" class="blog-btn blog-btn-ghost" style="font-size:0.78rem;color:#dc3545;border-color:#fecaca" @click="clearCover">移除封面</button>
              </div>
            </div>
            <input ref="coverInput" type="file" accept="image/*" hidden @change="handleCoverUpload" />
            <MediaSelector
              :visible="showCoverMediaSelector"
              @close="showCoverMediaSelector = false"
              @selected="handleCoverMediaSelected"
            />
          </div>

          <div class="setting-group">
            <label class="setting-label setting-checkbox">
              <input type="checkbox" v-model="form.is_featured" />
              <span>置顶文章</span>
            </label>
          </div>

          <div class="setting-group">
            <label class="setting-label">SEO 标题</label>
            <input
              v-model="form.seo_title"
              type="text"
              placeholder="留空则使用文章标题"
              class="blog-input"
            />
          </div>

          <div class="setting-group">
            <label class="setting-label">SEO 描述</label>
            <textarea
              v-model="form.seo_description"
              rows="3"
              placeholder="留空则使用文章内容前200字作为摘要"
              class="blog-input"
            ></textarea>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 底部信息栏 (sticky) ===== -->
    <footer class="editor-bottombar">
      <div class="bottombar-left">
        <span class="stat-item">字数 {{ wordCount }}</span>
        <span class="stat-divider"></span>
        <span class="stat-item">字符 {{ charCount }}</span>
        <span class="stat-divider"></span>
        <span class="stat-item">{{ readingTime }}</span>
      </div>
      <div class="bottombar-right">
        <span class="shortcut-hint">
          <kbd>Ctrl</kbd> + <kbd>S</kbd> 保存
        </span>
      </div>
    </footer>

    <!-- ===== 浮动 Toast ===== -->
    <Transition name="toast-float">
      <div v-if="toast" :class="['toast-float', toastType]">
        <span class="toast-icon">
          <svg v-if="toastType === 'success'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
        </span>
        {{ toast }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { getArticleDetail, createArticle, updateArticle, getCategories } from '../api/blog'
import { marked } from 'marked'
import MilkdownEditor from '../components/MilkdownEditor.vue'
import MediaSelector from '../components/MediaSelector.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const articleId = route.params.id ? Number(route.params.id) : null
const isEdit = computed(() => !!articleId)

const contentErrorRef = ref<HTMLDivElement | null>(null)
const titleInputRef = ref<HTMLInputElement | null>(null)
const coverInput = ref<HTMLInputElement | null>(null)

// 表单字段错误记录：fieldName -> errorMessage
const fieldErrors = ref<Record<string, string>>({})

const form = ref({
  title: '',
  content: '',
  summary: '',
  article_type: 'article',
  category: null as number | null,
  status: 'draft',
  is_featured: false,
  seo_title: '',
  seo_description: '',
  cover_image: null as File | null,
})

const tagInput = ref('')
const categories = ref<any[]>([])
const coverPreview = ref<string | null>(null)
const showCoverMediaSelector = ref(false)
const saving = ref(false)
const toast = ref('')
const toastType = ref('success')
const rightTab = ref<'preview' | 'settings'>('preview')
const draftSaved = ref(false)

let autoSaveTimer: ReturnType<typeof setInterval> | null = null

// ========== 计算属性 ==========

const previewHtml = computed(() => {
  if (!form.value.content) return '<p style="color:#999">暂无内容</p>'
  try {
    return marked.parse(form.value.content) as string
  } catch {
    return form.value.content
  }
})

const wordCount = computed(() => {
  const content = form.value.content || ''
  const chineseChars = (content.match(/[一-鿿㐀-䶿]/g) || []).length
  const nonChinese = content.replace(/[一-鿿㐀-䶿]/g, ' ')
  const englishWords = (nonChinese.match(/\b\w+\b/g) || []).length
  return chineseChars + englishWords
})

const charCount = computed(() => {
  return (form.value.content || '').replace(/\s/g, '').length
})

const readingTime = computed(() => {
  const minutes = Math.max(1, Math.ceil(wordCount.value / 300))
  return `约 ${minutes} 分钟`
})

// ========== Toast ==========

const showToast = (msg: string, type = 'success') => {
  toast.value = msg
  toastType.value = type
  setTimeout(() => { toast.value = '' }, 3000)
}

// ========== 封面图片 ==========

const triggerCoverUpload = () => coverInput.value?.click()

const handleCoverUpload = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) {
    // 释放旧 blob URL
    if (coverPreview.value && coverPreview.value.startsWith('blob:')) {
      URL.revokeObjectURL(coverPreview.value)
    }
    form.value.cover_image = file
    coverPreview.value = URL.createObjectURL(file)
  }
}

// 从媒体库选择封面
const handleCoverMediaSelected = async (url: string) => {
  try {
    const filename = url.split('/').pop() || 'cover.jpg'
    const response = await fetch(url)
    const blob = await response.blob()
    const file = new File([blob], filename, { type: blob.type || 'image/jpeg' })
    form.value.cover_image = file
    coverPreview.value = url
  } catch {
    // 如果 fetch 失败，至少设置预览
    coverPreview.value = url
  }
}

const clearCover = () => {
  if (coverPreview.value && coverPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(coverPreview.value)
  }
  form.value.cover_image = null
  coverPreview.value = null
  if (coverInput.value) coverInput.value.value = ''
}

// ========== 字段错误处理 ==========

// 字段名到滚动的 ref / selector 映射
const FIELD_SCROLL_MAP: Record<string, { getEl: () => HTMLElement | null; switchTab?: boolean }> = {
  title:        { getEl: () => titleInputRef.value },
  content:      { getEl: () => contentErrorRef.value },
  tags:         { getEl: () => document.querySelector('.editor-right .blog-input') as HTMLElement, switchTab: true },
  category:     { getEl: () => document.querySelector('.editor-right select') as HTMLElement, switchTab: true },
  article_type: { getEl: () => document.querySelector('.editor-right select') as HTMLElement, switchTab: true },
  status:       { getEl: () => document.querySelectorAll('.editor-right select')[2] as HTMLElement, switchTab: true },
  seo_title:    { getEl: () => document.querySelector('.editor-right input[placeholder*="留空则使用文章标题"]') as HTMLElement, switchTab: true },
  seo_description: { getEl: () => document.querySelector('.editor-right textarea') as HTMLElement, switchTab: true },
}

function scrollToField(fieldName: string) {
  const map = FIELD_SCROLL_MAP[fieldName]
  if (map?.switchTab) rightTab.value = 'settings'
  // 等 tab 切换完成再滚动
  const el = map?.getEl() || null
  if (el) {
    setTimeout(() => {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      // 短暂高亮闪烁
      el.classList.add('field-flash')
      setTimeout(() => el.classList.remove('field-flash'), 1200)
    }, map?.switchTab ? 100 : 0)
  }
}

function clearFieldError(fieldName: string) {
  delete fieldErrors.value[fieldName]
}

// 后端错误字段名 → 前端字段名的映射
const BACKEND_FIELD_MAP: Record<string, string> = {
  title: 'title',
  content: 'content',
  tags: 'tags',
  category: 'category',
  article_type: 'article_type',
  status: 'status',
  is_featured: 'is_featured',
  seo_title: 'seo_title',
  seo_description: 'seo_description',
}

function applyBackendErrors(detail: Record<string, any>) {
  // 清空旧错误
  fieldErrors.value = {}
  let firstField = ''
  for (const [key, value] of Object.entries(detail)) {
    const frontendKey = BACKEND_FIELD_MAP[key] || key
    const msg = Array.isArray(value) ? value.join('; ') : String(value)
    fieldErrors.value[frontendKey] = msg
    if (!firstField) firstField = frontendKey
  }
  if (firstField) scrollToField(firstField)
}

// ========== 保存文章 ==========

const saveArticle = async (forceStatus?: string) => {
  // 清空旧错误
  fieldErrors.value = {}

  // 前端校验
  if (!form.value.title.trim()) {
    fieldErrors.value.title = '请输入文章标题'
    scrollToField('title')
    return
  }
  if (!form.value.content.trim()) {
    fieldErrors.value.content = '请输入文章内容'
    scrollToField('content')
    return
  }

  saving.value = true
  try {
    const tags = tagInput.value.split(/[,，]/).map(t => t.trim()).filter(Boolean)

    const jsonData: any = {
      title: form.value.title,
      content: form.value.content,
      summary: form.value.summary || form.value.content.replace(/[#*`\[\]()!>_\-]/g, '').substring(0, 200),
      article_type: form.value.article_type,
      category: form.value.category || null,
      status: forceStatus || form.value.status,
      is_featured: form.value.is_featured,
      seo_title: form.value.seo_title,
      seo_description: form.value.seo_description,
      tags,
    }

    if (form.value.cover_image) {
      const fd = new FormData()
      fd.append('title', jsonData.title)
      fd.append('content', jsonData.content)
      fd.append('summary', jsonData.summary)
      fd.append('article_type', jsonData.article_type)
      fd.append('status', jsonData.status)
      fd.append('is_featured', String(jsonData.is_featured))
      fd.append('seo_title', jsonData.seo_title || '')
      fd.append('seo_description', jsonData.seo_description || '')
      if (jsonData.category) fd.append('category', String(jsonData.category))
      tags.forEach((t: string) => fd.append('tags', t))
      fd.append('cover_image', form.value.cover_image)

      if (isEdit.value) {
        await updateArticle(articleId!, fd)
      } else {
        await createArticle(fd)
      }
    } else {
      if (isEdit.value) {
        await updateArticle(articleId!, jsonData)
      } else {
        await createArticle(jsonData)
      }
    }

    // 停止自动保存，防止跳转前定时器再次写入草稿
    if (autoSaveTimer) { clearInterval(autoSaveTimer); autoSaveTimer = null }
    clearDraft()
    showToast(isEdit.value ? '文章已更新' : '文章已创建')
    setTimeout(() => router.push('/sixth-admin/articles'), 1000)
  } catch (error: any) {
    const detail = error.response?.data
    if (detail && typeof detail === 'object' && !detail.detail) {
      // 后端返回了字段级错误 → 高亮对应字段
      applyBackendErrors(detail)
    } else {
      const msg = typeof detail === 'object' ? (detail?.detail || '保存失败') : (String(detail) || '保存失败')
      showToast(msg, 'error')
    }
  } finally {
    saving.value = false
  }
}

const goBack = () => router.push('/sixth-admin/articles')

// ========== 自动保存草稿到 localStorage ==========

const getDraftKey = () => {
  return isEdit.value ? `article_draft_${articleId}` : 'article_draft_new'
}

const autoSaveToLocal = () => {
  if (!form.value.title.trim() && !form.value.content.trim()) return

  const draftData = {
    title: form.value.title,
    content: form.value.content,
    article_type: form.value.article_type,
    category: form.value.category,
    status: form.value.status,
    is_featured: form.value.is_featured,
    seo_title: form.value.seo_title,
    seo_description: form.value.seo_description,
    tags: tagInput.value,
    savedAt: new Date().toISOString(),
  }
  try {
    localStorage.setItem(getDraftKey(), JSON.stringify(draftData))
    draftSaved.value = true
    setTimeout(() => { draftSaved.value = false }, 2500)
  } catch {
    // localStorage 不可用或已满，静默失败
  }
}

const restoreDraft = (): boolean => {
  const raw = localStorage.getItem(getDraftKey())
  if (!raw) return false
  try {
    const draft = JSON.parse(raw)
    form.value.title = draft.title || ''
    form.value.content = draft.content || ''
    form.value.article_type = draft.article_type || 'article'
    form.value.category = draft.category ?? null
    form.value.status = draft.status || 'draft'
    form.value.is_featured = draft.is_featured || false
    form.value.seo_title = draft.seo_title || ''
    form.value.seo_description = draft.seo_description || ''
    tagInput.value = draft.tags || ''
    return true
  } catch {
    localStorage.removeItem(getDraftKey())
    return false
  }
}

const clearDraft = () => {
  localStorage.removeItem(getDraftKey())
}

// ========== 键盘快捷键 ==========

const handleGlobalKeydown = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    saveArticle()
  }
}

const handleBeforeUnload = () => {
  autoSaveToLocal()
}

// ========== 生命周期 ==========

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  // 加载分类
  await getCategories().then(data => { categories.value = data as any[] }).catch(() => {})

  if (isEdit.value) {
    // 编辑模式：从服务器加载文章
    try {
      const article = await getArticleDetail(articleId!) as any
      form.value.title = article.title
      form.value.content = article.content
      form.value.summary = article.summary
      form.value.article_type = article.article_type
      form.value.category = article.category
      form.value.status = article.status
      form.value.is_featured = article.is_featured
      form.value.seo_title = article.seo_title || ''
      form.value.seo_description = article.seo_description || ''
      if (article.cover_image) coverPreview.value = article.cover_image
      tagInput.value = article.tags?.map((t: any) => t.name).join(', ') || ''
    } catch {
      showToast('文章不存在', 'error')
      router.push('/sixth-admin/articles')
      return
    }
  }

  // 启动自动保存
  autoSaveTimer = setInterval(autoSaveToLocal, 30000)

  // 注册快捷键和离开保存
  document.addEventListener('keydown', handleGlobalKeydown)
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onUnmounted(() => {
  if (autoSaveTimer) clearInterval(autoSaveTimer)
  document.removeEventListener('keydown', handleGlobalKeydown)
  window.removeEventListener('beforeunload', handleBeforeUnload)

  // 离开页面时清除未保存的草稿，避免下次进入时意外恢复
  clearDraft()

  // 释放 blob URL
  if (coverPreview.value && coverPreview.value.startsWith('blob:')) {
    URL.revokeObjectURL(coverPreview.value)
  }
})
</script>

<style scoped>
/* ========== 根容器 ========== */
.editor-page {
  margin: -28px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
  overflow: hidden;
}

/* ========== 顶部操作栏 ========== */
.editor-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 20px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  gap: 16px;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar-center {
  flex: 1;
  text-align: center;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-h);
  letter-spacing: -0.01em;
}

.draft-indicator {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-right: 8px;
}

/* ========== 标题输入 ========== */
.editor-title-bar {
  padding: 12px 20px;
  flex-shrink: 0;
}

.title-input {
  width: 100%;
  border: none;
  background: transparent;
  font-family: var(--heading);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-h);
  line-height: 1.4;
  outline: none;
  padding: 4px 0;
}
.title-input::placeholder { color: var(--text-muted); }

/* ========== 工具栏 ========== */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 6px 16px;
  background: var(--bg-subtle);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  overflow-x: auto;
  white-space: nowrap;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 2px;
}

.editor-toolbar button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 30px;
  padding: 0 8px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text);
  font-family: var(--heading);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.editor-toolbar button:hover {
  background: var(--accent-bg);
  color: var(--accent);
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border);
  margin: 0 6px;
  flex-shrink: 0;
}

/* ========== 主体：编辑 + 右侧面板 ========== */
.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

/* --- 左侧编辑区 --- */
.editor-left {
  flex: 6;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid var(--border);
}

.editor-textarea {
  flex: 1;
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px 24px;
  font-family: var(--mono);
  font-size: 0.875rem;
  line-height: 1.75;
  color: var(--text-h);
  resize: none;
  outline: none;
}
.editor-textarea::placeholder { color: var(--text-muted); }

/* --- 右侧面板 --- */
.editor-right {
  flex: 4;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-card);
}

.right-tabs {
  display: flex;
  border-bottom: 2px solid var(--border);
  flex-shrink: 0;
}

.right-tabs button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 11px 16px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 550;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}

.right-tabs button:hover {
  color: var(--text);
}

.right-tabs button.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* --- 预览面板 --- */
.preview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  font-size: 0.9rem;
  text-align: center;
  gap: 12px;
}

.preview {
  font-size: 0.9rem;
  line-height: 1.75;
  color: var(--text);
}

.preview :deep(h1) { font-size: 1.5rem; }
.preview :deep(h2) { font-size: 1.25rem; }
.preview :deep(h3) { font-size: 1.1rem; }
.preview :deep(h1), .preview :deep(h2), .preview :deep(h3) {
  color: var(--text-h);
  margin-top: 16px;
}
.preview :deep(p) { margin: 0 0 0.75rem; }
.preview :deep(pre) {
  background: var(--code-bg);
  padding: 12px;
  border-radius: var(--radius);
  overflow-x: auto;
  font-size: 0.8rem;
}
.preview :deep(code) {
  background: var(--code-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
}
.preview :deep(img) { max-width: 100%; border-radius: var(--radius); }
.preview :deep(a) { color: var(--accent); }
.preview :deep(blockquote) {
  border-left: 3px solid var(--accent);
  padding-left: 12px;
  color: var(--text-muted);
  margin-left: 0;
}

/* --- 设置面板 --- */
.settings-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.setting-label {
  font-size: 0.78rem;
  font-weight: 650;
  color: var(--text-h);
  letter-spacing: 0.02em;
}

.setting-checkbox {
  display: flex !important;
  flex-direction: row !important;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.setting-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
  margin: 0;
  cursor: pointer;
}

.settings-panel .blog-input {
  font-size: 0.85rem;
}

.settings-panel textarea.blog-input {
  resize: vertical;
  min-height: 60px;
}

/* --- 封面 --- */
.cover-area {
  display: flex;
  flex-direction: column;
}

.cover-preview-wrap {
  width: 100%;
  aspect-ratio: 16 / 9;
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;
  background: var(--bg-subtle);
}

.cover-preview-wrap:hover { border-color: var(--accent); }

.cover-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  font-size: 0.85rem;
  gap: 6px;
}

/* ========== 底部信息栏 ========== */
.editor-bottombar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 36px;
  padding: 0 20px;
  border-top: 1px solid var(--border);
  background: var(--bg-card);
  flex-shrink: 0;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.bottombar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bottombar-right {
  display: flex;
  align-items: center;
}

.stat-item { color: var(--text-muted); }

.stat-divider {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--border);
}

.shortcut-hint kbd {
  display: inline-block;
  padding: 1px 5px;
  font-size: 0.7rem;
  font-family: var(--mono);
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: 3px;
  color: var(--text-muted);
}

/* ========== 浮动 Toast ========== */
.toast-float {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 500;
  box-shadow: var(--shadow-lg);
  max-width: 380px;
  pointer-events: auto;
}

.toast-float.success {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.toast-float.error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* Toast 动画 */
.toast-float-enter-active { transition: all 0.3s ease-out; }
.toast-float-leave-active { transition: all 0.2s ease-in; }
.toast-float-enter-from { opacity: 0; transform: translateX(20px); }
.toast-float-leave-to { opacity: 0; transform: translateX(20px); }

/* 暗色模式适配 Toast */
[data-theme="dark"] .toast-float.success {
  background: #064e3b;
  color: #6ee7b7;
  border-color: #065f46;
}

[data-theme="dark"] .toast-float.error {
  background: #7f1d1d;
  color: #fca5a5;
  border-color: #991b1b;
}

/* ========== 字段校验错误 ========== */
.field-error-input {
  border-color: #ef4444 !important;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15) !important;
  animation: shake 0.4s ease;
}

.field-error-input:focus {
  border-color: #ef4444 !important;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.25) !important;
}

.field-error-msg {
  display: block;
  font-size: 0.75rem;
  color: #ef4444;
  font-weight: 500;
  margin-top: 4px;
  line-height: 1.3;
}

/* 错误消息淡入 */
.field-error-fade-enter-active { transition: all 0.2s ease-out; }
.field-error-fade-leave-active { transition: all 0.15s ease-in; }
.field-error-fade-enter-from { opacity: 0; transform: translateY(-4px); }
.field-error-fade-leave-to { opacity: 0; transform: translateY(-4px); }

/* 抖动 */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-4px); }
  40% { transform: translateX(4px); }
  60% { transform: translateX(-3px); }
  80% { transform: translateX(3px); }
}

/* 高亮闪烁（滚动到目标后） */
.field-flash {
  animation: fieldFlash 1.2s ease;
}

@keyframes fieldFlash {
  0%   { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.5); }
  30%  { box-shadow: 0 0 0 8px rgba(99, 102, 241, 0); }
  60%  { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.5); }
  100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .editor-left { flex: 5.5; }
  .editor-right { flex: 4.5; }
}

@media (max-width: 768px) {
  .editor-page {
    margin: -16px;
    height: auto;
    min-height: 100vh;
    overflow: visible;
  }

  .editor-topbar {
    padding: 0 12px;
    height: 48px;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .back-text { display: none; }
  .draft-indicator { display: none; }

  .editor-title-bar { padding: 10px 12px; }
  .title-input { font-size: 1.2rem; }

  .editor-toolbar { padding: 6px 10px; }

  .editor-body {
    flex-direction: column;
    flex: none;
    min-height: 0;
    overflow: visible;
  }

  .editor-left {
    flex: none;
    height: 55vh;
    border-right: none;
    border-bottom: 1px solid var(--border);
  }

  .editor-textarea { padding: 14px 16px; }

  .editor-right {
    flex: none;
    min-height: 45vh;
  }

  .tab-content { padding: 14px; }

  .editor-bottombar {
    padding: 0 12px;
    position: sticky;
    bottom: 0;
  }

  .shortcut-hint { display: none; }
}
</style>
