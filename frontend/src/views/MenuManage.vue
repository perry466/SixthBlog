<template>
  <div class="manage-page">
    <div class="page-header">
      <h1 class="page-title">菜单管理</h1>
      <button class="blog-btn blog-btn-primary" @click="openCreateDialog">+ 创建菜单项</button>
    </div>

    <div v-if="toast" :class="['toast', toastType]">{{ toast }}</div>

    <!-- 提示 -->
    <div class="help-tip">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
      <span>点击「关联分类」选择一个或多个分类，保存后自动为每个分类创建子菜单项，前台展示为下拉菜单。</span>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="allItems.length === 0" class="empty">暂无菜单项</div>
    <div v-else class="tree-list">
      <div v-for="parent in topLevelItems" :key="parent.id" class="tree-group">
        <!-- 父级菜单卡片 -->
        <div class="parent-card">
          <div class="parent-left">
            <span class="parent-name">{{ parent.name }}</span>
            <span v-if="parent.url" class="parent-url">{{ parent.url }}</span>
            <span v-else class="parent-url-dropdown">下拉菜单 · {{ parent.children.length }} 个子项</span>
            <span class="item-order">排序 {{ parent.order }}</span>
            <span :class="['status-dot', parent.is_active ? 'active' : 'inactive']"></span>
            <span class="status-text">{{ parent.is_active ? '启用' : '禁用' }}</span>
          </div>
          <div class="parent-actions">
            <button @click="openEditDialog(parent)" class="btn-action btn-edit">编辑</button>
            <button @click="confirmDelete(parent)" class="btn-action btn-delete">删除</button>
          </div>
        </div>

        <!-- 子菜单项列表（缩进在父级下方） -->
        <div v-if="parent.children.length" class="children-block">
          <div v-for="child in parent.children" :key="child.id" class="child-row">
            <div class="child-connector">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
            </div>
            <div class="child-info">
              <span class="child-name">{{ child.name }}</span>
              <span class="child-url">{{ child.url }}</span>
              <span v-if="isCategoryLink(child.url)" class="cat-link-badge">分类</span>
            </div>
            <div class="child-actions">
              <button @click="promoteToTop(child)" class="btn-action btn-promote" title="提升为顶级菜单">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
                提升
              </button>
              <button @click="openEditDialog(child)" class="btn-action btn-edit">编辑</button>
              <button @click="confirmDelete(child)" class="btn-action btn-delete">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <div v-if="showDialog" class="modal-overlay" @click.self="closeDialog">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ isEdit ? '编辑菜单项' : '创建菜单项' }}</h2>
          <button class="modal-close" @click="closeDialog">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>菜单名称 *</label>
            <input v-model="formData.name" type="text" placeholder="如：文章、关于我们" class="blog-input" />
          </div>
          <div class="form-group">
            <label>链接/路由</label>
            <div class="input-row">
              <input v-model="formData.url" type="text" placeholder="留空则为下拉菜单父级" class="blog-input" style="flex:1" />
              <button type="button" class="blog-btn blog-btn-ghost cat-picker-btn" @click="showCategoryPicker = !showCategoryPicker">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h6v6H4zM4 14h6v6H4zM14 4h6v6h-6zM14 14h6v6h-6z"/></svg>
                关联分类
              </button>
            </div>
            <!-- 分类选择器（多选，始终生成为子菜单） -->
            <div v-if="showCategoryPicker" class="category-picker">
              <div class="picker-header">选择分类 → 自动生成下拉子菜单（每分类一个子项）</div>
              <div
                v-for="cat in availableCategories"
                :key="cat.id"
                class="picker-item"
                :class="{ selected: selectedCategorySlugs.includes(cat.slug) }"
                @click="toggleCategory(cat)"
              >
                <span class="picker-check">
                  <svg v-if="selectedCategorySlugs.includes(cat.slug)" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--border)" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
                </span>
                <span class="picker-name">{{ cat.name }}</span>
                <span class="picker-slug">/{{ cat.slug }}</span>
              </div>
              <div v-if="!availableCategories.length" class="picker-empty">暂无分类，请先去「分类管理」创建</div>
              <div v-if="availableCategories.length" class="picker-footer">
                <span class="picker-selected-count" v-if="selectedCategorySlugs.length">
                  已选 {{ selectedCategorySlugs.length }} 个分类，将生成 {{ selectedCategorySlugs.length }} 个子菜单项
                </span>
                <span v-else class="picker-selected-count">请选择分类</span>
                <button type="button" class="blog-btn blog-btn-primary" style="padding:0.35rem 1rem;font-size:0.82rem" @click="confirmCategorySelection">确定</button>
              </div>
            </div>
            <!-- 已选分类标签 -->
            <div v-if="selectedCategorySlugs.length" class="selected-cats">
              <span v-for="slug in selectedCategorySlugs" :key="slug" class="selected-cat-tag">
                {{ categoryLabelMap[slug] || slug }}
                <span class="selected-cat-remove" @click="removeCategory(slug)">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6L6 18M6 6l12 12"/></svg>
                </span>
              </span>
              <span class="as-submenu-badge">下拉子菜单</span>
            </div>
          </div>
          <div class="form-group">
            <label>父菜单</label>
            <select v-model="formData.parent" class="blog-input blog-select">
              <option :value="null">无（顶级菜单）</option>
              <option v-for="p in parentOptions" :key="p.id" :value="p.id">
                {{ '  '.repeat(p._level) }}{{ p.name }}
              </option>
            </select>
            <p class="form-hint">选择父菜单后，此项在前台会出现在父菜单的下拉菜单中。</p>
          </div>
          <div class="form-row">
            <div class="form-group" style="flex:1">
              <label>排序</label>
              <input v-model.number="formData.order" type="number" class="blog-input" style="width:100px" />
            </div>
            <div class="form-group" style="flex:1">
              <label class="checkbox-label">
                <input type="checkbox" v-model="formData.is_active" style="accent-color:var(--accent)" />
                <span>启用</span>
              </label>
            </div>
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
          <p>确定要删除菜单项 <strong>{{ deleteTarget?.name }}</strong> 吗？</p>
          <p v-if="childrenOf(deleteTarget?.id).length" style="color:#dc2626;font-size:0.85rem">
            该菜单下有 {{ childrenOf(deleteTarget?.id).length }} 个子菜单项，删除后子菜单将一并删除。
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
import { getAdminMenuItems, createMenuItem, updateMenuItem, deleteMenuItem } from '../api/blog'
import { getCategories } from '../api/blog'

interface MenuItemRaw {
  id: number
  name: string
  url: string
  icon: string
  order: number
  is_active: boolean
  parent: number | null
  parent_name: string | null
}

interface CategoryOption {
  id: number
  name: string
  slug: string
}

interface MenuOption extends MenuItemRaw {
  _level: number
}

const allItems = ref<MenuItemRaw[]>([])
const loading = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const showDeleteDialog = ref(false)
const deleteTarget = ref<MenuItemRaw | null>(null)
const deleting = ref(false)
const toast = ref('')
const toastType = ref('')
const showCategoryPicker = ref(false)
const categoryOptions = ref<CategoryOption[]>([])
const selectedCategorySlugs = ref<string[]>([])

// 分类 slug → name 映射
const categoryLabelMap = computed(() => {
  const map: Record<string, string> = {}
  for (const cat of categoryOptions.value) {
    map[cat.slug] = cat.name
  }
  return map
})

// 编辑时，过滤掉已有子菜单对应的分类（去重）
const availableCategories = computed(() => {
  // 创建模式：显示所有分类
  if (!isEdit.value || !editingId.value) return categoryOptions.value
  // 编辑模式：排除已有子菜单的分类
  const existing = existingChildSlugs.value
  // 但保留当前已选中的（允许用户不修改已选）
  return categoryOptions.value.filter(
    cat => !existing.includes(cat.slug) || selectedCategorySlugs.value.includes(cat.slug)
  )
})

// 编辑时获取已有子菜单的 category slug 列表
const existingChildSlugs = computed(() => {
  if (!isEdit.value || !editingId.value) return [] as string[]
  const slugs: string[] = []
  for (const child of childrenOf(editingId.value)) {
    const match = child.url.match(/\/articles\?category_slug=([^&]+)/)
    if (match) {
      // 可能是多个 slug 逗号分隔
      match[1].split(',').forEach(s => {
        const trimmed = s.trim()
        if (trimmed) slugs.push(trimmed)
      })
    }
  }
  return slugs
})

const formData = ref<{
  name: string
  url: string
  icon: string
  parent: number | null
  order: number
  is_active: boolean
}>({ name: '', url: '', icon: '', parent: null, order: 0, is_active: true })

// 父菜单名称映射
const parentNameMap = computed(() => {
  const map = new Map<number, string>()
  for (const item of allItems.value) {
    map.set(item.id, item.name)
  }
  return map
})

// 判断是否为分类文章页面链接
const isCategoryLink = (url: string) => /\/articles\?category_slug=/.test(url)

// 获取某个菜单的子菜单
const childrenOf = (id: number | undefined | null): MenuItemRaw[] => {
  if (!id) return []
  return allItems.value.filter(i => i.parent === id)
}

// 顶级菜单项（带子项列表）
const topLevelItems = computed(() => {
  return allItems.value
    .filter(i => !i.parent)
    .map(parent => ({
      ...parent,
      children: childrenOf(parent.id)
    }))
})

// 父菜单选项（带层级缩进）
const parentOptions = computed(() => {
  const result: MenuOption[] = []
  const addChildren = (parentId: number | null, level: number, excludeId: number | null) => {
    for (const item of allItems.value) {
      if (item.parent !== parentId) continue
      if (item.id === excludeId) continue
      result.push({ ...item, _level: level })
      addChildren(item.id, level + 1, excludeId)
    }
  }
  addChildren(null, 0, editingId.value)
  return result
})

const showToast = (msg: string, type = 'success') => {
  toast.value = msg
  toastType.value = type
  setTimeout(() => { toast.value = '' }, 3000)
}

const fetchMenuItems = async () => {
  loading.value = true
  try {
    allItems.value = await getAdminMenuItems() as MenuItemRaw[]
    allItems.value.sort((a, b) => a.order - b.order)
  } catch {
    showToast('获取菜单列表失败', 'error')
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  editingId.value = null
  selectedCategorySlugs.value = []
  showCategoryPicker.value = false
  formData.value = { name: '', url: '', icon: '', parent: null, order: 0, is_active: true }
  showDialog.value = true
}

const openEditDialog = (item: MenuItemRaw) => {
  isEdit.value = true
  editingId.value = item.id
  showCategoryPicker.value = false

  // 从已有子菜单中恢复已选分类
  const existingSlugs: string[] = []
  for (const child of childrenOf(item.id)) {
    const match = child.url.match(/\/articles\?category_slug=([^&]+)/)
    if (match) {
      match[1].split(',').forEach(s => {
        const trimmed = s.trim()
        if (trimmed) existingSlugs.push(trimmed)
      })
    }
  }
  // 如果 URL 本身是分类链接（非下拉模式时的遗留数据），也解析
  const urlMatch = item.url.match(/\/articles\?category_slug=([^&]+)/)
  if (urlMatch) {
    urlMatch[1].split(',').forEach(s => {
      const trimmed = s.trim()
      if (trimmed && !existingSlugs.includes(trimmed)) existingSlugs.push(trimmed)
    })
  }
  selectedCategorySlugs.value = existingSlugs

  formData.value = {
    name: item.name,
    url: existingSlugs.length > 0 ? '' : item.url,  // 有子菜单时清空 URL
    icon: item.icon,
    parent: item.parent,
    order: item.order,
    is_active: item.is_active,
  }
  showDialog.value = true
}

// 切换分类选择（多选切换）
const toggleCategory = (cat: CategoryOption) => {
  const idx = selectedCategorySlugs.value.indexOf(cat.slug)
  if (idx === -1) {
    selectedCategorySlugs.value.push(cat.slug)
  } else {
    selectedCategorySlugs.value.splice(idx, 1)
  }
}

// 确认分类选择
const confirmCategorySelection = () => {
  if (selectedCategorySlugs.value.length > 0) {
    // 选中的分类将生成为子菜单 → 父级 URL 留空
    formData.value.url = ''
    // 只在创建且名称为空时给个默认名
    if (!isEdit.value && !formData.value.name) {
      formData.value.name = '文章'
    }
  }
  showCategoryPicker.value = false
}

// 移除已选的某个分类
const removeCategory = (slug: string) => {
  selectedCategorySlugs.value = selectedCategorySlugs.value.filter(s => s !== slug)
}

const closeDialog = () => {
  showDialog.value = false
}

const handleSubmit = async () => {
  if (!formData.value.name) {
    showToast('请输入菜单名称', 'error')
    return
  }
  submitting.value = true
  try {
    let parentId: number | null = null

    if (isEdit.value && editingId.value) {
      await updateMenuItem(editingId.value, formData.value)
      parentId = editingId.value
    } else {
      const created = await createMenuItem(formData.value) as any
      parentId = created.id
    }

    // 为选中的分类创建/同步子菜单项
    if (selectedCategorySlugs.value.length > 0 && parentId) {
      // 编辑时：获取已有子菜单的 URL 集合用于去重
      const existingUrls = new Set<string>()
      if (isEdit.value) {
        for (const child of childrenOf(parentId)) {
          existingUrls.add(child.url)
        }
      }

      let createdCount = 0
      let orderIdx = isEdit.value ? childrenOf(parentId).length : 0
      for (const slug of selectedCategorySlugs.value) {
        const cat = categoryOptions.value.find(c => c.slug === slug)
        if (!cat) continue
        const childUrl = `/articles?category_slug=${cat.slug}`
        // 去重：跳过已有相同 URL 的子菜单
        if (existingUrls.has(childUrl)) continue
        await createMenuItem({
          name: cat.name,
          url: childUrl,
          icon: '',
          parent: parentId,
          order: orderIdx,
          is_active: true,
        })
        createdCount++
        orderIdx++
      }

      if (createdCount > 0) {
        showToast(`已创建 ${createdCount} 个子菜单项`)
      } else if (isEdit.value) {
        showToast('菜单项已更新（子菜单无变化）')
      } else {
        showToast('菜单项已创建')
      }
    } else if (isEdit.value) {
      showToast('菜单项已更新')
    } else {
      showToast('菜单项已创建')
    }

    closeDialog()
    await fetchMenuItems()
    // 刷新前台菜单缓存
    try {
      const { useBlogStore } = await import('../stores/blog')
      useBlogStore().fetchMenuItems()
    } catch { /* ignore */ }
  } catch (e: any) {
    showToast(e.response?.data?.error || '操作失败', 'error')
  } finally {
    submitting.value = false
  }
}

// 提升为顶级菜单
const promoteToTop = async (item: MenuItemRaw) => {
  try {
    await updateMenuItem(item.id, { parent: null })
    showToast(`"${item.name}" 已提升为顶级菜单`)
    await fetchMenuItems()
    const { useBlogStore } = await import('../stores/blog')
    useBlogStore().fetchMenuItems()
  } catch (e: any) {
    showToast(e.response?.data?.error || '操作失败', 'error')
  }
}

const confirmDelete = (item: MenuItemRaw) => {
  deleteTarget.value = item
  showDeleteDialog.value = true
}

const doDelete = async () => {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await deleteMenuItem(deleteTarget.value.id)
    showToast('菜单项已删除')
    showDeleteDialog.value = false
    await fetchMenuItems()
  } catch (e: any) {
    showToast(e.response?.data?.error || '删除失败', 'error')
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  fetchMenuItems()
  try {
    categoryOptions.value = await getCategories() as CategoryOption[]
  } catch { /* ignore */ }
})
</script>

<style scoped>
.manage-page { max-width: 900px; margin: 0 auto; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.page-title { color: var(--text-h); margin: 0; }

.help-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  font-size: 0.82rem;
  color: #1e40af;
  margin-bottom: 1.25rem;
}
[data-theme="dark"] .help-tip {
  background: #1e293b;
  border-color: #334155;
  color: #93c5fd;
}

.toast { padding: 12px 24px; border-radius: 8px; margin-bottom: 16px; text-align: center; font-size: 14px; }
.toast.success { background: #d4edda; color: #155724; }
.toast.error { background: #f8d7da; color: #721c24; }

.loading, .empty { text-align: center; padding: 48px; color: var(--text); }

/* ===== 树形列表 ===== */
.tree-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 父级分组卡片 */
.tree-group {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.15s;
}
.tree-group:hover {
  border-color: var(--accent);
}

/* 父级菜单行 */
.parent-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 18px;
  background: var(--bg);
}

.parent-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
  flex-wrap: wrap;
}

.parent-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-h);
  white-space: nowrap;
}

.parent-url {
  font-size: 0.78rem;
  color: var(--accent);
  opacity: 0.75;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
}

.parent-url-dropdown {
  font-size: 0.78rem;
  color: #7c3aed;
  background: #ede9fe;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 500;
  white-space: nowrap;
}
[data-theme="dark"] .parent-url-dropdown {
  background: #2e1065;
  color: #a78bfa;
}

.item-order {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.active { background: #22c55e; }
.status-dot.inactive { background: #94a3b8; }

.status-text {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.parent-actions {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
}

/* 子菜单区域 */
.children-block {
  border-top: 1px solid var(--border);
  background: var(--bg-subtle);
  padding: 6px 0;
}

/* 子菜单行 */
.child-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 18px 9px 14px;
  transition: background 0.1s;
}
.child-row:hover {
  background: var(--accent-bg);
}

.child-connector {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  color: var(--border);
  margin-left: 20px;
  margin-right: 4px;
}

.child-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
  flex-wrap: wrap;
}

.child-name {
  font-size: 0.88rem;
  font-weight: 550;
  color: var(--text-h);
  white-space: nowrap;
}

.child-url {
  font-size: 0.75rem;
  color: var(--accent);
  opacity: 0.7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 260px;
}

.child-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.cat-link-badge {
  font-size: 0.7rem;
  padding: 1px 7px;
  border-radius: 4px;
  background: #eef2ff;
  color: #6366f1;
  font-weight: 500;
}
[data-theme="dark"] .cat-link-badge {
  background: #1e1b4b;
  color: #a5b4fc;
}

.list-actions { display: flex; gap: 5px; flex-shrink: 0; flex-wrap: wrap; align-items: center; }

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border: 1px solid var(--border);
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.78rem;
  background: var(--bg);
  white-space: nowrap;
  transition: all 0.15s;
}
.btn-edit { color: var(--accent); border-color: var(--accent); }
.btn-edit:hover { background: var(--accent-bg); }
.btn-delete { color: #dc3545; border-color: #dc3545; }
.btn-delete:hover { background: #f8d7da; }
.btn-promote { color: #6366f1; border-color: #6366f1; }
.btn-promote:hover { background: #eef2ff; }

.input-row { display: flex; gap: 8px; align-items: stretch; }

.cat-picker-btn { white-space: nowrap; font-size: 0.82rem; padding: 0.5rem 0.85rem; }

.category-picker {
  margin-top: 8px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg);
  overflow: hidden;
  animation: fadeIn 0.15s ease;
}

.picker-header {
  padding: 8px 12px;
  font-size: 0.75rem;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  background: var(--bg-subtle);
}

.picker-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.picker-item:last-child { border-bottom: none; }
.picker-item:hover { background: var(--accent-bg); }
.picker-item.selected { background: var(--accent-bg); }

.picker-name { font-size: 0.88rem; font-weight: 500; color: var(--text-h); flex: 1; }
.picker-slug { font-size: 0.78rem; color: var(--text-muted); }

.picker-empty { padding: 16px; text-align: center; font-size: 0.82rem; color: var(--text-muted); }

.picker-check { display: flex; align-items: center; flex-shrink: 0; width: 18px; height: 18px; }

.picker-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-top: 1px solid var(--border);
  background: var(--bg-subtle);
  flex-wrap: wrap;
}

.picker-selected-count { font-size: 0.78rem; color: var(--text-muted); white-space: nowrap; }

.selected-cats {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.selected-cat-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.78rem;
  padding: 3px 8px;
  border-radius: 4px;
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 500;
}

.as-submenu-badge {
  font-size: 0.7rem;
  padding: 1px 7px;
  border-radius: 4px;
  background: #ede9fe;
  color: #7c3aed;
  font-weight: 500;
}
[data-theme="dark"] .as-submenu-badge {
  background: #2e1065;
  color: #a78bfa;
}

.selected-cat-remove {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.15s;
}
.selected-cat-remove:hover { opacity: 1; }

.form-row { display: flex; gap: 1rem; align-items: flex-end; }

.form-hint { font-size: 0.75rem; color: var(--text-muted); margin: 4px 0 0; }

.checkbox-label { display: flex !important; align-items: center; gap: 0.5rem; cursor: pointer; padding-top: 0.35rem; }
.checkbox-label input[type="checkbox"] { width: 18px; height: 18px; }

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

.form-group { margin-bottom: 1.25rem; }
.form-group label { display: block; font-size: 0.82rem; font-weight: 550; color: var(--text); margin-bottom: 0.35rem; }

.blog-input {
  width: 100%; padding: 0.55rem 0.75rem;
  border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--bg); color: var(--text-h); font-size: 0.88rem;
  transition: border-color 0.2s; box-sizing: border-box;
}
.blog-input:focus { outline: none; border-color: var(--accent); }
.blog-select { appearance: auto; cursor: pointer; }

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
