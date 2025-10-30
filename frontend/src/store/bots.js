import { defineStore } from 'pinia'

export const useBotsStore = defineStore('bots', {
  state: () => ({
    bots: [],
    loading: false
  }),
  
  actions: {
    async fetchBots() {
      this.loading = true
      try {
        // API调用逻辑
        const response = await fetch('/api/bots')
        if (response.ok) {
          this.bots = await response.json()
        }
      } catch (error) {
        console.error('Failed to fetch bots:', error)
      } finally {
        this.loading = false
      }
    }
  }
})
