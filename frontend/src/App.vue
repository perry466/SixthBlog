<template>
  <div :style="appBackgroundStyle">
    <SplashScreen
      v-if="showSplash"
      :text="siteConfig?.splash_animation_text"
      :bg="siteConfig?.splash_animation_bg"
      :theme="siteConfig?.splash_animation_theme"
      @finished="showSplash = false"
    />
    <MainLayout />
    <DesktopPet />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import MainLayout from './layouts/MainLayout.vue'
import SplashScreen from './components/SplashScreen.vue'
import DesktopPet from './components/DesktopPet.vue'
import { useBlogStore } from './stores/blog'

const blogStore = useBlogStore()

// 开屏动画仅在首次访问首页时展示，同一会话内不再重复
const hasShownSplash = sessionStorage.getItem('splash_shown')
const isHomePath = window.location.pathname === '/' || window.location.pathname === '/home'
const showSplash = ref(!hasShownSplash && isHomePath)

const siteConfig = computed(() => blogStore.siteConfig)

// 标记已展示
if (showSplash.value) {
  sessionStorage.setItem('splash_shown', '1')
}

const appBackgroundStyle = computed(() => {
  if (siteConfig.value?.blog_background) {
    return {
      backgroundImage: `url(${siteConfig.value.blog_background})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed',
    }
  }
  return {}
})

// 动态设置 favicon 和标题
watch(siteConfig, (config) => {
  if (config) {
    // 设置标题
    document.title = config.site_title || 'My Blog'

    // 设置 favicon
    if (config.site_favicon) {
      let link = document.querySelector("link[rel*='icon']") as HTMLLinkElement
      if (!link) {
        link = document.createElement('link')
        link.rel = 'icon'
        document.head.appendChild(link)
      }
      link.href = config.site_favicon
    }

    // 设置 meta description
    let metaDesc = document.querySelector('meta[name="description"]')
    if (!metaDesc) {
      metaDesc = document.createElement('meta')
      metaDesc.setAttribute('name', 'description')
      document.head.appendChild(metaDesc)
    }
    metaDesc.setAttribute('content', config.site_description || '')
  }
}, { immediate: true })

onMounted(async () => {
  await blogStore.fetchSiteConfig()
})
</script>
