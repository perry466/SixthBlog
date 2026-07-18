<template>
  <div class="guestbook-page">
    <h1 class="page-title">留言板</h1>

    <form @submit.prevent="submitMessage" class="message-form">
      <div class="form-row">
        <input v-model="form.nickname" type="text" placeholder="昵称 *" required class="blog-input" />
        <input v-model="form.email" type="email" placeholder="邮箱 *" required class="blog-input" />
      </div>
      <textarea v-model="form.content" placeholder="写下你的留言..." required class="blog-input" style="min-height:110px;resize:vertical;margin-bottom:0.75rem"></textarea>
      <button type="submit" :disabled="loading" class="blog-btn blog-btn-primary">{{ loading ? '提交中...' : '提交留言' }}</button>
      <div v-if="message" :class="['form-message', messageType === 'success' ? 'msg-success' : 'msg-error']">{{ message }}</div>
    </form>

    <div class="messages-list">
      <div v-if="messages.length === 0" class="empty-state">暂无留言，快来发表第一条留言吧</div>
      <div v-for="msg in messages" :key="msg.id" class="message-item">
        <div class="message-avatar">{{ msg.nickname.charAt(0).toUpperCase() }}</div>
        <div class="message-body">
          <div class="message-header">
            <span class="message-nickname">{{ msg.nickname }}</span>
            <span class="message-date">{{ formatDate(msg.created_at) }}</span>
          </div>
          <p class="message-content">{{ msg.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getGuestbook, createGuestbook } from '../api/blog'

const form = ref({ nickname: '', email: '', content: '' })
const messages = ref<any[]>([])
const loading = ref(false)
const message = ref('')
const messageType = ref('')

const submitMessage = async () => {
  loading.value = true; message.value = ''
  try {
    await createGuestbook(form.value)
    message.value = '留言提交成功！审核通过后将显示。'; messageType.value = 'success'
    form.value = { nickname: '', email: '', content: '' }
  } catch { message.value = '留言提交失败，请重试。'; messageType.value = 'error' }
  loading.value = false
}
const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })

onMounted(async () => { try { messages.value = await getGuestbook() } catch { /* empty */ } })
</script>

<style scoped>
.guestbook-page { max-width: 800px; margin: 0 auto; }

.message-form {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-xl); padding: 1.5rem;
  margin-bottom: 2rem;
}
.form-row { display: flex; gap: 0.75rem; margin-bottom: 0.75rem; }
.form-message { margin-top: 0.75rem; padding: 0.65rem 0.875rem; border-radius: var(--radius); font-size: 0.82rem; text-align: center; }
.msg-success { background: #dcfce7; color: #166534; }
.msg-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

.messages-list { display: flex; flex-direction: column; gap: 0.75rem; }
.message-item {
  display: flex; gap: 0.75rem;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1rem;
  transition: all 0.2s;
}
.message-item:hover { border-color: var(--accent); }
.message-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--gradient-primary);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem; font-weight: 700; flex-shrink: 0;
}
.message-body { flex: 1; min-width: 0; }
.message-header { display: flex; justify-content: space-between; margin-bottom: 0.25rem; }
.message-nickname { font-size: 0.85rem; font-weight: 600; color: var(--text-h); }
.message-date { font-size: 0.75rem; color: var(--text-muted); }
.message-content { font-size: 0.875rem; color: var(--text); line-height: 1.6; margin: 0; }

@media (max-width: 768px) { .form-row { flex-direction: column; } }
</style>
