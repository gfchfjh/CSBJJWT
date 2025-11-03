<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="logo">
        <img src="/icon.png" alt="Logo" class="logo-image">
        <span v-if="!sidebarCollapsed" class="logo-text">KOOK转发</span>
      </div>
      
      <el-menu
        :default-active="currentRoute"
        class="sidebar-menu"
        :collapse="sidebarCollapsed"
        router
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <template #title>概览</template>
        </el-menu-item>
        
        <el-menu-item index="/accounts">
          <el-icon><User /></el-icon>
          <template #title>账号管理</template>
        </el-menu-item>
        
        <el-menu-item index="/bots">
          <el-icon><Robot /></el-icon>
          <template #title>Bot配置</template>
        </el-menu-item>
        
        <el-menu-item index="/mapping">
          <el-icon><Connection /></el-icon>
          <template #title>频道映射</template>
        </el-menu-item>
        
        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <template #title>实时日志</template>
        </el-menu-item>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
        
        <el-menu-item index="/help">
          <el-icon><QuestionFilled /></el-icon>
          <template #title>帮助中心</template>
        </el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <el-button 
          :icon="sidebarCollapsed ? Expand : Fold" 
          circle
          size="small"
          @click="toggleSidebar"
        />
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部栏 -->
      <header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="crumb in breadcrumbs" :key="crumb.path">
              {{ crumb.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 系统状态指示器 -->
          <div class="status-indicator" :class="systemStatus">
            <span class="status-dot"></span>
            <span class="status-text">{{ statusText }}</span>
          </div>
          
          <!-- 通知 -->
          <el-badge :value="notificationCount" :hidden="notificationCount === 0">
            <el-button :icon="Bell" circle @click="showNotifications" />
          </el-badge>
          
          <!-- 用户菜单 -->
          <el-dropdown>
            <el-avatar :size="32">
              <el-icon><User /></el-icon>
            </el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goToSettings">
                  <el-icon><Setting /></el-icon>
                  设置
                </el-dropdown-item>
                <el-dropdown-item @click="showAbout">
                  <el-icon><InfoFilled /></el-icon>
                  关于
                </el-dropdown-item>
                <el-dropdown-item divided @click="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <!-- 路由视图 -->
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  HomeFilled,
  User,
  Tools,
  Connection,
  Document,
  Setting,
  QuestionFilled,
  Bell,
  InfoFilled,
  SwitchButton,
  Expand,
  Fold
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

// 侧边栏状态
const sidebarCollapsed = ref(false)

// 当前路由
const currentRoute = computed(() => route.path)

// 面包屑
const breadcrumbs = computed(() => {
  const routeMap = {
    '/': { name: '概览' },
    '/accounts': { name: '账号管理' },
    '/bots': { name: 'Bot配置' },
    '/mapping': { name: '频道映射' },
    '/logs': { name: '实时日志' },
    '/settings': { name: '系统设置' },
    '/help': { name: '帮助中心' }
  }
  
  const current = routeMap[route.path]
  return current ? [{ name: current.name, path: route.path }] : []
})

// 系统状态
const systemStatus = ref('running')  // running/stopped/error
const notificationCount = ref(0)

// 状态文本
const statusText = computed(() => {
  const statusMap = {
    running: '运行中',
    stopped: '已停止',
    error: '异常'
  }
  return statusMap[systemStatus.value] || '未知'
})

// 定时器
let statusInterval = null

// 方法：切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value)
}

// 方法：显示通知
const showNotifications = () => {
  router.push('/notifications')
}

// 方法：跳转设置
const goToSettings = () => {
  router.push('/settings')
}

// 方法：显示关于
const showAbout = () => {
  // 显示关于对话框
  alert('KOOK消息转发系统 v1.0.0')
}

// 方法：退出
const logout = () => {
  if (confirm('确定要退出吗？')) {
    localStorage.clear()
    router.push('/login')
  }
}

// 方法：获取系统状态
const fetchSystemStatus = async () => {
  try {
    const response = await axios.get('/api/system/stats')
    systemStatus.value = response.data.status || 'running'
  } catch (error) {
    systemStatus.value = 'error'
  }
}

// 生命周期：挂载
onMounted(() => {
  // 恢复侧边栏状态
  const savedState = localStorage.getItem('sidebarCollapsed')
  if (savedState !== null) {
    sidebarCollapsed.value = savedState === 'true'
  }
  
  // 获取系统状态
  fetchSystemStatus()
  
  // 定期刷新状态（10秒）
  statusInterval = setInterval(fetchSystemStatus, 10000)
})

// 生命周期：卸载
onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

/* 侧边栏 */
.sidebar {
  width: 240px;
  background: #001529;
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar.collapsed {
  width: 64px;
}

.logo {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-image {
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.sidebar-footer {
  padding: 16px;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部栏 */
.header {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 状态指示器 */
.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 16px;
  background: #f0f0f0;
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
}

.status-indicator.running .status-dot {
  background: #52c41a;
  box-shadow: 0 0 4px #52c41a;
}

.status-indicator.stopped .status-dot {
  background: #d9d9d9;
}

.status-indicator.error .status-dot {
  background: #ff4d4f;
  box-shadow: 0 0 4px #ff4d4f;
}

/* 内容区 */
.content-wrapper {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 滚动条样式 */
.content-wrapper::-webkit-scrollbar {
  width: 8px;
}

.content-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.content-wrapper::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.content-wrapper::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>
