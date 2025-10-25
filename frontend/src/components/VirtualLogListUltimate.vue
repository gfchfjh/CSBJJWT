<template>
  <div class="virtual-log-list-ultimate">
    <!-- 过滤器 -->
    <el-card class="filter-card" shadow="never">
      <el-space wrap>
        <el-select v-model="filterStatus" placeholder="状态" style="width: 120px" @change="applyFilter">
          <el-option label="全部" value="" />
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="进行中" value="pending" />
        </el-select>

        <el-select v-model="filterPlatform" placeholder="平台" style="width: 120px" @change="applyFilter">
          <el-option label="全部" value="" />
          <el-option label="Discord" value="discord" />
          <el-option label="Telegram" value="telegram" />
          <el-option label="飞书" value="feishu" />
        </el-select>

        <el-input 
          v-model="filterKeyword" 
          placeholder="搜索关键词" 
          style="width: 200px"
          clearable
          @input="applyFilter"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-tag type="info">共 {{ filteredLogs.length }} 条</el-tag>
        
        <el-switch 
          v-model="autoRefresh" 
          active-text="自动刷新"
          @change="toggleAutoRefresh"
        />
      </el-space>
    </el-card>

    <!-- 虚拟滚动列表 -->
    <div class="log-container" ref="containerRef">
      <RecycleScroller
        class="scroller"
        :items="filteredLogs"
        :item-size="80"
        :buffer="200"
        key-field="id"
        v-slot="{ item }"
      >
        <div class="log-item" :class="`status-${item.status}`">
          <div class="log-header">
            <div class="log-time">
              <el-icon><Clock /></el-icon>
              {{ formatTime(item.created_at) }}
            </div>
            
            <el-tag :type="getStatusType(item.status)" size="small">
              {{ getStatusText(item.status) }}
            </el-tag>
          </div>

          <div class="log-content">
            <div class="log-route">
              <el-tag type="primary" size="small">
                # {{ item.kook_channel_name || item.kook_channel_id }}
              </el-tag>
              
              <el-icon class="arrow"><Right /></el-icon>
              
              <el-tag :type="getPlatformType(item.target_platform)" size="small">
                {{ getPlatformName(item.target_platform) }}
              </el-tag>
              
              <span class="target-channel">{{ item.target_channel }}</span>
            </div>

            <div class="log-message">
              <el-icon v-if="item.message_type === 'image'"><Picture /></el-icon>
              <el-icon v-else-if="item.message_type === 'file'"><Document /></el-icon>
              <el-icon v-else><ChatDotRound /></el-icon>
              
              <span class="message-content">
                {{ item.sender_name }}: {{ truncate(item.content, 100) }}
              </span>
            </div>

            <div v-if="item.error_message" class="log-error">
              <el-icon color="#F56C6C"><WarningFilled /></el-icon>
              <span>{{ item.error_message }}</span>
            </div>

            <div class="log-meta">
              <el-text type="info" size="small">
                延迟: {{ item.latency_ms || 0 }}ms
              </el-text>
              
              <el-button-group size="small">
                <el-button @click="viewDetail(item)">
                  <el-icon><View /></el-icon>
                  详情
                </el-button>
                <el-button v-if="item.status === 'failed'" @click="retryMessage(item)">
                  <el-icon><RefreshRight /></el-icon>
                  重试
                </el-button>
              </el-button-group>
            </div>
          </div>
        </div>
      </RecycleScroller>
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-if="filteredLogs.length === 0 && !loading"
      description="暂无日志记录"
      :image-size="200"
    />

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 消息详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="消息详情" width="700px">
      <div v-if="selectedLog" class="message-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="消息ID">{{ selectedLog.kook_message_id }}</el-descriptions-item>
          <el-descriptions-item label="发送时间">{{ formatTime(selectedLog.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="KOOK频道">{{ selectedLog.kook_channel_name }}</el-descriptions-item>
          <el-descriptions-item label="目标平台">{{ getPlatformName(selectedLog.target_platform) }}</el-descriptions-item>
          <el-descriptions-item label="目标频道">{{ selectedLog.target_channel }}</el-descriptions-item>
          <el-descriptions-item label="消息类型">{{ selectedLog.message_type }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedLog.status)">
              {{ getStatusText(selectedLog.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="延迟">{{ selectedLog.latency_ms }}ms</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="message-content-detail">
          <h4>消息内容</h4>
          <el-input 
            type="textarea" 
            :value="selectedLog.content" 
            :rows="8" 
            readonly
          />
        </div>

        <div v-if="selectedLog.error_message" class="error-detail">
          <h4>错误信息</h4>
          <el-alert type="error" :closable="false">
            {{ selectedLog.error_message }}
          </el-alert>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { RecycleScroller } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
import {
  Search,
  Clock,
  Right,
  Picture,
  Document,
  ChatDotRound,
  WarningFilled,
  View,
  RefreshRight,
  Loading
} from '@element-plus/icons-vue';
import api from '@/api';

// 数据
const logs = ref([]);
const filteredLogs = ref([]);
const filterStatus = ref('');
const filterPlatform = ref('');
const filterKeyword = ref('');
const autoRefresh = ref(true);
const loading = ref(false);
const containerRef = ref(null);
const detailDialogVisible = ref(false);
const selectedLog = ref(null);

let refreshInterval = null;

// 加载日志
const loadLogs = async () => {
  loading.value = true;
  
  try {
    const response = await api.get('/api/logs', {
      params: { limit: 10000 }  // 支持10000条日志
    });
    
    logs.value = response.logs;
    applyFilter();
  } catch (error) {
    ElMessage.error('加载日志失败');
  } finally {
    loading.value = false;
  }
};

// 应用过滤
const applyFilter = () => {
  filteredLogs.value = logs.value.filter(log => {
    // 状态过滤
    if (filterStatus.value && log.status !== filterStatus.value) {
      return false;
    }
    
    // 平台过滤
    if (filterPlatform.value && log.target_platform !== filterPlatform.value) {
      return false;
    }
    
    // 关键词过滤
    if (filterKeyword.value) {
      const keyword = filterKeyword.value.toLowerCase();
      const searchText = `${log.content} ${log.sender_name} ${log.kook_channel_name}`.toLowerCase();
      if (!searchText.includes(keyword)) {
        return false;
      }
    }
    
    return true;
  });
};

// 切换自动刷新
const toggleAutoRefresh = (value) => {
  if (value) {
    startAutoRefresh();
  } else {
    stopAutoRefresh();
  }
};

// 启动自动刷新
const startAutoRefresh = () => {
  if (refreshInterval) return;
  
  refreshInterval = setInterval(() => {
    loadLogs();
  }, 5000); // 每5秒刷新
};

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
};

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 截断文本
const truncate = (text, length) => {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
};

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    success: 'success',
    failed: 'danger',
    pending: 'warning'
  };
  return types[status] || 'info';
};

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    success: '✅ 成功',
    failed: '❌ 失败',
    pending: '⏳ 进行中'
  };
  return texts[status] || status;
};

// 获取平台名称
const getPlatformName = (platform) => {
  const names = {
    discord: 'Discord',
    telegram: 'Telegram',
    feishu: '飞书'
  };
  return names[platform] || platform;
};

// 获取平台类型
const getPlatformType = (platform) => {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  };
  return types[platform] || '';
};

// 查看详情
const viewDetail = (log) => {
  selectedLog.value = log;
  detailDialogVisible.value = true;
};

// 重试消息
const retryMessage = async (log) => {
  try {
    await api.post(`/api/logs/${log.id}/retry`);
    ElMessage.success('已加入重试队列');
  } catch (error) {
    ElMessage.error('重试失败');
  }
};

// 生命周期
onMounted(() => {
  loadLogs();
  if (autoRefresh.value) {
    startAutoRefresh();
  }
});

onUnmounted(() => {
  stopAutoRefresh();
});
</script>

<style scoped>
.virtual-log-list-ultimate {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-card {
  margin-bottom: 16px;
}

.log-container {
  flex: 1;
  background: white;
  border-radius: 4px;
  overflow: hidden;
}

.scroller {
  height: 100%;
}

.log-item {
  padding: 16px;
  border-bottom: 1px solid #EBEEF5;
  transition: background 0.3s;
}

.log-item:hover {
  background: #F5F7FA;
}

.log-item.status-success {
  border-left: 3px solid #67C23A;
}

.log-item.status-failed {
  border-left: 3px solid #F56C6C;
}

.log-item.status-pending {
  border-left: 3px solid #E6A23C;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-route {
  display: flex;
  align-items: center;
  gap: 8px;
}

.arrow {
  color: #409EFF;
}

.target-channel {
  color: #606266;
  font-size: 13px;
}

.log-message {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #303133;
}

.message-content {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-error {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #F56C6C;
  background: #FEF0F0;
  padding: 8px;
  border-radius: 4px;
}

.log-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #909399;
}

.loading-overlay .el-icon {
  font-size: 32px;
  margin-bottom: 16px;
}

.message-detail {
  padding: 10px 0;
}

.message-content-detail {
  margin: 20px 0;
}

.message-content-detail h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.error-detail {
  margin: 20px 0;
}

.error-detail h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #F56C6C;
}
</style>
