import { defineStore } from 'pinia'
import api from '../api'

export const useMappingsStore = defineStore('mappings', {
  state: () => ({
    mappings: [],
    loading: false,
    error: null
  }),
  
  getters: {
    /**
     * 根据频道ID获取频道名称
     */
    getChannelNameById: (state) => (channelId) => {
      const mapping = state.mappings.find(m => m.kook_channel_id === channelId)
      return mapping ? mapping.kook_channel_name : channelId
    },
    
    /**
     * 获取所有映射
     */
    allMappings: (state) => state.mappings,
    
    /**
     * 检查是否有映射
     */
    hasMappings: (state) => state.mappings.length > 0
  },
  
  actions: {
    /**
     * 获取所有频道映射
     */
    async fetchMappings() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/api/mappings')
        this.mappings = response.data || []
      } catch (error) {
        console.error('获取频道映射失败:', error)
        this.error = error.message
        this.mappings = []
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 添加新映射
     */
    async addMapping(mappingData) {
      try {
        await api.post('/api/mappings', mappingData)
        await this.fetchMappings()
      } catch (error) {
        console.error('添加映射失败:', error)
        throw error
      }
    },
    
    /**
     * 删除映射
     */
    async deleteMapping(mappingId) {
      try {
        await api.delete(`/api/mappings/${mappingId}`)
        await this.fetchMappings()
      } catch (error) {
        console.error('删除映射失败:', error)
        throw error
      }
    },
    
    /**
     * 更新映射
     */
    async updateMapping(mappingId, mappingData) {
      try {
        await api.put(`/api/mappings/${mappingId}`, mappingData)
        await this.fetchMappings()
      } catch (error) {
        console.error('更新映射失败:', error)
        throw error
      }
    },
    
    /**
     * 清空所有映射
     */
    clearMappings() {
      this.mappings = []
      this.error = null
    }
  }
})
