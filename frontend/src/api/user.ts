import api from '../utils/request'

// 用户登录
export const login = (data: { username: string; password: string }) => {
  return api.post('/users/auth/login/', data)
}

// 用户登出
export const logout = () => {
  return api.post('/users/auth/logout/')
}

// 用户注册
export const register = (data: { username: string; password: string; email?: string }) => {
  return api.post('/users/auth/register/', data)
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return api.get('/users/auth/user/')
}

// 获取用户列表（管理员）
export const getUsers = () => {
  return api.get('/users/admin/users/')
}

// 创建用户（管理员）
export const createUser = (data: {
  username: string
  email?: string
  password: string
  is_staff?: boolean
  role?: string
}) => {
  return api.post('/users/admin/users/create/', data)
}

// 获取用户详情（管理员）
export const getUserDetail = (id: number) => {
  return api.get(`/users/admin/users/${id}/`)
}

// 更新用户（管理员）
export const updateUser = (id: number, data: {
  username?: string
  email?: string
  is_staff?: boolean
  role?: string
  password?: string
}) => {
  return api.put(`/users/admin/users/${id}/`, data)
}

// 删除用户（管理员）
export const deleteUser = (id: number) => {
  return api.delete(`/users/admin/users/${id}/`)
}

// 更新个人资料
export const updateProfile = (data: {
  avatar?: File | null
  bio?: string
  email?: string
}) => {
  const formData = new FormData()
  if (data.avatar) formData.append('avatar', data.avatar)
  if (data.bio !== undefined) formData.append('bio', data.bio)
  if (data.email !== undefined) formData.append('email', data.email)
  return api.put('/users/auth/profile/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 上传图片
export const uploadImage = (file: File) => {
  const formData = new FormData()
  formData.append('image', file)
  return api.post('/blog/upload-image/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
