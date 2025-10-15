<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>KOOK转发系统</h2>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="menu"
        router
        :unique-opened="true"
      >
        <el-menu-item index="/home">
          <el-icon><House /></el-icon>
          <span>概览</span>
        </el-menu-item>
        
        <el-menu-item index="/accounts">
          <el-icon><User /></el-icon>
          <span>账号管理</span>
        </el-menu-item>
        
        <el-menu-item index="/bots">
          <el-icon><Robot /></el-icon>
          <span>机器人配置</span>
        </el-menu-item>
        
        <el-menu-item index="/mapping">
          <el-icon><Connection /></el-icon>
          <span>频道映射</span>
        </el-menu-item>
        
        <el-menu-item index="/filter">
          <el-icon><Filter /></el-icon>
          <span>过滤规则</span>
        </el-menu-item>
        
        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <span>实时日志</span>
        </el-menu-item>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <h3>{{ $route.meta.title || '概览' }}</h3>
        </div>
        
        <div class="header-right">
          <el-tag :type="statusType" effect="dark">
            {{ statusText }}
          </el-tag>
          
          <el-button
            :type="serviceRunning ? 'warning' : 'success'"
            size="small"
            @click="toggleService"
          >
            {{ serviceRunning ? '停止服务' : '启动服务' }}
          </el-button>
          
          <el-button type="info" size="small" circle>
            <el-icon><QuestionFilled /></el-icon>
          </el-button>
        </div>
      </el-header>
      
      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useSystemStore } from '../store/system'
import { ElMessage } from 'element-plus'

const route = useRoute()
const systemStore = useSystemStore()

const activeMenu = computed(() => route.path)

const serviceRunning = computed(() => systemStore.status.service_running)
const redisConnected = computed(() => systemStore.status.redis_connected)

const statusType = computed(() => {
  if (serviceRunning.value && redisConnected.value) return 'success'
  if (serviceRunning.value) return 'warning'
  return 'danger'
})

const statusText = computed(() => {
  if (serviceRunning.value && redisConnected.value) return '运行中'
  if (serviceRunning.value) return 'Redis未连接'
  return '已停止'
})

let statusInterval = null

const toggleService = async () => {
  try {
    if (serviceRunning.value) {
      await systemStore.stopService()
      ElMessage.success('服务已停止')
    } else {
      await systemStore.startService()
      ElMessage.success('服务已启动')
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  }
}

onMounted(() => {
  // 定期刷新状态
  systemStore.fetchSystemStatus()
  statusInterval = setInterval(() => {
    systemStore.fetchSystemStatus()
  }, 5000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #545c64;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #434a50;
}

.logo h2 {
  font-size: 18px;
  color: #fff;
  margin: 0;
}

.menu {
  border-right: none;
  background-color: #545c64;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.main-content {
  background-color: #f5f5f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
