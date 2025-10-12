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

const routes = [
  {
    path: '/wizard',
    name: 'Wizard',
    component: Wizard,
    meta: { title: '配置向导' }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    children: [
      {
        path: '/home',
        name: 'Home',
        component: Home,
        meta: { title: '概览' }
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

// 路由守卫：首次启动跳转到向导
router.beforeEach((to, from, next) => {
  const wizardCompleted = localStorage.getItem('wizard_completed')
  
  // 如果是首次启动且不是向导页面，跳转到向导
  if (!wizardCompleted && to.path !== '/wizard') {
    next('/wizard')
  } else if (wizardCompleted && to.path === '/wizard') {
    // 如果已完成向导但访问向导页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router
