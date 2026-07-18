<template>
  <div class="manage-page">
    <div class="page-header">
      <h1 class="page-title">分类管理</h1>
      <button class="blog-btn blog-btn-primary" @click="openCreateDialog">+ 创建分类</button>
    </div>

    <div v-if="toast" :class="['toast', toastType]">{{ toast }}</div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="categories.length === 0" class="empty">暂无分类</div>
    <div v-else class="list-table">
      <div v-for="cat in categories" :key="cat.id" class="list-row">
        <div class="list-info">
          <div class="list-main">
            <span class="cat-name">{{ cat.name }}</span>
            <span class="cat-slug">/{{ cat.slug }}</span>
            <span class="cat-count">{{ cat.article_count }} 篇文章</span>
            <span class="cat-order">排序: {{ cat.order }}</span>
          </div>
          <div v-if="cat.description" class="cat-desc">{{ cat.description }}</div>
          <!-- 子分类 -->
          <div v-if="cat.children && cat.children.length" class="child-list">
            <div v-for="child in cat.children" :key="child.id" class="child-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0"><path d="M9 18l6-6-6-6"/></svg>
              <span class="child-name">{{ child.name }}</span>
              <span class="child-slug">/{{ child.slug }}</span>
              <span class="child-count">{{ child.article_count }} 篇</span>
              <span class="child-order">排序: {{ child.order }}</span>
              <div class="child-actions">
                <button @click="openEditDialog(child)" class="btn-action btn-edit">编辑</button>
                <button @click="confirmDelete(child)" class="btn-action btn-delete">删除</button>
              </div>
            </div>
          </div>
        </div>
        <div class="list-actions">
          <button @click="openEditDialog(cat)" class="btn-action btn-edit">编辑</button>
          <button @click="confirmDelete(cat)" class="btn-action btn-delete">删除</button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <div v-if="showDialog" class="modal-overlay" @click.self="closeDialog">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ isEdit ? '编辑分类' : '创建分类' }}</h2>
          <button class="modal-close" @click="closeDialog">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>分类名称 *</label>
            <input v-model="formData.name" type="text" placeholder="请输入分类名称" class="blog-input" @input="autoSlug" />
          </div>
          <div class="form-group">
            <label>分类标识 (slug) *</label>
            <input v-model="formData.slug" type="text" placeholder="英文标识，如 my-category" class="blog-input" />
          </div>
          <div class="form-group">
            <label>父分类</label>
            <select v-model="formData.parent" class="blog-input blog-select">
              <option :value="null">无（顶级分类）</option>
              <option v-for="cat in parentOptions" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>排序</label>
            <input v-model.number="formData.order" type="number" class="blog-input" style="width:100px" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="formData.description" class="blog-textarea" placeholder="分类描述（可选）" rows="3"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="blog-btn blog-btn-ghost" @click="closeDialog">取消</button>
          <button class="blog-btn blog-btn-primary" @click="handleSubmit" :disabled="submitting">{{ submitting ? '提交中...' : (isEdit ? '保存' : '创建') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="showDeleteDialog" class="modal-overlay" @click.self="showDeleteDialog = false">
      <div class="modal" style="max-width:380px">
        <div class="modal-header">
          <h2>确认删除</h2>
          <button class="modal-close" @click="showDeleteDialog = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="modal-body">
          <p>确定要删除分类 <strong>{{ deleteTarget?.name }}</strong> 吗？</p>
          <p v-if="deleteTarget?.article_count > 0" style="color:#dc2626;font-size:0.85rem">
            该分类下有 {{ deleteTarget.article_count }} 篇文章，删除后文章将变为"未分类"状态。
          </p>
        </div>
        <div class="modal-footer">
          <button class="blog-btn blog-btn-ghost" @click="showDeleteDialog = false">取消</button>
          <button class="blog-btn blog-btn-ghost" style="color:#dc2626;border-color:#fecaca" @click="doDelete" :disabled="deleting">{{ deleting ? '删除中...' : '确认删除' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getAdminCategories, createCategory, updateCategory, deleteCategory } from '../api/blog'

interface CategoryItem {
  id: number
  name: string
  slug: string
  description: string
  parent: number | null
  order: number
  article_count: number
  children: CategoryItem[]
}

const categories = ref<CategoryItem[]>([])
const loading = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const showDeleteDialog = ref(false)
const deleteTarget = ref<CategoryItem | null>(null)
const deleting = ref(false)
const toast = ref('')
const toastType = ref('')

const formData = ref<{
  name: string
  slug: string
  parent: number | null
  order: number
  description: string
}>({ name: '', slug: '', parent: null, order: 0, description: '' })

// 父分类选项（排除自身及其子分类）
const parentOptions = computed(() => {
  const flatten = (items: CategoryItem[], excludeId?: number | null): CategoryItem[] => {
    const result: CategoryItem[] = []
    for (const item of items) {
      if (item.id !== excludeId) {
        result.push(item)
        if (item.children) {
          result.push(...flatten(item.children, excludeId))
        }
      }
    }
    return result
  }
  return flatten(categories.value, editingId.value)
})

const showToast = (msg: string, type = 'success') => {
  toast.value = msg
  toastType.value = type
  setTimeout(() => { toast.value = '' }, 3000)
}

// 自动生成 slug
const autoSlug = () => {
  if (!isEdit.value && !formData.value.slug) {
    formData.value.slug = formData.value.name
      .toLowerCase()
      .replace(/[^\w\s一-鿿]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
  }
}

const fetchCategories = async () => {
  loading.value = true
  try {
    categories.value = await getAdminCategories() as CategoryItem[]
  } catch {
    showToast('获取分类列表失败', 'error')
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  editingId.value = null
  formData.value = { name: '', slug: '', parent: null, order: 0, description: '' }
  showDialog.value = true
}

const openEditDialog = (cat: CategoryItem) => {
  isEdit.value = true
  editingId.value = cat.id
  formData.value = {
    name: cat.name,
    slug: cat.slug,
    parent: cat.parent,
    order: cat.order,
    description: cat.description,
  }
  showDialog.value = true
}

const closeDialog = () => {
  showDialog.value = false
}

const handleSubmit = async () => {
  if (!formData.value.name) {
    showToast('请输入分类名称', 'error')
    return
  }
  if (!formData.value.slug) {
    showToast('请输入分类标识', 'error')
    return
  }
  submitting.value = true
  try {
    if (isEdit.value && editingId.value) {
      await updateCategory(editingId.value, formData.value)
      showToast('分类已更新')
    } else {
      await createCategory(formData.value)
      showToast('分类已创建')
    }
    closeDialog()
    await fetchCategories()
  } catch (e: any) {
    const msg = e.response?.data?.error || e.response?.data?.slug?.[0] || '操作失败'
    showToast(msg, 'error')
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (cat: CategoryItem) => {
  deleteTarget.value = cat
  showDeleteDialog.value = true
}

const doDelete = async () => {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await deleteCategory(deleteTarget.value.id)
    showToast('分类已删除')
    showDeleteDialog.value = false
    await fetchCategories()
  } catch (e: any) {
    showToast(e.response?.data?.error || '删除失败', 'error')
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.manage-page { max-width: 900px; margin: 0 auto; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.page-title { color: var(--text-h); margin: 0; }

.toast { padding: 12px 24px; border-radius: 8px; margin-bottom: 16px; text-align: center; font-size: 14px; }
.toast.success { background: #d4edda; color: #155724; }
.toast.error { background: #f8d7da; color: #721c24; }

.loading, .empty { text-align: center; padding: 48px; color: var(--text); }

.list-table { display: flex; flex-direction: column; gap: 12px; }

.list-row {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.list-info { flex: 1; min-width: 0; }
.list-main { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 4px; }

.cat-name { font-size: 1rem; font-weight: 600; color: var(--text-h); }
.cat-slug { color: var(--text-muted); font-size: 0.8rem; }
.cat-count { color: var(--accent); font-size: 0.8rem; }
.cat-order { color: var(--text-muted); font-size: 0.8rem; }
.cat-desc { font-size: 0.85rem; color: var(--text); margin-top: 4px; }

.child-list {
  margin-top: 10px;
  padding-left: 20px;
  border-left: 2px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.child-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  background: var(--bg-subtle);
  flex-wrap: wrap;
}

.child-name { font-weight: 550; color: var(--text-h); }
.child-slug { color: var(--text-muted); font-size: 0.78rem; }
.child-count { color: var(--accent); font-size: 0.78rem; }
.child-order { color: var(--text-muted); font-size: 0.78rem; }

.child-actions { display: flex; gap: 4px; margin-left: auto; }

.list-actions { display: flex; gap: 6px; flex-shrink: 0; flex-wrap: wrap; }

.btn-action { padding: 6px 12px; border: 1px solid var(--border); border-radius: 4px; cursor: pointer; font-size: 12px; background: var(--bg); }
.btn-edit { color: var(--accent); border-color: var(--accent); }
.btn-edit:hover { background: var(--accent-bg); }
.btn-delete { color: #dc3545; border-color: #dc3545; }
.btn-delete:hover { background: #f8d7da; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.15s ease; }
.modal { background: var(--bg-card); border-radius: var(--radius-xl); width: 90%; max-width: 480px; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-lg); animation: modalIn 0.2s ease; }
@keyframes modalIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); }
.modal-header h2 { margin: 0; font-size: 1.125rem; }
.modal-close { background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 0.25rem; border-radius: var(--radius-sm); transition: all 0.15s; }
.modal-close:hover { background: var(--accent-bg); color: var(--accent); }
.modal-body { padding: 1.5rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding: 1rem 1.5rem; border-top: 1px solid var(--border); }

/* Form */
.form-group { margin-bottom: 1.25rem; }
.form-group:last-child { margin-bottom: 0; }
.form-group label { display: block; font-size: 0.82rem; font-weight: 550; color: var(--text); margin-bottom: 0.35rem; }

.blog-input {
  width: 100%; padding: 0.55rem 0.75rem;
  border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--bg); color: var(--text-h); font-size: 0.88rem;
  transition: border-color 0.2s; box-sizing: border-box;
}
.blog-input:focus { outline: none; border-color: var(--accent); }

.blog-select { appearance: auto; cursor: pointer; }

.blog-textarea {
  width: 100%; padding: 0.55rem 0.75rem;
  border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--bg); color: var(--text-h); font-size: 0.88rem;
  transition: border-color 0.2s; box-sizing: border-box; resize: vertical;
  font-family: inherit;
}
.blog-textarea:focus { outline: none; border-color: var(--accent); }

.blog-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.55rem 1.1rem; font-size: 0.85rem; font-weight: 550;
  border-radius: var(--radius); cursor: pointer;
  transition: all 0.2s; font-family: inherit; border: 1px solid transparent;
}
.blog-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.blog-btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.blog-btn-primary:hover:not(:disabled) { filter: brightness(1.1); }
.blog-btn-ghost { background: var(--bg-card); color: var(--text); border-color: var(--border); }
.blog-btn-ghost:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); background: var(--accent-bg); }
</style>
