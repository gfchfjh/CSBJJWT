/**
 * 路由守卫 - 认证检查
 * ✅ P0-8优化：添加主密码检查
 */
import api from '@/api'

export async function setupAuthGuard(router) {
  router.beforeEach(async (to, from, next) => {
    // ✅ P0-8优化：优先检查主密码
    // 如果不是解锁页面，检查是否需要解锁
    if (to.path !== '/unlock') {
      try {
        const response = await api.get('/api/auth/master-password-status')
        
        // 如果设置了主密码，检查是否已解锁
        if (response.password_set) {
          const masterToken = localStorage.getItem('master_token')
          
          if (!masterToken) {
            // 没有解锁Token，跳转到解锁页
            return next('/unlock')
          }
          
          // 验证Token是否有效（通过尝试访问API）
          try {
            await api.get('/health')
          } catch (error) {
            if (error.response?.data?.require_master_password) {
              // Token无效，需要重新解锁
              localStorage.removeItem('master_token')
              return next('/unlock')
            }
          }
        }
      } catch (error) {
        console.error('检查主密码状态失败:', error)
        // 如果API不可用，允许继续（避免卡住）
      }
    }
    
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
