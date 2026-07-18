<template>
  <div class="profile-page">
    <h1 class="page-title">个人资料</h1>

    <div v-if="toast" :class="['toast', toastType]">{{ toast }}</div>

    <div v-if="!isLoggedIn" class="empty-state">请先登录</div>

    <div v-else class="profile-container">
      <!-- 头像区域 -->
      <div class="profile-avatar-section">
        <div class="avatar-wrapper">
          <img v-if="avatarPreview" :src="avatarPreview" class="avatar-img" />
          <div v-else class="avatar-placeholder">{{ user?.username?.charAt(0).toUpperCase() }}</div>
        </div>
        <div class="avatar-actions">
          <button @click="triggerAvatar" class="blog-btn blog-btn-soft">更换头像</button>
          <input ref="avatarInput" type="file" accept="image/*" hidden @change="handleAvatar" />
        </div>
      </div>

      <!-- 基本信息 -->
      <div class="profile-section">
        <h3>基本信息</h3>
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" type="text" disabled class="blog-input" />
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="form.email" type="email" placeholder="输入邮箱" class="blog-input" />
        </div>
        <div class="form-group">
          <label>个人简介</label>
          <textarea v-model="form.bio" rows="4" placeholder="介绍一下自己..." class="blog-input" style="resize:vertical"></textarea>
        </div>
        <div class="form-group">
          <label>角色</label>
          <input :value="roleLabel" type="text" disabled class="blog-input" />
        </div>
        <div class="form-group">
          <label>注册时间</label>
          <input :value="formatDate(user?.date_joined)" type="text" disabled class="blog-input" />
        </div>
        <button @click="saveProfile" :disabled="saving" class="blog-btn blog-btn-primary">
          {{ saving ? '保存中...' : '保存修改' }}
        </button>
      </div>

      <!-- 修改密码 -->
      <div class="profile-section">
        <h3>修改密码</h3>
        <div class="form-group">
          <label>当前密码</label>
          <input v-model="passwordForm.oldPassword" type="password" placeholder="输入当前密码" class="blog-input" />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input v-model="passwordForm.newPassword" type="password" placeholder="输入新密码" class="blog-input" />
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <input v-model="passwordForm.confirmPassword" type="password" placeholder="再次输入新密码" class="blog-input" />
        </div>
        <button @click="changePassword" :disabled="changingPwd" class="blog-btn blog-btn-soft">
          {{ changingPwd ? '修改中...' : '修改密码' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { updateProfile, updateUser } from '../api/user'

const router = useRouter()
const userStore = useUserStore()

const user = computed(() => userStore.user)
const isLoggedIn = computed(() => userStore.isLoggedIn)

const avatarInput = ref<HTMLInputElement | null>(null)
const avatarPreview = ref<string | null>(null)
const avatarFile = ref<File | null>(null)
const saving = ref(false)
const changingPwd = ref(false)
const toast = ref('')
const toastType = ref('')

const form = ref({
  username: '',
  email: '',
  bio: '',
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const roleLabel = computed(() => {
  if (!user.value) return ''
  if (user.value.is_superuser) return '超级管理员'
  if (user.value.is_staff) return '管理员'
  const roleMap: Record<string, string> = { admin: '管理员', editor: '编辑', author: '作者', user: '普通用户' }
  return roleMap[user.value.role || ''] || '普通用户'
})

const formatDate = (d: string | undefined) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

const showToast = (msg: string, type = 'success') => {
  toast.value = msg
  toastType.value = type
  setTimeout(() => { toast.value = '' }, 3000)
}

const triggerAvatar = () => avatarInput.value?.click()

const handleAvatar = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) {
    avatarFile.value = file
    avatarPreview.value = URL.createObjectURL(file)
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const data: any = {}
    if (form.value.email) data.email = form.value.email
    if (form.value.bio !== undefined) data.bio = form.value.bio
    if (avatarFile.value) data.avatar = avatarFile.value

    await updateProfile(data)
    await userStore.fetchCurrentUser()
    showToast('资料更新成功')
  } catch (error: any) {
    showToast(error.response?.data?.error || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  if (!passwordForm.value.oldPassword) { showToast('请输入当前密码', 'error'); return }
  if (!passwordForm.value.newPassword) { showToast('请输入新密码', 'error'); return }
  if (passwordForm.value.newPassword.length < 6) { showToast('新密码至少6位', 'error'); return }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) { showToast('两次密码不一致', 'error'); return }

  changingPwd.value = true
  try {
    // 通过管理员更新用户接口修改自己的密码
    if (user.value?.id) {
      await updateUser(user.value.id, { password: passwordForm.value.newPassword })
    }
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
    showToast('密码修改成功')
  } catch (error: any) {
    showToast(error.response?.data?.error || '修改密码失败', 'error')
  } finally {
    changingPwd.value = false
  }
}

onMounted(() => {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }
  if (user.value) {
    form.value.username = user.value.username
    form.value.email = user.value.email || ''
    form.value.bio = user.value.bio || ''
    if (user.value.avatar) avatarPreview.value = user.value.avatar
  }
})
</script>

<style scoped>
.profile-page { max-width: 640px; margin: 0 auto; }

.page-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--text-h);
}

.toast {
  padding: 12px 24px;
  border-radius: 8px;
  margin-bottom: 16px;
  text-align: center;
  font-size: 14px;
}
.toast.success { background: #d4edda; color: #155724; }
.toast.error { background: #f8d7da; color: #721c24; }

.empty-state { text-align: center; padding: 48px; color: var(--text); font-size: 18px; }

.profile-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
}

.avatar-wrapper {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid var(--accent);
}

.avatar-img { width: 100%; height: 100%; object-fit: cover; }

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
}

.profile-section {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
}

.profile-section h3 {
  margin: 0 0 1rem;
  color: var(--text-h);
  font-size: 1.1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-h);
  margin-bottom: 0.35rem;
}
</style>
