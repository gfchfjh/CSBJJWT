import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'
import Home from '../views/Home.vue'
import HomeEnhanced from '../views/HomeEnhanced.vue'  // ✅ P1-2新增：增强版主界面
import Accounts from '../views/Accounts.vue'
import Bots from '../views/Bots.vue'
import Mapping from '../views/Mapping.vue'
import MappingVisual from '../views/MappingVisual.vue'  // ✅ P0-4新增：可视化映射编辑器
import Filter from '../views/Filter.vue'
import Logs from '../views/Logs.vue'
import Settings from '../views/Settings.vue'
import Advanced from '../views/Advanced.vue'
import Selectors from '../views/Selectors.vue'
import Help from '../views/Help.vue'
import Wizard from '../views/Wizard.vue'
import WizardQuick3Steps from '../views/WizardQuick3Steps.vue'
import WizardUltimate3Steps from '../views/WizardUltimate3Steps.vue'
import WizardUnified from '../views/WizardUnified.vue'  // ✅ v9.0.0新增：统一向导
import WizardSimple3Steps from '../views/WizardSimple3Steps.vue'  // ✅ P0-1新增：真正的3步向导
import QuickSetup from '../views/QuickSetup.vue'
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
    component: WizardSimple3Steps,  // ✅ P0-1优化: 使用真正的3步向导（傻瓜式）
    meta: { title: '配置向导', requiresAuth: true }
  },
  {
    path: '/wizard-advanced',
    name: 'WizardAdvanced',
    component: WizardUnified,  // 保留高级向导作为备选
    meta: { title: '高级配置向导', requiresAuth: true }
  },
  {
    path: '/wizard-ultimate',
    name: 'WizardUltimate',
    component: WizardUltimate3Steps,  // 保留终极向导作为备选
    meta: { title: '快速配置向导（3步）', requiresAuth: true }
  },
  {
    path: '/wizard-simple',
    name: 'WizardSimple',
    component: WizardQuick3Steps,  // 备用简化向导
    meta: { title: '简化配置向导', requiresAuth: true }
  },
  {
    path: '/wizard-full',
    name: 'WizardFull',
    component: Wizard,  // 保留完整版向导
    meta: { title: '完整配置向导（6步）', requiresAuth: true }
  },
  {
    path: '/quick-setup',
    name: 'QuickSetup',
    component: QuickSetup,
    meta: { title: '快速配置', requiresAuth: true }
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
        component: HomeEnhanced,  // ✅ P1-2优化: 使用增强版主界面
        meta: { title: '概览', requiresAuth: true }
      },
      {
        path: '/home-simple',
        name: 'HomeSimple',
        component: Home,  // 保留简单版作为备选
        meta: { title: '概览（简单）', requiresAuth: true }
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
        component: MappingVisual,  // ✅ P0-4优化: 使用可视化映射编辑器
        meta: { title: '频道映射（可视化）' }
      },
      {
        path: '/mapping-table',
        name: 'MappingTable',
        component: Mapping,  // 保留表格式映射作为备选
        meta: { title: '频道映射（表格）' }
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
      },
      {
        path: '/selectors',
        name: 'Selectors',
        component: Selectors,
        meta: { title: '选择器配置' }
      },
      {
        path: '/help',
        name: 'Help',
        component: Help,
        meta: { title: '帮助中心' }
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
  
  // 2. 如果路由不需要认证，直接通过
  if (!requiresAuth) {
    next()
    return
  }
  
  // 3. 检查是否已设置密码
  try {
    const response = await fetch('http://localhost:9527/auth/status')
    const data = await response.json()
    
    if (!data.password_set) {
      // 未设置密码，首次使用，跳转到登录页进行设置
      if (to.path !== '/login') {
        next('/login')
        return
      }
      next()
      return
    }
  } catch (error) {
    console.error('检查密码状态失败:', error)
  }
  
  // 4. 检查Token
  const token = localStorage.getItem('auth_token')
  
  if (!token && to.path !== '/login') {
    // 没有Token，跳转到登录页
    next('/login')
    return
  }
  
  // 5. 验证Token（如果有）
  if (token) {
    try {
      const tokenExpire = localStorage.getItem('auth_token_expire')
      if (tokenExpire && Date.now() > parseInt(tokenExpire)) {
        // Token已过期
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_token_expire')
        if (to.path !== '/login') {
          next('/login')
          return
        }
      }
      
      // Token验证通过，如果在登录页则跳转到首页
      if (to.path === '/login') {
        next('/')
        return
      }
    } catch (error) {
      console.error('验证Token失败:', error)
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_token_expire')
      if (to.path !== '/login') {
        next('/login')
        return
      }
    }
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
