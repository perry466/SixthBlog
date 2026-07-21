<template>
  <div class="media-page">
    <!-- 顶部 -->
    <div class="page-header">
      <h1 class="page-title">媒体库</h1>
      <div class="header-actions">
        <div class="search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索文件名..."
            class="search-input"
            @input="onSearch"
          />
        </div>
        <button class="blog-btn blog-btn-primary" @click="triggerUpload">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          上传图片
        </button>
        <input ref="uploadInput" type="file" accept="image/*" hidden @change="handleUpload" />
      </div>
    </div>

    <!-- 拖拽上传区域 -->
    <div
      :class="['drop-zone', { 'drop-active': isDragging }]"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.4"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
      <span>拖拽图片到此处上传</span>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading">加载中...</div>

    <!-- 网格 -->
    <div v-else-if="items.length" class="media-grid">
      <div
        v-for="item in items"
        :key="item.id"
        class="media-card"
        @click="previewItem = item"
      >
        <img :src="item.file_url" :alt="item.filename" loading="lazy" />
        <div class="card-overlay">
          <button class="card-action" title="复制 URL" @click.stop="copyUrl(item.file_url)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
          </button>
          <button class="card-action card-delete" title="删除" @click.stop="confirmDelete(item)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
          </button>
        </div>
        <div class="card-info">
          <span class="card-filename" :title="item.filename">{{ item.filename }}</span>
          <span class="card-size">{{ formatSize(item.file_size) }}</span>
        </div>
      </div>
    </div>

    <!-- 空 -->
    <div v-else class="empty">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.25"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
      <p>媒体库为空</p>
      <p class="empty-hint">拖拽图片到上方区域或点击「上传图片」按钮</p>
    </div>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="pagination">
      <button :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">上一页</button>
      <span class="page-num">{{ currentPage }} / {{ totalPages }}</span>
      <button :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">下一页</button>
    </div>

    <!-- 预览弹窗 -->
    <Transition name="modal-fade">
      <div v-if="previewItem" class="preview-overlay" @click="previewItem = null">
        <div class="preview-modal" @click.stop>
          <img :src="previewItem.file_url" :alt="previewItem.filename" />
          <div class="preview-info">
            <strong>{{ previewItem.filename }}</strong>
            <span>{{ formatSize(previewItem.file_size) }} · {{ previewItem.mime_type }}</span>
            <span>{{ previewItem.created_at }}</span>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 删除确认 -->
    <Transition name="modal-fade">
      <div v-if="deleteTarget" class="confirm-overlay" @click="deleteTarget = null">
        <div class="confirm-dialog" @click.stop>
          <h3>确认删除</h3>
          <p>确定要删除「{{ deleteTarget.filename }}」吗？此操作不可撤销。</p>
          <div class="confirm-actions">
            <button class="blog-btn blog-btn-ghost" @click="deleteTarget = null">取消</button>
            <button class="blog-btn blog-btn-primary" style="background:#dc3545;border-color:#dc3545" :disabled="deleting" @click="doDelete">
              {{ deleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast-float">
      <div v-if="toast" :class="['toast', toastType]">{{ toast }}</div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getMediaList, uploadMedia, deleteMedia } from '../../api/blog'
import type { MediaItem } from '../../types'

const uploadInput = ref<HTMLInputElement | null>(null)
const items = ref<MediaItem[]>([])
const loading = ref(true)
const searchQuery = ref('')
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const isDragging = ref(false)
const previewItem = ref<MediaItem | null>(null)
const deleteTarget = ref<MediaItem | null>(null)
const deleting = ref(false)
const toast = ref('')
const toastType = ref<'success' | 'error'>('success')

let searchTimer: ReturnType<typeof setTimeout> | null = null

const totalPages = computed(() => Math.ceil(total.value / pageSize) || 1)

function showToast(msg: string, type: 'success' | 'error' = 'success') {
  toast.value = msg
  toastType.value = type
  setTimeout(() => { toast.value = '' }, 2500)
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function loadItems() {
  loading.value = true
  try {
    const params: any = { page: currentPage.value, page_size: pageSize }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    const res = (await getMediaList(params)) as any
    items.value = (res.results || []) as MediaItem[]
    total.value = (res.count || 0) as number
  } catch {
    items.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadItems()
  }, 300)
}

function goPage(page: number) {
  currentPage.value = page
  loadItems()
}

function triggerUpload() {
  uploadInput.value?.click()
}

async function handleUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  try {
    await uploadMedia(file)
    showToast('上传成功')
    await loadItems()
  } catch (e: any) {
    showToast(e.response?.data?.detail || '上传失败', 'error')
  }
  if (uploadInput.value) {
    uploadInput.value.value = ''
  }
}

async function handleDrop(e: DragEvent) {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (!files || !files.length) return
  const file = files[0]
  if (!file.type.startsWith('image/')) {
    showToast('只接受图片文件', 'error')
    return
  }
  try {
    await uploadMedia(file)
    showToast('上传成功')
    await loadItems()
  } catch (e: any) {
    showToast(e.response?.data?.detail || '上传失败', 'error')
  }
}

async function copyUrl(url: string) {
  try {
    await navigator.clipboard.writeText(url)
    showToast('URL 已复制')
  } catch {
    showToast('复制失败，请手动复制', 'error')
  }
}

function confirmDelete(item: MediaItem) {
  deleteTarget.value = item
}

async function doDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await deleteMedia(deleteTarget.value.id)
    showToast('已删除')
    deleteTarget.value = null
    await loadItems()
  } catch (e: any) {
    showToast(e.response?.data?.detail || '删除失败', 'error')
  } finally {
    deleting.value = false
  }
}

onMounted(() => loadItems())
</script>

<style scoped>
.media-page {
  max-width: 1100px;
  margin: 0 auto;
  padding-bottom: 60px;
}

/* ===== 头部 ===== */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  gap: 16px;
  flex-wrap: wrap;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-h);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-muted);
  min-width: 200px;
}
.search-box:focus-within { border-color: var(--accent); }

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 0.85rem;
  color: var(--text-h);
  outline: none;
  font-family: inherit;
}

.blog-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  font-size: 0.85rem;
  font-weight: 550;
  border-radius: var(--radius);
  cursor: pointer;
  font-family: inherit;
  border: 1px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
}
.blog-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.blog-btn-primary { background: var(--accent); color: #fff; }
.blog-btn-primary:hover:not(:disabled) { filter: brightness(1.1); }
.blog-btn-ghost { background: var(--bg-card); color: var(--text); border-color: var(--border); }
.blog-btn-ghost:hover { border-color: var(--accent); color: var(--accent); }

/* ===== 拖拽区域 ===== */
.drop-zone {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  border: 2px dashed var(--border);
  border-radius: var(--radius-lg);
  color: var(--text-muted);
  font-size: 0.85rem;
  transition: all 0.2s;
  margin-bottom: 1rem;
  background: var(--bg-subtle);
}
.drop-zone.drop-active {
  border-color: var(--accent);
  background: var(--accent-bg);
  color: var(--accent);
}

/* ===== 网格 ===== */
.media-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.media-card {
  position: relative;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--bg-card);
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.media-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--accent);
}

.media-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}

.card-overlay {
  position: absolute;
  top: 6px;
  right: 6px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}
.media-card:hover .card-overlay { opacity: 1; }

.card-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius);
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
}
.card-action:hover { background: var(--accent); }
.card-delete:hover { background: #dc3545 !important; }

.card-info {
  padding: 6px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-filename {
  font-size: 0.72rem;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-size {
  font-size: 0.68rem;
  color: var(--text-muted);
}

/* ===== 空 ===== */
.loading, .empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 48px 0;
  color: var(--text-muted);
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.empty-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* ===== 分页 ===== */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}
.pagination button {
  padding: 6px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  color: var(--text);
  font-size: 0.82rem;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}
.pagination button:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.page-num { font-size: 0.82rem; color: var(--text-muted); }

/* ===== 预览弹窗 ===== */
.preview-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.preview-modal {
  max-width: 90vw;
  max-height: 90vh;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.preview-modal img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  display: block;
}
.preview-info {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.8rem;
  color: var(--text-muted);
}
.preview-info strong {
  font-size: 0.88rem;
  color: var(--text-h);
}

/* ===== 删除确认 ===== */
.confirm-overlay {
  position: fixed;
  inset: 0;
  z-index: 2100;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.confirm-dialog {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  max-width: 400px;
  width: 100%;
  box-shadow: var(--shadow-lg);
}
.confirm-dialog h3 {
  margin: 0 0 8px;
  font-size: 1rem;
  font-weight: 650;
  color: var(--text-h);
}
.confirm-dialog p {
  margin: 0 0 16px;
  font-size: 0.88rem;
  color: var(--text);
}
.confirm-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* ===== Toast ===== */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 2200;
  padding: 10px 20px;
  border-radius: var(--radius);
  font-size: 0.85rem;
  font-weight: 500;
  box-shadow: var(--shadow-lg);
}
.toast.success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.toast.error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

[data-theme="dark"] .toast.success { background: #064e3b; color: #6ee7b7; border-color: #065f46; }
[data-theme="dark"] .toast.error { background: #7f1d1d; color: #fca5a5; border-color: #991b1b; }

/* 动画 */
.modal-fade-enter-active { transition: opacity 0.2s ease; }
.modal-fade-leave-active { transition: opacity 0.15s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

.toast-float-enter-active { transition: all 0.3s ease-out; }
.toast-float-leave-active { transition: all 0.2s ease-in; }
.toast-float-enter-from { opacity: 0; transform: translateY(10px); }
.toast-float-leave-to { opacity: 0; transform: translateY(10px); }

/* ===== 响应式 ===== */
@media (max-width: 1024px) {
  .media-grid { grid-template-columns: repeat(4, 1fr); }
}
@media (max-width: 768px) {
  .media-grid { grid-template-columns: repeat(3, 1fr); }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-wrap: wrap; }
  .search-box { flex: 1; min-width: 0; }
}
</style>
