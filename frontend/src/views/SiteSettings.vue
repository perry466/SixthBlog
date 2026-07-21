<template>
  <div class="settings-page">
    <h1 class="page-title">站点设置</h1>

    <div v-if="loading" class="loading">加载中...</div>

    <form v-else @submit.prevent="handleSave" class="settings-form">
      <!-- 基本信息 -->
      <fieldset class="form-section">
        <legend>基本信息</legend>
        <div class="form-row-2">
          <div class="form-group">
            <label>网站标题</label>
            <input v-model="form.site_title" type="text" class="blog-input" />
          </div>
          <div class="form-group">
            <label>每页文章数</label>
            <input v-model.number="form.articles_per_page" type="number" min="1" max="50" class="blog-input" style="width:120px" />
          </div>
        </div>
        <div class="form-group">
          <label>网站描述</label>
          <textarea v-model="form.site_description" rows="3" class="blog-input" style="resize:vertical"></textarea>
        </div>
      </fieldset>

      <!-- 媒体资源 -->
      <fieldset class="form-section">
        <legend>媒体资源</legend>
        <div class="form-row-2">
          <div class="form-group">
            <label>网站 Logo</label>
            <div class="img-field-row">
              <input v-model="form.site_logo" type="text" placeholder="图片URL" class="blog-input" style="flex:1" />
              <button type="button" class="blog-btn blog-btn-ghost" style="padding:0.4rem 0.6rem;font-size:0.75rem;white-space:nowrap" @click="mediaField = 'site_logo'">媒体库</button>
            </div>
            <span class="form-hint">显示在导航栏左侧</span>
          </div>
          <div class="form-group">
            <label>网站图标 (Favicon)</label>
            <div class="img-field-row">
              <input v-model="form.site_favicon" type="text" placeholder="图片URL" class="blog-input" style="flex:1" />
              <button type="button" class="blog-btn blog-btn-ghost" style="padding:0.4rem 0.6rem;font-size:0.75rem;white-space:nowrap" @click="mediaField = 'site_favicon'">媒体库</button>
            </div>
            <span class="form-hint">浏览器标签页图标</span>
          </div>
        </div>
        <div class="form-group">
          <label>博客背景图</label>
          <div class="img-field-row">
            <input v-model="form.blog_background" type="text" placeholder="图片URL，留空使用默认" class="blog-input" style="flex:1" />
            <button type="button" class="blog-btn blog-btn-ghost" style="padding:0.4rem 0.6rem;font-size:0.75rem;white-space:nowrap" @click="mediaField = 'blog_background'">媒体库</button>
          </div>
        </div>
        <MediaSelector
          :visible="!!mediaField"
          @close="mediaField = ''"
          @selected="handleSiteMediaSelected"
        />
      </fieldset>

      <!-- 首页动画 -->
      <fieldset class="form-section">
        <legend>开屏动画</legend>
        <div class="form-row-3">
          <div class="form-group">
            <label>动画文字</label>
            <input v-model="form.splash_animation_text" type="text" placeholder="留空则关闭开屏动画" class="blog-input" />
          </div>
          <div class="form-group">
            <label>背景色</label>
            <input v-model="form.splash_animation_bg" type="color" class="color-input" />
          </div>
          <div class="form-group">
            <label>动画主题</label>
            <select v-model="form.splash_animation_theme" class="blog-input blog-select">
              <option value="default">默认</option>
              <option value="minimal">极简</option>
              <option value="colorful">多彩</option>
            </select>
          </div>
        </div>
      </fieldset>

      <!-- 关于页面 -->
      <fieldset class="form-section">
        <legend>关于页面</legend>
        <div class="form-group">
          <label>关于内容 (Markdown)</label>
          <textarea v-model="form.about_content" rows="8" class="blog-input" style="resize:vertical;font-family:monospace" placeholder="支持 Markdown 格式"></textarea>
        </div>
      </fieldset>

      <!-- 社交链接 -->
      <fieldset class="form-section">
        <legend>社交链接</legend>
        <div class="social-list">
          <div v-for="(value, key) in form.social_links" :key="key" class="social-row">
            <input v-model="form.social_links[key]" type="text" :placeholder="key" class="blog-input" style="flex:1" />
            <button type="button" class="blog-btn blog-btn-ghost" style="color:#dc3545;border-color:#fecaca;font-size:0.75rem" @click="delete form.social_links[key]">删除</button>
          </div>
        </div>
        <div class="social-add" style="display:flex;gap:8px;margin-top:8px">
          <input v-model="newSocialKey" type="text" placeholder="平台名（如 github）" class="blog-input" style="flex:1" />
          <input v-model="newSocialValue" type="text" placeholder="链接URL" class="blog-input" style="flex:2" />
          <button type="button" class="blog-btn blog-btn-primary" style="padding:0.45rem 1rem;font-size:0.8rem" @click="addSocial" :disabled="!newSocialKey.trim() || !newSocialValue.trim()">添加</button>
        </div>
      </fieldset>

      <!-- 问候语 -->
      <fieldset class="form-section">
        <legend>随机问候语</legend>
        <div class="welcome-list">
          <div v-for="(msg, idx) in form.welcome_messages" :key="idx" class="welcome-row">
            <input v-model="form.welcome_messages[idx]" type="text" class="blog-input" style="flex:1" />
            <button type="button" class="blog-btn blog-btn-ghost" style="color:#dc3545;border-color:#fecaca;font-size:0.75rem" @click="form.welcome_messages.splice(idx, 1)">删除</button>
          </div>
        </div>
        <div style="display:flex;gap:8px;margin-top:8px">
          <input v-model="newWelcomeMsg" type="text" placeholder="输入新的问候语" class="blog-input" style="flex:1" @keyup.enter="addWelcome" />
          <button type="button" class="blog-btn blog-btn-primary" style="padding:0.45rem 1rem;font-size:0.8rem" @click="addWelcome" :disabled="!newWelcomeMsg.trim()">添加</button>
        </div>
      </fieldset>

      <!-- 其他 -->
      <fieldset class="form-section">
        <legend>其他</legend>
        <label class="checkbox-label">
          <input type="checkbox" v-model="form.show_article_stats" style="accent-color:var(--accent)" />
          <span>展示文章统计信息</span>
        </label>
      </fieldset>

    </form>

    <!-- 底部固定保存栏 -->
    <div class="save-bar">
      <div class="save-bar-inner">
        <div v-if="saveMsg" :class="['save-msg', saveMsgType]">
          <svg v-if="saveMsgType === 'success'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
          {{ saveMsg }}
        </div>
        <button type="button" class="blog-btn blog-btn-primary" :disabled="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getSiteConfig } from '../api/blog'
import api from '../utils/request'
import MediaSelector from '../components/MediaSelector.vue'

const loading = ref(true)
const saving = ref(false)
const saveMsg = ref('')
const saveMsgType = ref<'success' | 'error'>('success')
const newSocialKey = ref('')
const newSocialValue = ref('')
const newWelcomeMsg = ref('')
const mediaField = ref('')  // 当前正在选择图片的字段名

interface SettingsForm {
  site_title: string
  site_description: string
  site_logo: string
  site_favicon: string
  blog_background: string
  about_content: string
  splash_animation_text: string
  splash_animation_bg: string
  splash_animation_theme: string
  articles_per_page: number
  show_article_stats: boolean
  social_links: Record<string, string>
  welcome_messages: string[]
}

const form = reactive<SettingsForm>({
  site_title: '',
  site_description: '',
  site_logo: '',
  site_favicon: '',
  blog_background: '',
  about_content: '',
  splash_animation_text: '',
  splash_animation_bg: '#1a1a2e',
  splash_animation_theme: 'default',
  articles_per_page: 10,
  show_article_stats: true,
  social_links: {},
  welcome_messages: [],
})

const showMsg = (msg: string, type: 'success' | 'error' = 'success') => {
  saveMsg.value = msg
  saveMsgType.value = type
  if (type === 'success') {
    setTimeout(() => { saveMsg.value = '' }, 3000)
  }
}

const addSocial = () => {
  const k = newSocialKey.value.trim()
  const v = newSocialValue.value.trim()
  if (k && v) {
    form.social_links[k] = v
    newSocialKey.value = ''
    newSocialValue.value = ''
  }
}

const addWelcome = () => {
  const msg = newWelcomeMsg.value.trim()
  if (msg) {
    form.welcome_messages.push(msg)
    newWelcomeMsg.value = ''
  }
}

// 从媒体库选择图片填入对应字段
const handleSiteMediaSelected = (url: string) => {
  if (mediaField.value && mediaField.value in form) {
    ;(form as any)[mediaField.value] = url
  }
  mediaField.value = ''
}

const handleSave = async () => {
  saving.value = true
  saveMsg.value = ''
  try {
    await api.patch('/blog/admin/site-config/', form)
    showMsg('设置已保存')
  } catch (e: any) {
    const detail = e.response?.data
    // DRF 返回的验证错误可能是 {field: ['error msg']} 格式
    if (detail && typeof detail === 'object') {
      const errors = Object.entries(detail)
        .filter(([k]) => k !== 'detail')
        .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
      if (errors.length) {
        showMsg(errors.join('；'), 'error')
      } else if (detail.detail) {
        showMsg(detail.detail, 'error')
      } else {
        showMsg('保存失败，请检查输入', 'error')
      }
    } else {
      showMsg('保存失败，请检查网络连接', 'error')
    }
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const config: any = await getSiteConfig()
    Object.keys(form).forEach(key => {
      if (key in config) {
        (form as any)[key] = config[key]
      }
    })
    // 确保 social_links 是对象
    if (!form.social_links || typeof form.social_links !== 'object') {
      form.social_links = {}
    }
    // 确保 welcome_messages 是数组
    if (!Array.isArray(form.welcome_messages)) {
      form.welcome_messages = []
    }
  } catch {
    showMsg('加载站点配置失败', 'error')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.settings-page { max-width: 800px; margin: 0 auto; padding-bottom: 80px; }

.loading { text-align: center; padding: 48px; color: var(--text-muted); }

.settings-form { display: flex; flex-direction: column; gap: 1.5rem; }

.form-section {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
}
.form-section legend {
  font-size: 0.95rem;
  font-weight: 650;
  color: var(--text-h);
  padding: 0 0.5rem;
}

.form-group { margin-bottom: 0.75rem; }
.form-group:last-child { margin-bottom: 0; }
.form-group label { display: block; font-size: 0.8rem; font-weight: 550; color: var(--text); margin-bottom: 0.3rem; }

.form-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-row-3 { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1rem; }

.form-hint { font-size: 0.72rem; color: var(--text-muted); margin-top: 2px; display: block; }
.img-field-row { display: flex; gap: 6px; align-items: center; }

.blog-input {
  width: 100%; padding: 0.5rem 0.7rem;
  border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--bg); color: var(--text-h); font-size: 0.85rem;
  transition: border-color 0.2s; box-sizing: border-box;
}
.blog-input:focus { outline: none; border-color: var(--accent); }
.blog-select { appearance: auto; cursor: pointer; }

.color-input { width: 70px; height: 36px; border: 1px solid var(--border); border-radius: var(--radius); cursor: pointer; padding: 2px; background: var(--bg); }

.blog-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.5rem 1rem; font-size: 0.85rem; font-weight: 550;
  border-radius: var(--radius); cursor: pointer;
  transition: all 0.2s; font-family: inherit; border: 1px solid transparent;
}
.blog-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.blog-btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.blog-btn-primary:hover:not(:disabled) { filter: brightness(1.1); }
.blog-btn-ghost { background: var(--bg-card); color: var(--text); border-color: var(--border); }
.blog-btn-ghost:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); background: var(--accent-bg); }

.checkbox-label { display: flex !important; align-items: center; gap: 0.5rem; cursor: pointer; }
.checkbox-label input[type="checkbox"] { width: 18px; height: 18px; }

.social-list, .welcome-list { display: flex; flex-direction: column; gap: 6px; }
.social-row, .welcome-row { display: flex; gap: 8px; align-items: center; }

/* ===== 底部固定保存栏 ===== */
.save-bar {
  position: fixed;
  bottom: 0;
  left: 240px;  /* 侧边栏宽度 */
  right: 0;
  z-index: 100;
  background: var(--bg-card);
  border-top: 1px solid var(--border);
  padding: 12px 28px;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.06);
}
.save-bar-inner {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
}

.save-msg {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: var(--radius);
  flex: 1;
}
.save-msg.success { background: #dcfce7; color: #166534; }
.save-msg.error { background: #fef2f2; color: #dc2626; }

@media (max-width: 768px) {
  .save-bar { left: 0; padding: 10px 16px; }
  .save-bar-inner { flex-direction: column; gap: 8px; }
  .save-bar-inner .blog-btn { width: 100%; justify-content: center; }
  .form-row-2, .form-row-3 { grid-template-columns: 1fr; }
}
</style>
