import api from '../utils/request'

// 获取文章列表
export const getArticles = (params?: any) => {
  return api.get('/blog/articles/', { params })
}

// 获取文章详情
export const getArticleDetail = (id: number) => {
  return api.get(`/blog/articles/${id}/`)
}

// 创建文章
export const createArticle = (data: any) => {
  return api.post('/blog/articles/', data)
}

// 更新文章（PATCH 局部更新，仅提交变更字段）
export const updateArticle = (id: number, data: any) => {
  return api.patch(`/blog/articles/${id}/`, data)
}

// 删除文章
export const deleteArticle = (id: number) => {
  return api.delete(`/blog/articles/${id}/`)
}

// 获取文章归档
export const getArchives = () => {
  return api.get('/blog/articles/archives/')
}

// 获取文章统计
export const getStats = () => {
  return api.get('/blog/articles/stats/')
}

// 获取分类列表
export const getCategories = () => {
  return api.get('/blog/categories/')
}

// 获取标签列表
export const getTags = () => {
  return api.get('/blog/tags/')
}

// 获取文章评论
export const getComments = (articleId: number) => {
  return api.get(`/blog/articles/${articleId}/comments/`)
}

// 创建评论
export const createComment = (data: any) => {
  return api.post(`/blog/articles/${data.article}/comments/`, data)
}

// 获取站点配置
export const getSiteConfig = () => {
  return api.get('/blog/site-config/')
}

// 获取菜单项
export const getMenuItems = () => {
  return api.get('/blog/menu-items/')
}

// 获取留言板
export const getGuestbook = () => {
  return api.get('/blog/guestbook/')
}

// 创建留言
export const createGuestbook = (data: any) => {
  return api.post('/blog/guestbook/', data)
}

// 获取日记列表
export const getDiaries = (params?: any) => {
  return api.get('/blog/diaries/', { params })
}

// 获取关于页面
export const getAbout = () => {
  return api.get('/blog/about/')
}

// ========== 管理员 API ==========

// 获取所有留言（含未审核）
export const getAdminGuestbook = (params?: any) => {
  return api.get('/blog/admin/guestbook/', { params })
}

// 审核/更新留言
export const updateGuestbook = (id: number, data: any) => {
  return api.patch(`/blog/admin/guestbook/${id}/`, data)
}

// 删除留言
export const deleteGuestbook = (id: number) => {
  return api.delete(`/blog/admin/guestbook/${id}/`)
}

// 获取所有评论（含未审核）
export const getAdminComments = (params?: any) => {
  return api.get('/blog/admin/comments/', { params })
}

// 审核/更新评论
export const updateComment = (id: number, data: any) => {
  return api.patch(`/blog/admin/comments/${id}/`, data)
}

// 删除评论
export const deleteComment = (id: number) => {
  return api.delete(`/blog/admin/comments/${id}/`)
}

// ========== 管理员分类 API ==========

// 获取所有分类（含全部层级，用于管理）
export const getAdminCategories = () => {
  return api.get('/blog/admin/categories/')
}

// 创建分类
export const createCategory = (data: any) => {
  return api.post('/blog/admin/categories/', data)
}

// 更新分类
export const updateCategory = (id: number, data: any) => {
  return api.patch(`/blog/admin/categories/${id}/`, data)
}

// 删除分类
export const deleteCategory = (id: number) => {
  return api.delete(`/blog/admin/categories/${id}/`)
}

// ========== 管理员菜单 API ==========

// 获取所有菜单项（含全部层级，用于管理）
export const getAdminMenuItems = () => {
  return api.get('/blog/admin/menu-items/')
}

// 创建菜单项
export const createMenuItem = (data: any) => {
  return api.post('/blog/admin/menu-items/', data)
}

// 更新菜单项
export const updateMenuItem = (id: number, data: any) => {
  return api.patch(`/blog/admin/menu-items/${id}/`, data)
}

// 删除菜单项
export const deleteMenuItem = (id: number) => {
  return api.delete(`/blog/admin/menu-items/${id}/`)
}
