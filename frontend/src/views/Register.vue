<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">创建账号</h1>
        <p class="auth-subtitle">加入我们，开始写作</p>
      </div>
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input id="username" v-model="form.username" type="text" placeholder="请输入用户名" required class="blog-input" />
        </div>
        <div class="form-group">
          <label for="email">邮箱 <span class="optional">(可选)</span></label>
          <input id="email" v-model="form.email" type="email" placeholder="请输入邮箱" class="blog-input" />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input id="password" v-model="form.password" type="password" placeholder="至少6位" required minlength="6" class="blog-input" />
        </div>
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input id="confirmPassword" v-model="confirmPassword" type="password" placeholder="再次输入密码" required class="blog-input" />
        </div>
        <div v-if="message" :class="['form-message', messageType === 'success' ? 'msg-success' : 'msg-error']">{{ message }}</div>
        <button type="submit" :disabled="loading" class="blog-btn blog-btn-primary" style="width:100%;padding:0.7rem">{{ loading ? '注册中...' : '注册' }}</button>
      </form>
          </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const form = ref({ username: '', email: '', password: '' })
const confirmPassword = ref('')
const message = ref('')
const messageType = ref('')
const loading = ref(false)

const handleRegister = async () => {
  if (form.value.password !== confirmPassword.value) {
    message.value = '两次输入的密码不一致'; messageType.value = 'error'; return
  }
  loading.value = true; message.value = ''
  const result = await userStore.register(form.value.username, form.value.password, form.value.email || undefined)
  if (result.success) {
    message.value = result.message; messageType.value = 'success'
    setTimeout(() => router.push('/sixth-admin'), 1000)
  } else {
    message.value = result.message; messageType.value = 'error'
  }
  loading.value = false
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 12rem);
}
.auth-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow);
}
.auth-header { text-align: center; margin-bottom: 2rem; }
.auth-title { font-size: 1.5rem; font-weight: 700; margin: 0 0 0.25rem; }
.auth-subtitle { font-size: 0.9rem; color: var(--text-muted); margin: 0; }
.optional { font-weight: 400; color: var(--text-muted); }
.auth-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-group label { font-size: 0.82rem; font-weight: 550; color: var(--text); }
.form-message { padding: 0.65rem 0.875rem; border-radius: var(--radius); font-size: 0.82rem; text-align: center; }
.msg-success { background: #dcfce7; color: #166534; }
.msg-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.auth-footer { text-align: center; margin-top: 1.5rem; font-size: 0.85rem; color: var(--text-muted); }
.auth-footer a { font-weight: 600; }
</style>
