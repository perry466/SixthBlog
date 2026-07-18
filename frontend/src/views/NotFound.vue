<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="not-found-code">404</div>
      <h1 class="not-found-title">页面未找到</h1>
      <p class="not-found-desc">你访问的页面不存在或已被移除。</p>
      <div class="not-found-actions">
        <router-link to="/home" class="blog-btn blog-btn-primary">返回首页</router-link>
        <router-link to="/articles" class="blog-btn blog-btn-soft">浏览文章</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.not-found-content {
  text-align: center;
  max-width: 480px;
}

.not-found-code {
  font-size: 8rem;
  font-weight: 800;
  line-height: 1;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  letter-spacing: -0.04em;
}

.not-found-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-h);
  margin: 0 0 0.5rem;
}

.not-found-desc {
  font-size: 0.95rem;
  color: var(--text-muted);
  margin: 0 0 2rem;
  line-height: 1.6;
}

.not-found-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
}
</style>
