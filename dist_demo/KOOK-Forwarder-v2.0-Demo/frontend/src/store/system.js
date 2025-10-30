import { defineStore } from 'pinia'
import api from '../api'

export const useSystemStore = defineStore('system', {
  state: () => ({
    status: {
      service_running: false,
      redis_connected: false,
      queue_size: 0,
      active_scrapers: 0
    },
    config: null
  }),
  
  actions: {
    async fetchSystemStatus() {
      try {
        this.status = await api.getSystemStatus()
      } catch (error) {
        console.error('获取系统状态失败:', error)
      }
    },
    
    async fetchConfig() {
      try {
        this.config = await api.getConfig()
      } catch (error) {
        console.error('获取配置失败:', error)
      }
    },
    
    async startService() {
      try {
        await api.startService()
        await this.fetchSystemStatus()
      } catch (error) {
        console.error('启动服务失败:', error)
        throw error
      }
    },
    
    async stopService() {
      try {
        await api.stopService()
        await this.fetchSystemStatus()
      } catch (error) {
        console.error('停止服务失败:', error)
        throw error
      }
    }
  }
})
