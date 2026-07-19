<template>
  <div class="setup-wrapper">
    <div class="setup-card">
      <!-- Step 1: Welcome -->
      <div v-if="step === 1" class="setup-step">
        <div class="setup-icon">🚀</div>
        <h1>欢迎使用 SixthBlog</h1>
        <p class="setup-desc">在开始之前，需要完成一些基本配置。整个过程只需一两分钟。</p>
        <div class="setup-checklist">
          <div class="check-item"><span class="check-icon">📋</span> 检查数据库连接</div>
          <div class="check-item"><span class="check-icon">👤</span> 创建管理员账号</div>
          <div class="check-item"><span class="check-icon">⚙️</span> 设置站点信息</div>
        </div>
        <button class="btn-primary" @click="goStep2">开始配置</button>
      </div>

      <!-- Step 2: Database Check -->
      <div v-if="step === 2" class="setup-step">
        <div class="step-indicator">步骤 1/3</div>
        <h2>数据库连接</h2>
        <p class="setup-desc">正在检测数据库连接状态...</p>
        <div v-if="checking" class="status-box loading">
          <span class="spinner"></span> 正在连接数据库...
        </div>
        <div v-else-if="dbOk" class="status-box success">
          ✅ 数据库连接正常
        </div>
        <div v-else class="status-box error">
          ❌ 数据库连接失败
          <p class="error-msg">{{ dbError }}</p>
        </div>
        <div class="btn-row">
          <button class="btn-secondary" @click="step = 1">上一步</button>
          <button class="btn-primary" :disabled="!dbOk" @click="step = 3">下一步</button>
        </div>
      </div>

      <!-- Step 3: Admin Account -->
      <div v-if="step === 3" class="setup-step">
        <div class="step-indicator">步骤 2/3</div>
        <h2>创建管理员账号</h2>
        <p class="setup-desc">此账号用于登录后台管理系统</p>
        <div class="form-group">
          <label>用户名 <span class="required">*</span></label>
          <input v-model="adminForm.username" type="text" placeholder="至少3个字符" />
          <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="adminForm.email" type="email" placeholder="admin@example.com" />
        </div>
        <div class="form-group">
          <label>密码 <span class="required">*</span></label>
          <input v-model="adminForm.password" type="password" placeholder="至少6个字符" />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>
        <div class="form-group">
          <label>确认密码 <span class="required">*</span></label>
          <input v-model="adminForm.password2" type="password" placeholder="再次输入密码" />
          <span v-if="errors.password2" class="field-error">{{ errors.password2 }}</span>
        </div>
        <div class="btn-row">
          <button class="btn-secondary" @click="step = 2">上一步</button>
          <button class="btn-primary" @click="goToStep4">下一步</button>
        </div>
      </div>

      <!-- Step 4: Site Info -->
      <div v-if="step === 4" class="setup-step">
        <div class="step-indicator">步骤 3/3</div>
        <h2>站点信息</h2>
        <p class="setup-desc">给你的博客取个好名字吧</p>
        <div class="form-group">
          <label>网站标题 <span class="required">*</span></label>
          <input v-model="siteForm.site_title" type="text" placeholder="我的博客" />
          <span v-if="errors.site_title" class="field-error">{{ errors.site_title }}</span>
        </div>
        <div class="form-group">
          <label>网站描述</label>
          <input v-model="siteForm.site_description" type="text" placeholder="记录生活，分享技术" />
        </div>
        <div class="btn-row">
          <button class="btn-secondary" @click="step = 3">上一步</button>
          <button class="btn-primary" :disabled="installing" @click="doInstall">
            <span v-if="installing" class="spinner"></span>
            {{ installing ? '正在安装...' : '完成安装' }}
          </button>
        </div>
      </div>

      <!-- Step 5: Complete -->
      <div v-if="step === 5" class="setup-step">
        <div class="setup-icon">🎉</div>
        <h2>安装完成！</h2>
        <p class="setup-desc">{{ installMessage }}</p>
        <button class="btn-primary" @click="goHome">前往首页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { checkDatabase, install } from '../api/setup'

const router = useRouter()

const step = ref(1)
const checking = ref(true)
const dbOk = ref(false)
const dbError = ref('')
const installing = ref(false)
const installMessage = ref('')

const adminForm = reactive({
  username: '',
  email: '',
  password: '',
  password2: '',
})

const siteForm = reactive({
  site_title: '',
  site_description: '',
})

const errors = reactive({
  username: '',
  password: '',
  password2: '',
  site_title: '',
})

onMounted(() => {
  // component mounted, nothing to do
})

async function testDb() {
  checking.value = true
  try {
    const res = await checkDatabase() as any
    dbOk.value = res.ok
    if (!res.ok) {
      dbError.value = res.error || '未知错误'
    }
  } catch (e: any) {
    dbOk.value = false
    dbError.value = e?.response?.data?.error || e?.message || '无法连接到服务器'
  } finally {
    checking.value = false
  }
}

function goStep2() {
  step.value = 2
  testDb()
}

function validateAdmin(): boolean {
  errors.username = ''
  errors.password = ''
  errors.password2 = ''

  if (!adminForm.username || adminForm.username.length < 3) {
    errors.username = '用户名至少需要 3 个字符'
    return false
  }
  if (!adminForm.password || adminForm.password.length < 6) {
    errors.password = '密码至少需要 6 个字符'
    return false
  }
  if (adminForm.password !== adminForm.password2) {
    errors.password2 = '两次密码不一致'
    return false
  }
  return true
}

function goToStep4() {
  if (validateAdmin()) {
    step.value = 4
  }
}

async function doInstall() {
  errors.site_title = ''
  if (!siteForm.site_title.trim()) {
    errors.site_title = '请输入网站标题'
    return
  }

  installing.value = true
  try {
    const res = await install({
      username: adminForm.username,
      email: adminForm.email,
      password: adminForm.password,
      site_title: siteForm.site_title,
      site_description: siteForm.site_description,
    }) as any
    installMessage.value = res.message || '安装完成！'
    step.value = 5
  } catch (e: any) {
    const msg = e?.response?.data?.error || e?.message || '安装失败，请重试'
    alert(msg)
  } finally {
    installing.value = false
  }
}

function goHome() {
  router.push('/home').then(() => {
    window.location.reload()
  })
}
</script>

<style scoped>
.setup-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 20px;
}

.setup-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 48px;
  width: 100%;
  max-width: 480px;
  color: #e0e0e0;
}

.setup-step {
  text-align: center;
}

.setup-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

h1 { font-size: 24px; margin-bottom: 12px; color: #fff; }
h2 { font-size: 20px; margin-bottom: 12px; color: #fff; }

.setup-desc {
  color: #999;
  margin-bottom: 24px;
  line-height: 1.6;
}

.step-indicator {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.setup-checklist {
  text-align: left;
  margin-bottom: 32px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 16px 20px;
}

.check-item {
  padding: 8px 0;
  font-size: 14px;
  color: #ccc;
}

.check-icon {
  margin-right: 8px;
}

.status-box {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  font-size: 14px;
}

.status-box.loading { background: rgba(255, 255, 255, 0.05); color: #999; }
.status-box.success { background: rgba(0, 255, 0, 0.08); color: #4ade80; }
.status-box.error { background: rgba(255, 0, 0, 0.08); color: #f87171; }

.error-msg {
  font-size: 12px;
  margin-top: 8px;
  word-break: break-all;
}

.form-group {
  text-align: left;
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: #999;
  margin-bottom: 6px;
}

.required { color: #f87171; }

.form-group input {
  width: 100%;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  color: #e0e0e0;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: #4fc3f7;
}

.field-error {
  font-size: 12px;
  color: #f87171;
  margin-top: 4px;
  display: block;
}

.btn-row {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
}

.btn-primary {
  padding: 10px 32px;
  background: linear-gradient(135deg, #4fc3f7, #2196f3);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:hover { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-secondary {
  padding: 10px 32px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: #ccc;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secondary:hover { background: rgba(255, 255, 255, 0.12); }

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
