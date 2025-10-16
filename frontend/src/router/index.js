import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'
import Home from '../views/Home.vue'
import Accounts from '../views/Accounts.vue'
import Bots from '../views/Bots.vue'
import Mapping from '../views/Mapping.vue'
import Filter from '../views/Filter.vue'
import Logs from '../views/Logs.vue'
import Settings from '../views/Settings.vue'
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
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 1. 检查是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  const isAuthenticated = sessionStorage.getItem('is_authenticated') === 'true'
  
  // 2. 如果需要认证但未登录，跳转到登录页
  if (requiresAuth && !isAuthenticated && to.path !== '/login') {
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
  
  // 4. 检查向导完成状态
  const wizardCompleted = localStorage.getItem('wizard_completed')
  
  // 如果是首次启动且不是向导页面和登录页，跳转到向导
  if (!wizardCompleted && to.path !== '/wizard' && to.path !== '/login') {
    next('/wizard')
  } else if (wizardCompleted && to.path === '/wizard') {
    // 如果已完成向导但访问向导页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router
