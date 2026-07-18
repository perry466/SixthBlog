<template>
  <div class="manage-page">
    <div class="page-header">
      <h1 class="page-title">评论管理</h1>
    </div>

    <div v-if="toast" :class="['toast', toastType]">{{ toast }}</div>

    <!-- 筛选 -->
    <div class="filters">
      <select v-model="filterApproved" @change="fetchList">
        <option value="">全部</option>
        <option value="false">待审核</option>
        <option value="true">已通过</option>
      </select>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="list.length === 0" class="empty">暂无评论</div>
    <div v-else class="list-table">
      <div v-for="item in list" :key="item.id" class="list-row">
        <div class="list-info">
          <div class="list-header">
            <strong>{{ item.nickname }}</strong>
            <span class="list-email">{{ item.email }}</span>
            <span class="list-article">文章: {{ item.article_title || '#' + item.article }}</span>
            <span class="list-date">{{ formatDate(item.created_at) }}</span>
            <span :class="['status-badge', item.is_approved ? 'approved' : 'pending']">
              {{ item.is_approved ? '已通过' : '待审核' }}
            </span>
          </div>
          <p class="list-content">{{ item.content }}</p>
        </div>
        <div class="list-actions">
          <button v-if="!item.is_approved" @click="approve(item.id)" class="btn-action btn-approve">通过</button>
          <button v-if="item.is_approved" @click="reject(item.id)" class="btn-action btn-reject">驳回</button>
          <button @click="confirmDelete(item.id)" class="btn-action btn-delete">删除</button>
        </div>
      </div>
    </div>

    <!-- 删除确认 -->
    <div v-if="showDeleteDialog" class="modal-overlay" @click.self="showDeleteDialog = false">
      <div class="modal">
        <h3>确认删除</h3>
        <p>确定要删除这条评论吗？此操作不可恢复。</p>
        <div class="modal-actions">
          <button @click="doDelete" class="btn-delete-confirm">确认删除</button>
          <button @click="showDeleteDialog = false" class="btn-cancel">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { getAdminComments, updateComment, deleteComment } from '../api/blog'

const router = useRouter()
const userStore = useUserStore()

const list = ref<any[]>([])
const loading = ref(false)
const filterApproved = ref('')
const toast = ref('')
const toastType = ref('')
const showDeleteDialog = ref(false)
const deleteTarget = ref(0)

const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN')

const showToast = (msg: string, type = 'success') => {
  toast.value = msg
  toastType.value = type
  setTimeout(() => { toast.value = '' }, 3000)
}

const fetchList = async () => {
  loading.value = true
  const params: any = {}
  if (filterApproved.value !== '') params.approved = filterApproved.value
  try {
    list.value = await getAdminComments(params) as any[]
  } catch { showToast('获取评论列表失败', 'error') }
  finally { loading.value = false }
}

const approve = async (id: number) => {
  try {
    await updateComment(id, { is_approved: true })
    showToast('评论已通过')
    fetchList()
  } catch { showToast('操作失败', 'error') }
}

const reject = async (id: number) => {
  try {
    await updateComment(id, { is_approved: false })
    showToast('评论已驳回')
    fetchList()
  } catch { showToast('操作失败', 'error') }
}

const confirmDelete = (id: number) => {
  deleteTarget.value = id
  showDeleteDialog.value = true
}

const doDelete = async () => {
  try {
    await deleteComment(deleteTarget.value)
    showToast('评论已删除')
    showDeleteDialog.value = false
    fetchList()
  } catch { showToast('删除失败', 'error') }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  fetchList()
})
</script>

<style scoped>
.manage-page { max-width: 900px; margin: 0 auto; }

.page-header { margin-bottom: 1.5rem; }
.page-title { color: var(--text-h); margin: 0; }

.toast { padding: 12px 24px; border-radius: 8px; margin-bottom: 16px; text-align: center; font-size: 14px; }
.toast.success { background: #d4edda; color: #155724; }
.toast.error { background: #f8d7da; color: #721c24; }

.filters { display: flex; gap: 12px; margin-bottom: 1.5rem; }
.filters select { padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text-h); }

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
.list-header { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 8px; font-size: 14px; color: var(--text-h); }
.list-email { color: var(--text-muted); font-size: 12px; }
.list-article { color: var(--accent); font-size: 12px; }
.list-date { color: var(--text-muted); font-size: 12px; }

.status-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.status-badge.approved { background: #d4edda; color: #155724; }
.status-badge.pending { background: #fff3cd; color: #856404; }

.list-content { margin: 0; font-size: 14px; color: var(--text); line-height: 1.6; }

.list-actions { display: flex; gap: 6px; flex-shrink: 0; }

.btn-action { padding: 6px 12px; border: 1px solid var(--border); border-radius: 4px; cursor: pointer; font-size: 12px; background: var(--bg); }
.btn-approve { color: #28a745; border-color: #28a745; }
.btn-approve:hover { background: #d4edda; }
.btn-reject { color: #ffc107; border-color: #ffc107; }
.btn-reject:hover { background: #fff3cd; }
.btn-delete { color: #dc3545; border-color: #dc3545; }
.btn-delete:hover { background: #f8d7da; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: var(--bg); border-radius: 12px; padding: 32px; max-width: 400px; width: 90%; }
.modal h3 { margin: 0 0 16px; color: var(--text-h); }
.modal p { color: var(--text); margin-bottom: 24px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; }
.btn-delete-confirm { padding: 8px 20px; background: #dc3545; color: white; border: none; border-radius: 6px; cursor: pointer; }
.btn-cancel { padding: 8px 20px; background: var(--social-bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; cursor: pointer; }

@media (max-width: 768px) { .list-row { flex-direction: column; } .list-actions { width: 100%; } }
</style>
