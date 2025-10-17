import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'
import Home from '../views/Home.vue'
import Accounts from '../views/Accounts.vue'
import Bots from '../views/Bots.vue'
import Mapping from '../views/Mapping.vue'
import Filter from '../views/Filter.vue'
import Logs from '../views/Logs.vue'
import Settings from '../views/Settings.vue'
import Advanced from '../views/Advanced.vue'
import Wizard from '../views/Wizard.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/wizard',
    name: 'Wizard',
    component: Wizard,
    meta: { title: '配置向导', requiresAuth: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    meta: { requiresAuth: true },
    children: [
      {
        path: '/home',
        name: 'Home',
        component: Home,
        meta: { title: '概览', requiresAuth: true }
      },
      {
        path: '/accounts',
        name: 'Accounts',
        component: Accounts,
        meta: { title: '账号管理' }
      },
      {
        path: '/bots',
        name: 'Bots',
        component: Bots,
        meta: { title: '机器人配置' }
      },
      {
        path: '/mapping',
        name: 'Mapping',
        component: Mapping,
        meta: { title: '频道映射' }
      },
      {
        path: '/filter',
        name: 'Filter',
        component: Filter,
        meta: { title: '过滤规则' }
      },
      {
        path: '/logs',
        name: 'Logs',
        component: Logs,
        meta: { title: '实时日志' }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: Settings,
        meta: { title: '系统设置' }
      },
      {
        path: '/advanced',
        name: 'Advanced',
        component: Advanced,
        meta: { title: '高级功能' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 检查是否需要显示向导
async function checkNeedsWizard() {
  try {
    // 检查是否有账号和Bot配置
    const [accountsRes, botsRes] = await Promise.all([
      fetch('http://localhost:9527/api/accounts'),
      fetch('http://localhost:9527/api/bots')
    ])
    
    if (!accountsRes.ok || !botsRes.ok) {
      return true // API错误，显示向导
    }
    
    const accounts = await accountsRes.json()
    const bots = await botsRes.json()
    
    // 如果没有账号或没有Bot，需要向导
    return accounts.length === 0 || bots.length === 0
  } catch (error) {
    console.error('检查向导状态失败:', error)
    // 发生错误时，检查本地存储的标记
    return localStorage.getItem('wizard_completed') !== 'true'
  }
}

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 1. 检查是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  const isAuthenticated = sessionStorage.getItem('is_authenticated') === 'true'
  
  // 2. 如果需要认证但未登录，跳转到登录页
  if (requiresAuth && !isAuthenticated && to.path !== '/login' && to.path !== '/wizard') {
    // 检查密码保护是否启用
    try {
      const response = await fetch('http://localhost:9527/api/system/config/require_password')
      const data = await response.json()
      
      if (data.require_password) {
        // 密码保护已启用，跳转到登录页
        next('/login')
        return
      }
      // 密码保护未启用，标记为已认证并继续
      sessionStorage.setItem('is_authenticated', 'true')
    } catch (error) {
      console.error('检查认证状态失败:', error)
      // 网络错误，假设未启用密码保护
      sessionStorage.setItem('is_authenticated', 'true')
    }
  }
  
  // 3. 如果已登录访问登录页，跳转到首页
  if (isAuthenticated && to.path === '/login') {
    next('/')
    return
  }
  
  // 4. 智能检查是否需要向导（检查实际数据而非仅标记）
  if (to.path !== '/wizard' && to.path !== '/login') {
    const needsWizard = await checkNeedsWizard()
    
    if (needsWizard) {
      console.log('检测到首次启动或配置不完整，跳转到配置向导')
      next('/wizard')
      return
    }
  }
  
  // 5. 如果配置完整但访问向导页，允许进入（用户可能想重新配置）
  // 不强制跳转，让用户可以手动进入向导页
  
  next()
})

export default router
