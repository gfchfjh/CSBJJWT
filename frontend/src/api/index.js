import axios from 'axios'

const API_BASE_URL = 'http://localhost:9527'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API错误:', error)
    return Promise.reject(error)
  }
)

export default {
  // 系统
  getSystemStatus: () => api.get('/api/system/status'),
  startService: () => api.post('/api/system/start'),
  stopService: () => api.post('/api/system/stop'),
  getConfig: () => api.get('/api/system/config'),
  
  // 账号
  getAccounts: () => api.get('/api/accounts/'),
  addAccount: (data) => api.post('/api/accounts/', data),
  deleteAccount: (id) => api.delete(`/api/accounts/${id}`),
  startAccount: (id) => api.post(`/api/accounts/${id}/start`),
  stopAccount: (id) => api.post(`/api/accounts/${id}/stop`),
  getServers: (accountId) => api.get(`/api/accounts/${accountId}/servers`),
  getChannels: (accountId, serverId) => api.get(`/api/accounts/${accountId}/servers/${serverId}/channels`),
  getCaptchaStatus: (accountId) => api.get(`/api/accounts/${accountId}/captcha`),
  submitCaptcha: (accountId, code) => api.post(`/api/accounts/${accountId}/captcha`, { code }),
  
  // Bot配置
  getBotConfigs: (platform) => api.get('/api/bots/', { params: { platform } }),
  addBotConfig: (data) => api.post('/api/bots/', data),
  deleteBotConfig: (id) => api.delete(`/api/bots/${id}`),
  testBotConfig: (id) => api.post(`/api/bots/${id}/test`),
  
  // 频道映射
  getMappings: (kookChannelId) => api.get('/api/mappings/', { params: { kook_channel_id: kookChannelId } }),
  addMapping: (data) => api.post('/api/mappings/', data),
  deleteMapping: (id) => api.delete(`/api/mappings/${id}`),
  
  // 日志
  getLogs: (limit, status) => api.get('/api/logs/', { params: { limit, status } }),
  getStats: () => api.get('/api/logs/stats'),
  
  // 过滤规则
  getFilterRules: () => api.get('/api/system/filter-rules'),
  saveFilterRules: (data) => api.post('/api/system/filter-rules', data),
  
  // 智能映射
  suggestMappings: (data) => api.post('/api/smart-mapping/suggest', data),
  applySmartMappings: (suggestions) => api.post('/api/smart-mapping/apply', suggestions),
  previewSmartMapping: (accountId) => api.get(`/api/smart-mapping/preview/${accountId}`),
  
  // 备份恢复
  backupConfig: () => api.post('/api/backup/create'),
  restoreConfig: (data) => api.post('/api/backup/restore', data),
  listBackups: () => api.get('/api/backup/list'),
  
  // 认证与密码
  checkPasswordExists: () => api.get('/api/auth/password-exists'),
  setPassword: (data) => api.post('/api/auth/set-password', data),
  verifyPassword: (data) => api.post('/api/auth/verify-password', data),
  changePassword: (data) => api.post('/api/auth/change-password', data),
  resetPassword: () => api.post('/api/auth/reset-password')
}
