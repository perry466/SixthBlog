import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ArticleList, ArticleDetail, Category, Tag, SiteConfig, MenuItem, PaginatedResponse } from '../types'
import { getArticles, getArticleDetail, getCategories, getTags, getSiteConfig, getMenuItems, getStats, getArchives } from '../api/blog'

export const useBlogStore = defineStore('blog', () => {
  // 状态
  const articles = ref<ArticleList[]>([])
  const currentArticle = ref<ArticleDetail | null>(null)
  const categories = ref<Category[]>([])
  const tags = ref<Tag[]>([])
  const siteConfig = ref<SiteConfig | null>(null)
  const menuItems = ref<MenuItem[]>([])
  const stats = ref<any>(null)
  const archives = ref<any[]>([])
  const loading = ref(false)
  const total = ref(0)

  // 获取文章列表
  const fetchArticles = async (params?: any) => {
    loading.value = true
    try {
      const data = await getArticles(params) as PaginatedResponse<ArticleList>
      console.log('=== 获取文章列表响应 ===', data)
      console.log('results:', data.results)
      console.log('count:', data.count)
      articles.value = data.results
      total.value = data.count
      console.log('articles.value:', articles.value)
    } catch (error) {
      console.error('获取文章列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 获取文章详情
  const fetchArticleDetail = async (id: number) => {
    loading.value = true
    try {
      currentArticle.value = await getArticleDetail(id) as ArticleDetail
    } catch (error) {
      console.error('获取文章详情失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 获取分类列表
  const fetchCategories = async () => {
    try {
      categories.value = await getCategories() as Category[]
    } catch (error) {
      console.error('获取分类列表失败:', error)
    }
  }

  // 获取标签列表
  const fetchTags = async () => {
    try {
      tags.value = await getTags() as Tag[]
    } catch (error) {
      console.error('获取标签列表失败:', error)
    }
  }

  // 获取站点配置
  const fetchSiteConfig = async () => {
    try {
      siteConfig.value = await getSiteConfig() as SiteConfig
    } catch (error) {
      console.error('获取站点配置失败:', error)
    }
  }

  // 获取菜单项
  const fetchMenuItems = async () => {
    try {
      menuItems.value = await getMenuItems() as MenuItem[]
    } catch (error) {
      console.error('获取菜单项失败:', error)
    }
  }

  // 获取统计信息
  const fetchStats = async () => {
    try {
      stats.value = await getStats()
    } catch (error) {
      console.error('获取统计信息失败:', error)
    }
  }

  // 获取归档
  const fetchArchives = async () => {
    try {
      archives.value = await getArchives()
    } catch (error) {
      console.error('获取归档失败:', error)
    }
  }

  return {
    articles,
    currentArticle,
    categories,
    tags,
    siteConfig,
    menuItems,
    stats,
    archives,
    loading,
    total,
    fetchArticles,
    fetchArticleDetail,
    fetchCategories,
    fetchTags,
    fetchSiteConfig,
    fetchMenuItems,
    fetchStats,
    fetchArchives,
  }
})
