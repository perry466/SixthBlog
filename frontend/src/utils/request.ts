import axios from 'axios'

// 读取 CSRF token（Django 在 cookie 中设置）
function getCSRFToken(): string {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : ''
}

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // FormData 需要浏览器自动设置 Content-Type（含 boundary）
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    // 非 GET 请求自动附加 CSRF token
    const method = (config.method || '').toLowerCase()
    if (method !== 'get' && method !== 'head' && method !== 'options') {
      const csrf = getCSRFToken()
      if (csrf) {
        config.headers['X-CSRFToken'] = csrf
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
