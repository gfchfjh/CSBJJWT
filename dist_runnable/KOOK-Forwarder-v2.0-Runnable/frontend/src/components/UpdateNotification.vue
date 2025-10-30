<template>
  <div class="update-notification">
    <!-- 更新通知横幅 -->
    <el-alert
      v-if="updateAvailable"
      :title="`发现新版本 v${latestVersion}`"
      type="warning"
      :closable="false"
      show-icon
      class="update-banner"
    >
      <template #default>
        <div class="update-content">
          <div>
            <p>当前版本: v{{ currentVersion }}</p>
            <p>新版本: v{{ latestVersion }}</p>
            <p v-if="isCritical" class="critical-warning">
              ⚠️ 这是一个重要的安全更新，建议立即升级！
            </p>
          </div>
          <div class="update-actions">
            <el-button type="primary" @click="showUpdateDialog">
              查看详情
            </el-button>
            <el-button @click="dismissUpdate">
              稍后提醒
            </el-button>
          </div>
        </div>
      </template>
    </el-alert>

    <!-- 更新详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="版本更新"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="update-dialog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="当前版本">
            v{{ currentVersion }}
          </el-descriptions-item>
          <el-descriptions-item label="新版本">
            <el-tag type="success">v{{ latestVersion }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发布日期" :span="2">
            {{ releaseDate }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">更新内容</el-divider>
        
        <div class="changelog" v-html="formattedChangelog"></div>

        <el-progress
          v-if="isDownloading"
          :percentage="downloadProgress"
          :status="downloadProgress === 100 ? 'success' : undefined"
        >
          <template #default="{ percentage }">
            {{ percentage }}% 下载中...
          </template>
        </el-progress>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="downloadUpdate"
            :loading="isDownloading"
            :disabled="downloadProgress === 100"
          >
            {{ downloadProgress === 100 ? '下载完成，重启安装' : '立即下载' }}
          </el-button>
          <el-button
            v-if="downloadProgress === 100"
            type="success"
            @click="installUpdate"
          >
            立即重启安装
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

// 数据
const updateAvailable = ref(false);
const currentVersion = ref('');
const latestVersion = ref('');
const downloadUrl = ref('');
const changelog = ref('');
const releaseDate = ref('');
const isCritical = ref(false);

const dialogVisible = ref(false);
const isDownloading = ref(false);
const downloadProgress = ref(0);

let checkInterval = null;

// 计算属性
const formattedChangelog = computed(() => {
  if (!changelog.value) return '暂无更新说明';
  
  // 简单的Markdown转HTML
  return changelog.value
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br/>');
});

// 方法
const checkForUpdates = async (silent = false) => {
  try {
    const response = await axios.get('http://localhost:9527/api/updates/check');
    const data = response.data;
    
    currentVersion.value = data.current_version;
    
    if (data.has_update) {
      updateAvailable.value = true;
      latestVersion.value = data.latest_version;
      downloadUrl.value = data.download_url;
      changelog.value = data.changelog;
      isCritical.value = data.is_critical;
      
      if (!silent) {
        ElMessage.success('发现新版本！');
      }
      
      // 如果是关键更新，自动打开对话框
      if (isCritical.value) {
        showUpdateDialog();
      }
    } else {
      if (!silent) {
        ElMessage.info('当前已是最新版本');
      }
    }
  } catch (error) {
    console.error('检查更新失败:', error);
    if (!silent) {
      ElMessage.error('检查更新失败');
    }
  }
};

const showUpdateDialog = () => {
  dialogVisible.value = true;
};

const dismissUpdate = () => {
  updateAvailable.value = false;
  
  // 延迟7天再提醒
  localStorage.setItem('update_dismissed_until', Date.now() + 7 * 24 * 60 * 60 * 1000);
};

const downloadUpdate = async () => {
  if (!downloadUrl.value) {
    ElMessage.error('下载链接不可用');
    return;
  }
  
  isDownloading.value = true;
  downloadProgress.value = 0;
  
  // 模拟下载进度（实际应该通过Electron的IPC通信）
  const interval = setInterval(() => {
    downloadProgress.value += 10;
    
    if (downloadProgress.value >= 100) {
      clearInterval(interval);
      isDownloading.value = false;
      ElMessage.success('下载完成！');
    }
  }, 500);
  
  // 打开下载链接
  window.open(downloadUrl.value, '_blank');
};

const installUpdate = () => {
  // 通过Electron IPC触发安装
  if (window.electron && window.electron.installUpdate) {
    window.electron.installUpdate();
  } else {
    ElMessage.warning('请关闭应用后手动安装');
  }
};

// 生命周期
onMounted(() => {
  // 首次检查
  const dismissedUntil = localStorage.getItem('update_dismissed_until');
  if (!dismissedUntil || Date.now() > parseInt(dismissedUntil)) {
    checkForUpdates(true);
  }
  
  // 定期检查（每小时）
  checkInterval = setInterval(() => {
    checkForUpdates(true);
  }, 60 * 60 * 1000);
  
  // 监听Electron的更新事件
  if (window.electron && window.electron.onUpdateStatus) {
    window.electron.onUpdateStatus((event, data) => {
      if (data.status === 'download-progress') {
        downloadProgress.value = data.percent;
      } else if (data.status === 'downloaded') {
        downloadProgress.value = 100;
        isDownloading.value = false;
        ElMessage.success('更新已下载，可以安装了');
      }
    });
  }
});

onUnmounted(() => {
  if (checkInterval) {
    clearInterval(checkInterval);
  }
});

// 暴露方法供外部调用
defineExpose({
  checkForUpdates
});
</script>

<style scoped>
.update-banner {
  margin-bottom: 20px;
}

.update-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.update-content p {
  margin: 5px 0;
}

.critical-warning {
  color: #F56C6C;
  font-weight: bold;
}

.update-actions {
  display: flex;
  gap: 10px;
}

.update-dialog {
  max-height: 500px;
  overflow-y: auto;
}

.changelog {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.changelog h1,
.changelog h2,
.changelog h3 {
  margin: 10px 0;
  color: #303133;
}

.changelog code {
  padding: 2px 6px;
  background: #e4e7ed;
  border-radius: 3px;
  font-family: monospace;
}

.dialog-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>
