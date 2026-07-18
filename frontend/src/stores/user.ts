import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '../types'
import { login as loginApi, logout as logoutApi, register as registerApi, getCurrentUser } from '../api/user'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const isLoggedIn = ref(false)
  const loading = ref(false)

  // 登录
  const login = async (username: string, password: string) => {
    loading.value = true
    try {
      const data = await loginApi({ username, password }) as any
      user.value = data.user
      isLoggedIn.value = true
      return { success: true, message: data.message }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.error || '登录失败' }
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      await logoutApi()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      user.value = null
      isLoggedIn.value = false
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_logged_in')
    }
  }

  // 注册
  const register = async (username: string, password: string, email?: string) => {
    loading.value = true
    try {
      const data = await registerApi({ username, password, email }) as any
      user.value = data.user
      isLoggedIn.value = true
      return { success: true, message: data.message }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.error || '注册失败' }
    } finally {
      loading.value = false
    }
  }

  // 获取当前用户
  const fetchCurrentUser = async () => {
    try {
      user.value = await getCurrentUser() as User
      isLoggedIn.value = true
      // 持久化登录状态到 localStorage
      localStorage.setItem('auth_user', JSON.stringify(user.value))
      localStorage.setItem('auth_logged_in', 'true')
    } catch (error) {
      user.value = null
      isLoggedIn.value = false
      localStorage.removeItem('auth_user')
      localStorage.removeItem('auth_logged_in')
    }
  }

  // 从 localStorage 恢复用户信息（仅用于快速显示用户名，不标记已登录）
  const restoreFromStorage = () => {
    const loggedIn = localStorage.getItem('auth_logged_in')
    if (loggedIn === 'true') {
      const saved = localStorage.getItem('auth_user')
      if (saved) {
        try {
          user.value = JSON.parse(saved)
          // 注意：不设置 isLoggedIn，需要 fetchCurrentUser 验证后才算已登录
        } catch {
          localStorage.removeItem('auth_user')
          localStorage.removeItem('auth_logged_in')
        }
      }
    }
  }

  return {
    user,
    isLoggedIn,
    loading,
    login,
    logout,
    register,
    fetchCurrentUser,
    restoreFromStorage,
  }
})
