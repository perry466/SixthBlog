<template>
  <div class="user-manage">
    <div class="user-manage-header">
      <h1 class="page-title" style="margin-bottom:0">用户管理</h1>
      <button class="blog-btn blog-btn-primary" @click="openCreateDialog">+ 创建用户</button>
    </div>

    <div v-if="!loading" class="user-list">
      <div v-for="userItem in users" :key="userItem.id" class="user-card">
        <div class="user-info">
          <div v-if="userItem.avatar" class="user-avatar"><img :src="userItem.avatar" :alt="userItem.user.username" /></div>
          <div v-else class="user-avatar placeholder">{{ userItem.user.username.charAt(0).toUpperCase() }}</div>
          <div class="user-details">
            <div class="user-name-line">
              <span class="user-name">{{ userItem.user.username }}</span>
              <span v-if="userItem.user.is_staff" class="blog-badge" style="background:var(--accent-bg);color:var(--accent)">Staff</span>
            </div>
            <div class="user-email">{{ userItem.user.email || '未设置邮箱' }}</div>
            <div class="user-meta">
              <span :class="['role-badge', 'role-' + userItem.role]">{{ getRoleLabel(userItem.role) }}</span>
              <span class="join-date">加入于 {{ formatDate(userItem.created_at) }}</span>
            </div>
          </div>
        </div>
        <div class="user-actions">
          <button class="blog-btn blog-btn-ghost" style="padding:0.35rem 0.75rem" @click="openEditDialog(userItem)">编辑</button>
          <button class="blog-btn blog-btn-ghost" style="padding:0.35rem 0.75rem;color:#dc2626;border-color:#fecaca" @click="confirmDelete(userItem)" :disabled="userItem.user.is_staff && userItem.role === 'admin'">删除</button>
        </div>
      </div>
      <div v-if="users.length === 0" class="empty-state">暂无用户</div>
    </div>
    <div v-else class="loading-spinner">加载中...</div>

    <!-- Create/Edit Dialog -->
    <div v-if="showDialog" class="modal-overlay" @click.self="closeDialog">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ isEdit ? '编辑用户' : '创建用户' }}</h2>
          <button class="modal-close" @click="closeDialog">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>用户名 *</label>
            <input v-model="formData.username" type="text" placeholder="请输入用户名" class="blog-input" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="formData.email" type="email" placeholder="请输入邮箱" class="blog-input" />
          </div>
          <div class="form-group">
            <label>{{ isEdit ? '新密码（留空则不修改）' : '密码 *' }}</label>
            <input v-model="formData.password" type="password" :placeholder="isEdit ? '留空则不修改密码' : '至少6位'" class="blog-input" />
          </div>
          <div class="form-group">
            <label>角色</label>
            <select v-model="formData.role" class="blog-input blog-select">
              <option value="subscriber">订阅者</option>
              <option value="author">作者</option>
              <option value="editor">编辑</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          <div v-if="isEdit" class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="formData.is_staff" style="accent-color:var(--accent)" />
              <span>Staff 权限（可访问后台）</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="blog-btn blog-btn-ghost" @click="closeDialog">取消</button>
          <button class="blog-btn blog-btn-primary" @click="handleSubmit" :disabled="submitting">{{ submitting ? '提交中...' : (isEdit ? '保存' : '创建') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="modal" style="max-width:380px">
        <div class="modal-header">
          <h2>确认删除</h2>
          <button class="modal-close" @click="showDeleteConfirm = false"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg></button>
        </div>
        <div class="modal-body">
          <p>确定要删除用户 <strong>{{ deleteUserItem?.user.username }}</strong> 吗？此操作不可恢复。</p>
        </div>
        <div class="modal-footer">
          <button class="blog-btn blog-btn-ghost" @click="showDeleteConfirm = false">取消</button>
          <button class="blog-btn blog-btn-ghost" style="color:#dc2626;border-color:#fecaca" @click="handleDelete" :disabled="deleting">{{ deleting ? '删除中...' : '确认删除' }}</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.show" :class="['toast', 'toast-' + toast.type]">{{ toast.message }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { getUsers, createUser, updateUser, deleteUser } from '../api/user'

interface UserProfile { id: number; user: { id: number; username: string; email: string; is_staff: boolean }; role: string; avatar: string | null; bio: string; created_at: string }

const router = useRouter()
const userStore = useUserStore()
const users = ref<UserProfile[]>([])
const loading = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const showDeleteConfirm = ref(false)
const deleteUserItem = ref<UserProfile | null>(null)
const deleting = ref(false)
const editingUserId = ref<number | null>(null)

const formData = reactive({ username: '', email: '', password: '', role: 'subscriber', is_staff: false })
const toast = reactive({ show: false, message: '', type: 'success' as 'success' | 'error' })
const roleLabels: Record<string, string> = { admin: '管理员', editor: '编辑', author: '作者', subscriber: '订阅者' }

const getRoleLabel = (role: string) => roleLabels[role] || role
const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN')

function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.message = message; toast.type = type; toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}
async function fetchUsers() {
  loading.value = true
  try { users.value = await getUsers() as UserProfile[] }
  catch { showToast('获取用户列表失败', 'error') }
  finally { loading.value = false }
}

function openCreateDialog() {
  isEdit.value = false; editingUserId.value = null
  formData.username = ''; formData.email = ''; formData.password = ''; formData.role = 'subscriber'; formData.is_staff = false
  showDialog.value = true
}
function openEditDialog(userItem: UserProfile) {
  isEdit.value = true; editingUserId.value = userItem.user.id
  formData.username = userItem.user.username; formData.email = userItem.user.email; formData.password = ''; formData.role = userItem.role; formData.is_staff = userItem.user.is_staff
  showDialog.value = true
}
function closeDialog() { showDialog.value = false }
async function handleSubmit() {
  if (!formData.username) { showToast('请输入用户名', 'error'); return }
  if (!isEdit.value && !formData.password) { showToast('请输入密码', 'error'); return }
  submitting.value = true
  try {
    if (isEdit.value && editingUserId.value) {
      const data: any = { username: formData.username, email: formData.email, role: formData.role, is_staff: formData.is_staff }
      if (formData.password) data.password = formData.password
      await updateUser(editingUserId.value, data)
      showToast('用户更新成功')
    } else {
      await createUser({ username: formData.username, email: formData.email, password: formData.password, is_staff: formData.is_staff, role: formData.role })
      showToast('用户创建成功')
    }
    closeDialog(); await fetchUsers()
  } catch (error: any) {
    const msg = error.response?.data?.username?.[0] || error.response?.data?.error || '操作失败'
    showToast(msg, 'error')
  } finally { submitting.value = false }
}
function confirmDelete(userItem: UserProfile) { deleteUserItem.value = userItem; showDeleteConfirm.value = true }
async function handleDelete() {
  if (!deleteUserItem.value) return; deleting.value = true
  try { await deleteUser(deleteUserItem.value.user.id); showToast('用户已删除'); showDeleteConfirm.value = false; await fetchUsers() }
  catch (error: any) { showToast(error.response?.data?.error || '删除失败', 'error') }
  finally { deleting.value = false }
}

onMounted(async () => {
  await userStore.fetchCurrentUser()
  const user = userStore.user
  if (!user || !(user.is_superuser || user.is_staff)) {
    showToast('权限不足，仅管理员可访问', 'error')
    router.push('/home'); return
  }
  await fetchUsers()
})
</script>

<style scoped>
.user-manage { max-width: 900px; margin: 0 auto; }
.user-manage-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.user-list { display: flex; flex-direction: column; gap: 0.75rem; }

.user-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 1rem 1.25rem;
  display: flex; justify-content: space-between; align-items: center;
  transition: all 0.2s;
}
.user-card:hover { border-color: var(--accent); box-shadow: var(--shadow-sm); }

.user-info { display: flex; align-items: center; gap: 0.875rem; }
.user-avatar { width: 44px; height: 44px; border-radius: 50%; overflow: hidden; flex-shrink: 0; }
.user-avatar img { width: 100%; height: 100%; object-fit: cover; }
.user-avatar.placeholder { background: var(--gradient-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 700; }
.user-details { display: flex; flex-direction: column; gap: 0.15rem; }
.user-name-line { display: flex; align-items: center; gap: 0.5rem; }
.user-name { font-size: 0.95rem; font-weight: 600; color: var(--text-h); }
.user-email { font-size: 0.78rem; color: var(--text-muted); }
.user-meta { display: flex; align-items: center; gap: 0.75rem; margin-top: 0.15rem; }
.role-badge { font-size: 0.7rem; font-weight: 600; padding: 0.15rem 0.6rem; border-radius: 999px; }
.role-admin { background: #fee2e2; color: #dc2626; }
.role-editor { background: #dbeafe; color: #2563eb; }
.role-author { background: #dcfce7; color: #16a34a; }
.role-subscriber { background: #f1f5f9; color: #64748b; }
.join-date { font-size: 0.7rem; color: var(--text-muted); }

.user-actions { display: flex; gap: 0.5rem; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
  animation: fadeIn 0.15s ease;
}
.modal {
  background: var(--bg-card); border-radius: var(--radius-xl);
  width: 90%; max-width: 480px; max-height: 90vh; overflow-y: auto;
  box-shadow: var(--shadow-lg);
  animation: modalIn 0.2s ease;
}
@keyframes modalIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border);
}
.modal-header h2 { margin: 0; font-size: 1.125rem; }
.modal-close { background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 0.25rem; border-radius: var(--radius-sm); transition: all 0.15s; }
.modal-close:hover { background: var(--accent-bg); color: var(--accent); }
.modal-body { padding: 1.5rem; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 0.75rem;
  padding: 1rem 1.5rem; border-top: 1px solid var(--border);
}
.form-group { margin-bottom: 1.25rem; }
.form-group:last-child { margin-bottom: 0; }
.form-group label { display: block; font-size: 0.82rem; font-weight: 550; color: var(--text); margin-bottom: 0.35rem; }
.checkbox-label { display: flex !important; align-items: center; gap: 0.5rem; cursor: pointer; }
.checkbox-label input[type="checkbox"] { width: 18px; height: 18px; }

/* Toast */
.toast {
  position: fixed; top: 1.5rem; right: 1.5rem;
  padding: 0.75rem 1.25rem; border-radius: var(--radius);
  font-size: 0.85rem; z-index: 2000;
  box-shadow: var(--shadow-lg); animation: fadeIn 0.2s ease;
}
.toast-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.toast-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .user-card { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
  .user-actions { width: 100%; justify-content: flex-end; }
}
</style>
