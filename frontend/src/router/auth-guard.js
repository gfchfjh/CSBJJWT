/**
 * 路由守卫 - 认证检查
 */
import api from '@/api'

export async function setupAuthGuard(router) {
  router.beforeEach(async (to, from, next) => {
    // 检查路由是否需要认证
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
    
    if (!requiresAuth) {
      // 不需要认证，直接通过
      return next()
    }
    
    // 检查Token
    const token = localStorage.getItem('auth_token')
    
    if (!token) {
      // 没有Token，跳转到登录页
      return next('/login')
    }
    
    // 检查Token是否记住（30天）
    const tokenExpire = localStorage.getItem('auth_token_expire')
    if (tokenExpire && Date.now() > parseInt(tokenExpire)) {
      // Token已过期
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_token_expire')
      return next('/login')
    }
    
    try {
      // 验证Token
      await api.verifyToken()
      next()
    } catch (error) {
      // Token无效，跳转到登录页
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_token_expire')
      next('/login')
    }
  })
}
