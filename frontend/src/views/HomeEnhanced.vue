<template>
  <div class="home-view">
    <!-- ✅ P0-4优化：顶部快捷操作栏 -->
    <div class="action-bar">
      <div class="status-indicator">
        <el-tag :type="serviceStatus === 'running' ? 'success' : 'danger'" size="large" effect="dark">
          {{ serviceStatus === 'running' ? '🟢 运行中' : '🔴 已停止' }}
        </el-tag>
        <span class="uptime">运行时长: {{ uptime }}</span>
      </div>
      
      <div class="quick-actions">
        <el-button
          v-if="serviceStatus !== 'running'"
          type="success"
          size="large"
          @click="startService"
          :loading="starting"
        >
          <el-icon><VideoPlay /></el-icon>
          启动服务
        </el-button>
        <el-button
          v-else
          type="danger"
          size="large"
          @click="stopService"
          :loading="stopping"
        >
          <el-icon><VideoPause /></el-icon>
          停止服务
        </el-button>
        
        <el-button size="large" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>
    
    <!-- ✅ P0-4优化：实时统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409EFF"><ChatDotRound /></el-icon>
            <div class="stat-data">
              <div class="stat-value">{{ stats.total.toLocaleString() }}</div>
              <div class="stat-label">今日转发</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67C23A"><CircleCheck /></el-icon>
            <div class="stat-data">
              <div class="stat-value">{{ stats.success_rate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#E6A23C"><Timer /></el-icon>
            <div class="stat-data">
              <div class="stat-value">{{ stats.avg_latency.toFixed(1) }}s</div>
              <div class="stat-label">平均延迟</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#F56C6C"><CircleClose /></el-icon>
            <div class="stat-data">
              <div class="stat-value">{{ stats.failed }}</div>
              <div class="stat-label">
                失败消息
                <el-link type="primary" @click="$router.push('/logs?status=failed')" :underline="false" style="margin-left: 5px;">
                  查看
                </el-link>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- ✅ P0-4优化：实时监控图表 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📈 实时转发趋势（最近1小时）</span>
              <el-radio-group v-model="chartTimeRange" size="small" @change="loadChartData">
                <el-radio-button label="1h">1小时</el-radio-button>
                <el-radio-button label="6h">6小时</el-radio-button>
                <el-radio-button label="24h">24小时</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="messageChart" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>📊 平台分布</span>
          </template>
          <div ref="platformChart" class="chart-container-small"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- ✅ P0-4优化：快捷操作面板 -->
    <el-card shadow="hover" class="quick-panel">
      <template #header>
        <span>⚡ 快捷操作</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="quick-action" @click="$router.push('/accounts')">
            <el-icon class="action-icon" color="#409EFF"><User /></el-icon>
            <div class="action-text">
              <div class="action-title">管理账号</div>
              <div class="action-desc">{{ accountCount }} 个账号</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="quick-action" @click="$router.push('/bots')">
            <el-icon class="action-icon" color="#67C23A"><Robot /></el-icon>
            <div class="action-text">
              <div class="action-title">配置机器人</div>
              <div class="action-desc">{{ botCount }} 个Bot</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="quick-action" @click="$router.push('/mapping')">
            <el-icon class="action-icon" color="#E6A23C"><Connection /></el-icon>
            <div class="action-text">
              <div class="action-title">设置映射</div>
              <div class="action-desc">{{ mappingCount }} 条映射</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="6">
          <div class="quick-action" @click="$router.push('/logs')">
            <el-icon class="action-icon" color="#909399"><Document /></el-icon>
            <div class="action-text">
              <div class="action-title">查看日志</div>
              <div class="action-desc">实时监控</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- ✅ P0-4优化：空状态引导 -->
    <el-card v-if="showEmptyState" shadow="hover" class="empty-state">
      <el-empty description="欢迎使用KOOK消息转发系统">
        <template #image>
          <el-icon style="font-size: 100px;" color="#409EFF"><ChatDotRound /></el-icon>
        </template>
        <template #description>
          <div class="empty-description">
            <h2>👋 欢迎使用！</h2>
            <p>请按以下步骤开始：</p>
            <ol class="setup-steps">
              <li>
                <el-icon><User /></el-icon>
                添加KOOK账号
              </li>
              <li>
                <el-icon><Robot /></el-icon>
                配置Bot（Discord/Telegram/飞书）
              </li>
              <li>
                <el-icon><Connection /></el-icon>
                设置频道映射
              </li>
              <li>
                <el-icon><VideoPlay /></el-icon>
                启动消息转发服务
              </li>
            </ol>
          </div>
        </template>
        <el-button type="primary" size="large" @click="$router.push('/wizard')">
          🚀 开始配置向导
        </el-button>
        <el-button size="large" @click="showEmptyState = false">
          跳过，手动配置
        </el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  VideoPlay,
  VideoPause,
  Refresh,
  ChatDotRound,
  CircleCheck,
  Timer,
  CircleClose,
  User,
  Robot,
  Connection,
  Document
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/api'

// 状态
const serviceStatus = ref('stopped')
const uptime = ref('--')
const starting = ref(false)
const stopping = ref(false)

// 统计数据
const stats = ref({
  total: 0,
  success: 0,
  failed: 0,
  success_rate: 0,
  avg_latency: 0
})

// 快捷信息
const accountCount = ref(0)
const botCount = ref(0)
const mappingCount = ref(0)

// 空状态
const showEmptyState = ref(false)

// 图表
const messageChart = ref(null)
const platformChart = ref(null)
const chartTimeRange = ref('1h')
let messageChartInstance = null
let platformChartInstance = null

// 定时刷新
let refreshTimer = null

// 启动服务
const startService = async () => {
  try {
    starting.value = true
    await api.startService()
    ElMessage.success('服务已启动')
    await loadSystemStatus()
  } catch (error) {
    ElMessage.error('启动失败：' + (error.response?.data?.detail || error.message))
  } finally {
    starting.value = false
  }
}

// 停止服务
const stopService = async () => {
  try {
    stopping.value = true
    await api.stopService()
    ElMessage.success('服务已停止')
    await loadSystemStatus()
  } catch (error) {
    ElMessage.error('停止失败：' + (error.response?.data?.detail || error.message))
  } finally {
    stopping.value = false
  }
}

// 加载系统状态
const loadSystemStatus = async () => {
  try {
    const status = await api.getSystemStatus()
    serviceStatus.value = status.service_running ? 'running' : 'stopped'
    
    // 计算运行时长（示例）
    if (status.service_running) {
      uptime.value = '3小时25分钟'  // TODO: 从后端获取真实运行时长
    } else {
      uptime.value = '--'
    }
  } catch (error) {
    console.error('加载系统状态失败:', error)
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const data = await api.getStats()
    stats.value = {
      total: data.total || 0,
      success: data.success || 0,
      failed: data.failed || 0,
      success_rate: data.success_rate || 0,
      avg_latency: (data.avg_latency || 0) / 1000  // 转换为秒
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 加载快捷信息
const loadQuickInfo = async () => {
  try {
    const [accounts, bots, mappings] = await Promise.all([
      api.getAccounts(),
      api.getBotConfigs(),
      api.getAllMappings()
    ])
    
    accountCount.value = accounts?.length || 0
    botCount.value = bots?.length || 0
    mappingCount.value = mappings?.length || 0
    
    // 检查是否显示空状态
    if (accountCount.value === 0 && botCount.value === 0 && mappingCount.value === 0) {
      showEmptyState.value = true
    }
  } catch (error) {
    console.error('加载快捷信息失败:', error)
  }
}

// 初始化消息趋势图表
const initMessageChart = () => {
  if (!messageChart.value) return
  
  messageChartInstance = echarts.init(messageChart.value)
  
  const option = {
    title: {
      text: '消息转发趋势',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['成功', '失败'],
      bottom: 10
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []  // 动态加载
    },
    yAxis: {
      type: 'value',
      name: '消息数'
    },
    series: [
      {
        name: '成功',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: { color: '#67C23A' },
        areaStyle: { opacity: 0.3 }
      },
      {
        name: '失败',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: { color: '#F56C6C' },
        areaStyle: { opacity: 0.3 }
      }
    ]
  }
  
  messageChartInstance.setOption(option)
}

// 初始化平台分布图表
const initPlatformChart = () => {
  if (!platformChart.value) return
  
  platformChartInstance = echarts.init(platformChart.value)
  
  const option = {
    title: {
      text: '平台分布',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%'
        },
        data: []  // 动态加载
      }
    ]
  }
  
  platformChartInstance.setOption(option)
}

// 加载图表数据
const loadChartData = async () => {
  try {
    // 生成模拟数据（TODO: 从后端API获取真实数据）
    const timeLabels = []
    const successData = []
    const failedData = []
    
    const now = new Date()
    for (let i = 59; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 1000)
      timeLabels.push(time.getHours() + ':' + String(time.getMinutes()).padStart(2, '0'))
      successData.push(Math.floor(Math.random() * 20))
      failedData.push(Math.floor(Math.random() * 3))
    }
    
    // 更新消息趋势图表
    if (messageChartInstance) {
      messageChartInstance.setOption({
        xAxis: { data: timeLabels },
        series: [
          { data: successData },
          { data: failedData }
        ]
      })
    }
    
    // 更新平台分布图表
    if (platformChartInstance) {
      const platformData = [
        { name: 'Discord', value: 450 },
        { name: 'Telegram', value: 380 },
        { name: 'Feishu', value: 120 }
      ]
      
      platformChartInstance.setOption({
        series: [{ data: platformData }]
      })
    }
  } catch (error) {
    console.error('加载图表数据失败:', error)
  }
}

// 刷新所有数据
const refreshData = async () => {
  await Promise.all([
    loadSystemStatus(),
    loadStats(),
    loadQuickInfo(),
    loadChartData()
  ])
  ElMessage.success('数据已刷新')
}

// 生命周期
onMounted(async () => {
  await refreshData()
  
  // 初始化图表
  setTimeout(() => {
    initMessageChart()
    initPlatformChart()
    loadChartData()
  }, 100)
  
  // 每30秒自动刷新
  refreshTimer = setInterval(() => {
    refreshData()
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 销毁图表实例
  if (messageChartInstance) {
    messageChartInstance.dispose()
  }
  if (platformChartInstance) {
    platformChartInstance.dispose()
  }
})
</script>

<style scoped>
.home-view {
  padding: 20px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 15px;
}

.uptime {
  color: #606266;
  font-size: 14px;
}

.quick-actions {
  display: flex;
  gap: 10px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.stat-data {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  line-height: 1.2;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 图表 */
.chart-row {
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.chart-container-small {
  width: 100%;
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 快捷操作面板 */
.quick-panel {
  margin-bottom: 20px;
}

.quick-action {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-action:hover {
  border-color: #409EFF;
  background: #ECF5FF;
  transform: scale(1.05);
}

.action-icon {
  font-size: 36px;
}

.action-text {
  flex: 1;
}

.action-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.action-desc {
  font-size: 12px;
  color: #909399;
}

/* 空状态 */
.empty-state {
  margin-top: 40px;
}

.empty-description {
  text-align: left;
  display: inline-block;
}

.empty-description h2 {
  margin-bottom: 15px;
  color: #303133;
}

.empty-description p {
  margin-bottom: 10px;
  color: #606266;
}

.setup-steps {
  text-align: left;
  margin: 15px 0;
  padding-left: 30px;
}

.setup-steps li {
  margin: 10px 0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .action-bar {
    flex-direction: column;
    gap: 15px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .quick-action {
    margin-bottom: 10px;
  }
}
</style>
