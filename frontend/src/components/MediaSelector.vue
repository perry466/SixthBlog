<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="media-selector-overlay" @click.self="$emit('close')">
        <div class="media-selector">
          <!-- 头部 -->
          <div class="selector-header">
            <h3>媒体库</h3>
            <button class="selector-close" @click="$emit('close')" title="关闭">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <!-- 搜索栏 + 上传 -->
          <div class="selector-toolbar">
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
            <button class="upload-btn" @click="triggerUpload">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              上传
            </button>
            <input ref="uploadInput" type="file" accept="image/*" hidden @change="handleUpload" />
          </div>

          <!-- 网格 -->
          <div class="selector-grid" ref="gridRef">
            <div v-if="loading" class="grid-loading">加载中...</div>
            <template v-else-if="items.length">
              <div
                v-for="item in items"
                :key="item.id"
                :class="['grid-item', { selected: selectedId === item.id }]"
                @click="selectItem(item)"
                @dblclick="confirmItem(item)"
              >
                <img :src="item.file_url" :alt="item.filename" loading="lazy" />
                <div class="item-name" :title="item.filename">{{ item.filename }}</div>
                <div v-if="selectedId === item.id" class="item-check">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg>
                </div>
              </div>
            </template>
            <div v-else class="grid-empty">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              <p>暂无图片，点击「上传」添加</p>
            </div>
          </div>

          <!-- 底部分页 + 确认 -->
          <div class="selector-footer">
            <div class="pagination-info">
              <template v-if="total > 0">
                第 {{ currentPage }} / {{ totalPages }} 页（共 {{ total }} 张）
              </template>
              <template v-else>
                共 0 张
              </template>
            </div>
            <div class="pagination-btns">
              <button :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">上一页</button>
              <button :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">下一页</button>
            </div>
            <div class="footer-actions">
              <button class="btn-cancel" @click="$emit('close')">取消</button>
              <button class="btn-confirm" :disabled="!selectedUrl" @click="confirmSelection">
                确认选择
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { getMediaList, uploadMedia } from '../api/blog'
import type { MediaItem } from '../types'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{
  close: []
  selected: [url: string]
}>()

const uploadInput = ref<HTMLInputElement | null>(null)
const gridRef = ref<HTMLDivElement | null>(null)

const items = ref<MediaItem[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedId = ref<number | null>(null)
const selectedUrl = ref<string>('')
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20

let searchTimer: ReturnType<typeof setTimeout> | null = null

// 加载媒体列表
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

const totalPages = ref(0)

watch(total, (val) => {
  totalPages.value = Math.ceil(val / pageSize) || 0
})

watch(currentPage, () => {
  totalPages.value = Math.ceil(total.value / pageSize) || 0
})

// 打开时加载
watch(() => props.visible, (val) => {
  if (val) {
    // 保留上次搜索
    currentPage.value = 1
    selectedId.value = null
    selectedUrl.value = ''
    loadItems()
  }
})

// 搜索防抖
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

// 选择
function selectItem(item: MediaItem) {
  selectedId.value = item.id
  selectedUrl.value = item.file_url
}

function confirmItem(item: MediaItem) {
  selectedUrl.value = item.file_url
  confirmSelection()
}

function confirmSelection() {
  if (selectedUrl.value) {
    emit('selected', selectedUrl.value)
    emit('close')
  }
}

// 上传
function triggerUpload() {
  uploadInput.value?.click()
}

async function handleUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  try {
    await uploadMedia(file)
    // 上传后刷新列表，跳到最后一页或者刷新当前页
    await loadItems()
  } catch {
    // 父组件可侦听错误
  }
  if (uploadInput.value) {
    uploadInput.value.value = ''
  }
}
</script>

<style scoped>
/* ===== 遮罩 ===== */
.media-selector-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.media-selector {
  width: 100%;
  max-width: 760px;
  max-height: 85vh;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ===== 头部 ===== */
.selector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.selector-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 650;
  color: var(--text-h);
}

.selector-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}
.selector-close:hover { background: var(--bg-subtle); color: var(--text-h); }

/* ===== 工具栏 ===== */
.selector-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-subtle);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 7px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-muted);
}
.search-box:focus-within {
  border-color: var(--accent);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 0.85rem;
  color: var(--text-h);
  outline: none;
  font-family: inherit;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1px solid var(--accent);
  border-radius: var(--radius);
  background: var(--accent);
  color: #fff;
  font-size: 0.85rem;
  font-weight: 550;
  cursor: pointer;
  font-family: inherit;
  transition: filter 0.2s;
  white-space: nowrap;
}
.upload-btn:hover { filter: brightness(1.1); }

/* ===== 网格 ===== */
.selector-grid {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  min-height: 200px;
  max-height: 400px;
}

.grid-loading, .grid-empty {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  gap: 8px;
  padding: 32px;
}

.grid-item {
  position: relative;
  border: 2px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: var(--bg-subtle);
  aspect-ratio: 1;
}

.grid-item:hover {
  border-color: var(--accent);
}

.grid-item.selected {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.grid-item img {
  width: 100%;
  height: calc(100% - 26px);
  object-fit: cover;
  display: block;
}

.item-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 3px 6px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 0.65rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.item-check {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== 底部 ===== */
.selector-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-top: 1px solid var(--border);
  gap: 12px;
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.pagination-btns {
  display: flex;
  gap: 4px;
}

.pagination-btns button {
  padding: 4px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-card);
  color: var(--text);
  font-size: 0.78rem;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}
.pagination-btns button:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.pagination-btns button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.footer-actions {
  display: flex;
  gap: 8px;
}

.btn-cancel, .btn-confirm {
  padding: 6px 18px;
  border-radius: var(--radius);
  font-size: 0.85rem;
  font-weight: 550;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.btn-cancel {
  background: var(--bg-card);
  color: var(--text);
  border-color: var(--border);
}
.btn-cancel:hover { border-color: var(--accent); color: var(--accent); }

.btn-confirm {
  background: var(--accent);
  color: #fff;
}
.btn-confirm:hover:not(:disabled) { filter: brightness(1.1); }
.btn-confirm:disabled { opacity: 0.5; cursor: not-allowed; }

/* ===== 动画 ===== */
.modal-fade-enter-active { transition: opacity 0.2s ease; }
.modal-fade-leave-active { transition: opacity 0.15s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

.modal-fade-enter-active .media-selector { transition: transform 0.2s ease; }
.modal-fade-enter-from .media-selector { transform: scale(0.96); }

/* ===== 响应式 ===== */
@media (max-width: 640px) {
  .media-selector-overlay { padding: 10px; }
  .selector-grid { grid-template-columns: repeat(3, 1fr); }
  .selector-footer { flex-direction: column; align-items: stretch; }
  .pagination-btns { justify-content: center; }
  .footer-actions { justify-content: flex-end; }
}
</style>
