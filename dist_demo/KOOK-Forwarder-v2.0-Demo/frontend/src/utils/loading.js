/**
 * 加载状态管理工具
 */
import { ElLoading } from 'element-plus'

/**
 * 创建加载助手
 * @returns {Object} 加载助手对象
 */
export function createLoadingHelper() {
  let loadingInstance = null
  
  return {
    /**
     * 显示加载提示
     * @param {string} text - 加载文本
     */
    show(text = '加载中...') {
      if (loadingInstance) {
        return
      }
      
      loadingInstance = ElLoading.service({
        lock: true,
        text,
        background: 'rgba(0, 0, 0, 0.7)'
      })
    },
    
    /**
     * 隐藏加载提示
     */
    hide() {
      if (loadingInstance) {
        loadingInstance.close()
        loadingInstance = null
      }
    },
    
    /**
     * 包装异步操作，自动显示/隐藏加载
     * @param {Promise} promise - 异步操作
     * @param {string} text - 加载文本
     * @returns {Promise} 原始Promise结果
     */
    async wrap(promise, text = '加载中...') {
      this.show(text)
      try {
        const result = await promise
        return result
      } finally {
        this.hide()
      }
    }
  }
}

/**
 * 全局加载管理器
 */
class GlobalLoadingManager {
  constructor() {
    this.loadingCount = 0
    this.loadingInstance = null
  }
  
  /**
   * 显示加载
   * @param {string} text - 加载文本
   */
  show(text = '加载中...') {
    this.loadingCount++
    
    if (!this.loadingInstance) {
      this.loadingInstance = ElLoading.service({
        lock: true,
        text,
        background: 'rgba(0, 0, 0, 0.7)'
      })
    }
  }
  
  /**
   * 隐藏加载
   */
  hide() {
    this.loadingCount = Math.max(0, this.loadingCount - 1)
    
    if (this.loadingCount === 0 && this.loadingInstance) {
      this.loadingInstance.close()
      this.loadingInstance = null
    }
  }
  
  /**
   * 强制隐藏所有加载
   */
  hideAll() {
    this.loadingCount = 0
    if (this.loadingInstance) {
      this.loadingInstance.close()
      this.loadingInstance = null
    }
  }
}

export const globalLoading = new GlobalLoadingManager()
