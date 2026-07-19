import api from '../utils/request'

// 检查系统是否已初始化
export const getSetupStatus = () => {
  return api.get('/setup/status/')
}

// 测试数据库连接
export const checkDatabase = () => {
  return api.post('/setup/check-db/')
}

// 执行安装
export const install = (data: {
  username: string
  email?: string
  password: string
  site_title: string
  site_description?: string
}) => {
  return api.post('/setup/install/', data)
}
