import { defineStore } from 'pinia'
import api from '../api'

export const useAccountsStore = defineStore('accounts', {
  state: () => ({
    accounts: []
  }),
  
  actions: {
    async fetchAccounts() {
      try {
        this.accounts = await api.getAccounts()
      } catch (error) {
        console.error('获取账号列表失败:', error)
      }
    },
    
    async addAccount(accountData) {
      try {
        await api.addAccount(accountData)
        await this.fetchAccounts()
      } catch (error) {
        console.error('添加账号失败:', error)
        throw error
      }
    },
    
    async deleteAccount(accountId) {
      try {
        await api.deleteAccount(accountId)
        await this.fetchAccounts()
      } catch (error) {
        console.error('删除账号失败:', error)
        throw error
      }
    },
    
    async startAccount(accountId) {
      try {
        await api.startAccount(accountId)
        await this.fetchAccounts()
      } catch (error) {
        console.error('启动账号失败:', error)
        throw error
      }
    },
    
    async stopAccount(accountId) {
      try {
        await api.stopAccount(accountId)
        await this.fetchAccounts()
      } catch (error) {
        console.error('停止账号失败:', error)
        throw error
      }
    }
  }
})
