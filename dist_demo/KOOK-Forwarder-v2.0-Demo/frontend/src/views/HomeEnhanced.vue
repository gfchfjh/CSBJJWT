<template>
  <div class="home-enhanced">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-total">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="50"><DocumentCopy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日转发</div>
              <div class="stat-value">{{ formatNumber(stats.total) }}</div>
              <div class="stat-trend" :class="getTrendClass(stats.totalTrend)">
                <el-icon><CaretTop v-if="stats.totalTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(stats.totalTrend) }}% vs 昨日
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-success">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon :size="50"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">成功率</div>
              <div class="stat-value">{{ stats.successRate.toFixed(1) }}%</div>
              <el-progress
                :percentage="stats.successRate"
                :show-text="false"
                :stroke-width="6"
                :color="getSuccessRateColor(stats.successRate)"
              />
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-latency">
          <div class="stat-content">
            <div class="stat-icon warning">
              <el-icon :size="50"><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">平均延迟</div>
              <div class="stat-value">{{ stats.avgLatency.toFixed(1) }}s</div>
              <div class="stat-hint">
                {{ getLatencyLevel(stats.avgLatency) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-failed">
          <div class="stat-content">
            <div class="stat-icon danger">
              <el-icon :size="50"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">失败消息</div>
              <div class="stat-value">{{ stats.failed }}</div>
              <el-link type="danger" @click="showFailedMessages" v-if="stats.failed > 0">
                查看详情 →
              </el-link>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时图表 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="chart-header">
              <h3>📈 实时转发量</h3>
              <el-radio-group v-model="timeRange" size="small" @change="loadChartData">
                <el-radio-button label="1h">最近1小时</el-radio-button>
                <el-radio-button label="6h">最近6小时</el-radio-button>
                <el-radio-button label="24h">最近24小时</el-radio-button>
                <el-radio-button label="7d">最近7天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="chartRef" style="height: 300px"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="platform-card">
          <template #header>
            <h3>🎯 平台分布</h3>
          </template>
          <div ref="platformChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" class="action-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <h3>⚡ 快捷操作</h3>
          </template>
          <div class="quick-actions">
            <el-button
              :type="serviceStatus === 'running' ? 'danger' : 'success'"
              :icon="serviceStatus === 'running' ? VideoPause : VideoPlay"
              @click="toggleService"
              :loading="isToggling"
            >
              {{ serviceStatus === 'running' ? '停止服务' : '启动服务' }}
            </el-button>
            <el-button type="primary" :icon="Refresh" @click="restartService" :loading="isRestarting">
              重启服务
            </el-button>
            <el-button :icon="View" @click="goToLogs">
              查看实时日志
            </el-button>
            <el-button :icon="Delete" @click="clearQueue">
              清空消息队列
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近消息 -->
    <el-row :gutter="20" class="recent-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="recent-header">
              <h3>📝 最近转发（实时更新）</h3>
              <el-button size="small" @click="loadRecentMessages">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="recentMessages" stripe style="width: 100%">
            <el-table-column prop="time" label="时间" width="100">
              <template #default="{ row }">
                {{ formatTime(row.time) }}
              </template>
            </el-table-column>
            <el-table-column prop="source" label="来源" width="200">
              <template #default="{ row }">
                <el-icon><ChatDotRound /></el-icon>
                {{ row.source }}
              </template>
            </el-table-column>
            <el-table-column prop="target" label="目标" width="200">
              <template #default="{ row }">
                <el-tag :type="getPlatformTagType(row.platform)">
                  {{ row.target }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="内容" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.content }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
                  {{ row.status === 'success' ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="latency" label="延迟" width="100">
              <template #default="{ row }">
                {{ row.latency.toFixed(2) }}s
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  DocumentCopy, CircleCheck, Timer, CircleClose, Refresh,
  VideoPlay, VideoPause, View, Delete, ChatDotRound,
  CaretTop, CaretBottom
} from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import axios from 'axios';

const router = useRouter();

// 数据
const stats = ref({
  total: 0,
  successRate: 0,
  avgLatency: 0,
  failed: 0,
  totalTrend: 0
});

const serviceStatus = ref('stopped');
const isToggling = ref(false);
const isRestarting = ref(false);
const timeRange = ref('1h');
const recentMessages = ref([]);

// 图表
const chartRef = ref(null);
const platformChartRef = ref(null);
let mainChart = null;
let platformChart = null;
let updateInterval = null;

// 方法
const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num;
};

const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

const getTrendClass = (trend) => {
  return trend > 0 ? 'trend-up' : 'trend-down';
};

const getSuccessRateColor = (rate) => {
  if (rate >= 95) return '#67C23A';
  if (rate >= 80) return '#E6A23C';
  return '#F56C6C';
};

const getLatencyLevel = (latency) => {
  if (latency < 1) return '极快';
  if (latency < 2) return '快速';
  if (latency < 5) return '正常';
  return '较慢';
};

const getPlatformTagType = (platform) => {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  };
  return types[platform] || 'info';
};

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await axios.get('http://localhost:9527/api/stats/today');
    stats.value = response.data;
  } catch (error) {
    console.error('加载统计失败:', error);
  }
};

// 加载图表数据
const loadChartData = async () => {
  try {
    const response = await axios.get(`http://localhost:9527/api/stats/timeline`, {
      params: { range: timeRange.value }
    });
    
    const data = response.data;
    
    // 更新主图表
    if (mainChart) {
      mainChart.setOption({
        xAxis: {
          data: data.timeline
        },
        series: [{
          data: data.values
        }]
      });
    }
    
    // 更新平台分布
    if (platformChart) {
      platformChart.setOption({
        series: [{
          data: data.platformDistribution
        }]
      });
    }
  } catch (error) {
    console.error('加载图表数据失败:', error);
  }
};

// 加载最近消息
const loadRecentMessages = async () => {
  try {
    const response = await axios.get('http://localhost:9527/api/messages/recent', {
      params: { limit: 10 }
    });
    recentMessages.value = response.data;
  } catch (error) {
    console.error('加载最近消息失败:', error);
  }
};

// 初始化图表
const initCharts = () => {
  // 主图表
  if (chartRef.value) {
    mainChart = echarts.init(chartRef.value);
    mainChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: [],
        boundaryGap: false
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        type: 'line',
        data: [],
        smooth: true,
        areaStyle: {
          color: 'rgba(64, 158, 255, 0.2)'
        },
        lineStyle: {
          color: '#409EFF',
          width: 2
        },
        itemStyle: {
          color: '#409EFF'
        }
      }]
    });
  }
  
  // 平台分布饼图
  if (platformChartRef.value) {
    platformChart = echarts.init(platformChartRef.value);
    platformChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        name: '平台',
        type: 'pie',
        radius: '50%',
        data: [],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    });
  }
};

// 服务控制
const toggleService = async () => {
  isToggling.value = true;
  
  try {
    if (serviceStatus.value === 'running') {
      await axios.post('http://localhost:9527/api/system/stop');
      serviceStatus.value = 'stopped';
      ElMessage.success('服务已停止');
    } else {
      await axios.post('http://localhost:9527/api/system/start');
      serviceStatus.value = 'running';
      ElMessage.success('服务已启动');
    }
  } catch (error) {
    ElMessage.error(`操作失败：${error.message}`);
  } finally {
    isToggling.value = false;
  }
};

const restartService = async () => {
  isRestarting.value = true;
  
  try {
    await axios.post('http://localhost:9527/api/system/restart');
    ElMessage.success('服务已重启');
  } catch (error) {
    ElMessage.error(`重启失败：${error.message}`);
  } finally {
    isRestarting.value = false;
  }
};

const clearQueue = () => {
  ElMessageBox.confirm('确定要清空消息队列吗？', '确认', {
    type: 'warning'
  }).then(async () => {
    try {
      await axios.post('http://localhost:9527/api/queue/clear');
      ElMessage.success('队列已清空');
    } catch (error) {
      ElMessage.error(`清空失败：${error.message}`);
    }
  }).catch(() => {});
};

const showFailedMessages = () => {
  router.push('/logs?filter=failed');
};

const goToLogs = () => {
  router.push('/logs');
};

// 生命周期
onMounted(async () => {
  await loadStats();
  await nextTick();
  initCharts();
  await loadChartData();
  await loadRecentMessages();
  
  // 定时更新
  updateInterval = setInterval(() => {
    loadStats();
    loadChartData();
    loadRecentMessages();
  }, 5000);
});

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval);
  }
  
  if (mainChart) {
    mainChart.dispose();
  }
  
  if (platformChart) {
    platformChart.dispose();
  }
});
</script>

<style scoped>
.home-enhanced {
  padding: 20px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  gap: 15px;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.success {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
}

.stat-icon.warning {
  background: linear-gradient(135deg, #E6A23C 0%, #f7ba2a 100%);
}

.stat-icon.danger {
  background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-up {
  color: #67C23A;
}

.trend-down {
  color: #F56C6C;
}

.stat-hint {
  font-size: 12px;
  color: #909399;
}

/* 图表 */
.chart-row {
  margin-bottom: 20px;
}

.chart-card,
.platform-card {
  height: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h3 {
  margin: 0;
}

/* 快捷操作 */
.action-row {
  margin-bottom: 20px;
}

.quick-actions {
  display: flex;
  gap: 15px;
}

/* 最近消息 */
.recent-row {
  margin-bottom: 20px;
}

.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-header h3 {
  margin: 0;
}
</style>
