<template>
  <div class="settings-ultimate">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 基础设置 -->
      <el-tab-pane label="基础设置" name="basic">
        <el-form :model="basicSettings" label-width="140px">
          <el-divider content-position="left">
            <el-icon><Service /></el-icon>
            服务控制
          </el-divider>
          
          <el-form-item label="当前状态">
            <el-tag :type="serviceRunning ? 'success' : 'danger'" size="large">
              {{ serviceRunning ? '🟢 运行中' : '🔴 已停止' }}
            </el-tag>
            <span v-if="serviceRunning" style="margin-left: 15px">
              运行时长: {{ formatUptime(uptime) }}
            </span>
          </el-form-item>
          
          <el-form-item label="服务操作">
            <el-button-group>
              <el-button
                v-if="!serviceRunning"
                type="success"
                :icon="VideoPlay"
                @click="startService"
              >
                启动服务
              </el-button>
              <el-button
                v-else
                type="danger"
                :icon="VideoPause"
                @click="stopService"
              >
                停止服务
              </el-button>
              <el-button :icon="RefreshRight" @click="restartService">
                重启服务
              </el-button>
            </el-button-group>
          </el-form-item>
          
          <el-form-item label="开机自动启动">
            <el-switch
              v-model="basicSettings.autoStart"
              active-text="开启"
              inactive-text="关闭"
            />
          </el-form-item>
          
          <el-form-item label="最小化到托盘">
            <el-switch
              v-model="basicSettings.minimizeToTray"
              active-text="开启"
              inactive-text="关闭"
            />
          </el-form-item>
          
          <el-form-item label="关闭窗口行为">
            <el-radio-group v-model="basicSettings.closeAction">
              <el-radio value="minimize">最小化到托盘</el-radio>
              <el-radio value="quit">退出程序</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 图片处理设置 -->
      <el-tab-pane label="图片处理" name="image">
        <el-form :model="imageSettings" label-width="140px">
          <el-divider content-position="left">
            <el-icon><Picture /></el-icon>
            图片策略
          </el-divider>
          
          <el-form-item label="图片处理策略">
            <el-radio-group v-model="imageSettings.strategy">
              <el-radio value="smart">
                <div class="radio-content">
                  <strong>智能模式</strong>
                  <span class="radio-hint">优先直传，失败用图床（推荐）</span>
                </div>
              </el-radio>
              <el-radio value="direct">
                <div class="radio-content">
                  <strong>仅直传模式</strong>
                  <span class="radio-hint">图片直接上传到目标平台</span>
                </div>
              </el-radio>
              <el-radio value="imgbed">
                <div class="radio-content">
                  <strong>仅图床模式</strong>
                  <span class="radio-hint">所有图片使用内置图床</span>
                </div>
              </el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-divider content-position="left">
            <el-icon><FolderOpened /></el-icon>
            图床设置
          </el-divider>
          
          <el-form-item label="存储路径">
            <el-input
              v-model="imageSettings.storagePath"
              readonly
              style="width: 400px"
            >
              <template #append>
                <el-button :icon="FolderOpened" @click="openStorageFolder">
                  打开
                </el-button>
                <el-button :icon="Edit" @click="changeStoragePath">
                  更改
                </el-button>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="最大占用空间">
            <el-input-number
              v-model="imageSettings.maxStorageGB"
              :min="1"
              :max="100"
              style="width: 150px"
            />
            <span style="margin-left: 10px">GB</span>
            
            <div class="storage-info">
              <p>当前已用: {{ storageStats.used_gb?.toFixed(2) }} GB ({{ storageStats.usage_percentage?.toFixed(1) }}%)</p>
              <el-progress
                :percentage="storageStats.usage_percentage || 0"
                :color="getProgressColor(storageStats.usage_percentage)"
              />
            </div>
          </el-form-item>
          
          <el-form-item label="自动清理">
            <el-input-number
              v-model="imageSettings.autoCleanupDays"
              :min="1"
              :max="365"
              style="width: 150px"
            />
            <span style="margin-left: 10px">天前的图片</span>
            
            <el-button
              type="danger"
              :icon="Delete"
              style="margin-left: 20px"
              @click="cleanupNow"
            >
              立即清理
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 邮件告警 -->
      <el-tab-pane label="邮件告警" name="email">
        <el-form :model="emailSettings" label-width="140px">
          <el-form-item label="启用邮件告警">
            <el-switch
              v-model="emailSettings.enabled"
              active-text="开启"
              inactive-text="关闭"
            />
          </el-form-item>
          
          <template v-if="emailSettings.enabled">
            <el-divider content-position="left">SMTP配置</el-divider>
            
            <el-form-item label="SMTP服务器">
              <el-input
                v-model="emailSettings.smtp_host"
                placeholder="smtp.gmail.com"
                style="width: 300px"
              />
            </el-form-item>
            
            <el-form-item label="SMTP端口">
              <el-input-number
                v-model="emailSettings.smtp_port"
                :min="1"
                :max="65535"
                style="width: 150px"
              />
            </el-form-item>
            
            <el-form-item label="使用SSL/TLS">
              <el-switch v-model="emailSettings.smtp_use_tls" />
            </el-form-item>
            
            <el-form-item label="发件邮箱">
              <el-input
                v-model="emailSettings.sender_email"
                placeholder="your-email@gmail.com"
                style="width: 300px"
              />
            </el-form-item>
            
            <el-form-item label="邮箱密码">
              <el-input
                v-model="emailSettings.sender_password"
                type="password"
                show-password
                placeholder="邮箱密码或应用专用密码"
                style="width: 300px"
              />
            </el-form-item>
            
            <el-form-item label="收件邮箱">
              <el-input
                v-model="emailSettings.receiver_email"
                placeholder="your-email@gmail.com"
                style="width: 300px"
              />
            </el-form-item>
            
            <el-divider content-position="left">告警规则</el-divider>
            
            <el-form-item label="告警条件">
              <el-checkbox-group v-model="emailSettings.alert_conditions">
                <el-checkbox value="service_down">服务异常停止</el-checkbox>
                <el-checkbox value="account_offline">账号掉线</el-checkbox>
                <el-checkbox value="message_failed">消息转发失败</el-checkbox>
                <el-checkbox value="disk_full">磁盘空间不足</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="测试邮件">
              <el-button :icon="Message" @click="sendTestEmail">
                发送测试邮件
              </el-button>
            </el-form-item>
          </template>
        </el-form>
      </el-tab-pane>
      
      <!-- 备份与恢复 -->
      <el-tab-pane label="备份与恢复" name="backup">
        <el-form label-width="140px">
          <el-divider content-position="left">
            <el-icon><FolderOpened /></el-icon>
            配置备份
          </el-divider>
          
          <el-form-item label="最后备份时间">
            <span>{{ lastBackupTime || '从未备份' }}</span>
          </el-form-item>
          
          <el-form-item label="备份操作">
            <el-button type="primary" :icon="Download" @click="backupNow">
              立即备份配置
            </el-button>
            <el-button :icon="Upload" @click="showRestoreDialog">
              恢复配置
            </el-button>
          </el-form-item>
          
          <el-form-item label="自动备份">
            <el-switch
              v-model="backupSettings.autoBackup"
              active-text="每天自动备份"
              inactive-text="关闭"
            />
          </el-form-item>
          
          <el-form-item label="备份保留">
            <el-input-number
              v-model="backupSettings.keepDays"
              :min="1"
              :max="365"
              style="width: 150px"
            />
            <span style="margin-left: 10px">天</span>
          </el-form-item>
          
          <el-form-item label="备份文件列表">
            <el-table :data="backupFiles" stripe max-height="300">
              <el-table-column prop="filename" label="文件名" show-overflow-tooltip />
              <el-table-column label="大小" width="120">
                <template #default="{ row }">
                  {{ formatSize(row.size) }}
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" :icon="Upload" @click="restoreBackup(row.filename)">
                    恢复
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    :icon="Delete"
                    @click="deleteBackup(row.filename)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 高级设置 -->
      <el-tab-pane label="高级设置" name="advanced">
        <el-form label-width="140px">
          <el-divider content-position="left">
            <el-icon><Setting /></el-icon>
            日志设置
          </el-divider>
          
          <el-form-item label="日志级别">
            <el-select v-model="advancedSettings.logLevel" style="width: 200px">
              <el-option label="调试 (DEBUG)" value="debug" />
              <el-option label="普通 (INFO)" value="info" />
              <el-option label="警告 (WARNING)" value="warning" />
              <el-option label="仅错误 (ERROR)" value="error" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="日志保留时长">
            <el-input-number
              v-model="advancedSettings.logRetentionDays"
              :min="1"
              :max="365"
              style="width: 150px"
            />
            <span style="margin-left: 10px">天</span>
          </el-form-item>
          
          <el-form-item label="日志存储">
            <div class="log-info">
              <p>已用: {{ logStats.size_mb }} MB</p>
              <el-button :icon="FolderOpened" @click="openLogFolder">
                打开日志文件夹
              </el-button>
              <el-button type="danger" :icon="Delete" @click="clearLogs">
                清空所有日志
              </el-button>
            </div>
          </el-form-item>
          
          <el-divider content-position="left">
            <el-icon><Bell /></el-icon>
            通知设置
          </el-divider>
          
          <el-form-item label="桌面通知">
            <el-checkbox-group v-model="advancedSettings.notifications">
              <el-checkbox value="service_error">服务异常时通知</el-checkbox>
              <el-checkbox value="account_offline">账号掉线时通知</el-checkbox>
              <el-checkbox value="message_failed">消息转发失败时通知</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          
          <el-divider content-position="left">
            <el-icon><Monitor /></el-icon>
            界面设置
          </el-divider>
          
          <el-form-item label="语言">
            <el-select v-model="advancedSettings.language" style="width: 200px">
              <el-option label="简体中文" value="zh-CN" />
              <el-option label="English" value="en-US" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="主题">
            <el-radio-group v-model="advancedSettings.theme">
              <el-radio value="light">浅色</el-radio>
              <el-radio value="dark">深色</el-radio>
              <el-radio value="auto">跟随系统</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-divider content-position="left">
            <el-icon><Connection /></el-icon>
            更新设置
          </el-divider>
          
          <el-form-item label="自动检查更新">
            <el-radio-group v-model="advancedSettings.autoUpdate">
              <el-radio value="auto">自动检查并提示</el-radio>
              <el-radio value="manual">手动检查</el-radio>
              <el-radio value="disable">禁用</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="当前版本">
            <span>{{ currentVersion }}</span>
            <el-button style="margin-left: 15px" @click="checkUpdate">
              检查更新
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 保存按钮 -->
    <div class="footer-actions">
      <el-button type="primary" size="large" :loading="saving" @click="saveAllSettings">
        <el-icon><Check /></el-icon>
        保存所有设置
      </el-button>
      <el-button size="large" @click="resetSettings">
        <el-icon><RefreshLeft /></el-icon>
        重置为默认
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Service,
  VideoPlay,
  VideoPause,
  RefreshRight,
  Picture,
  FolderOpened,
  Edit,
  Delete,
  Setting,
  Bell,
  Monitor,
  Connection,
  Check,
  RefreshLeft,
  Download,
  Upload,
  Message
} from '@element-plus/icons-vue'
import api from '@/api'

const activeTab = ref('basic')
const saving = ref(false)
const serviceRunning = ref(false)
const uptime = ref(0)
const currentVersion = ref('6.8.0')

// 基础设置
const basicSettings = ref({
  autoStart: false,
  minimizeToTray: true,
  closeAction: 'minimize'
})

// 图片设置
const imageSettings = ref({
  strategy: 'smart',
  storagePath: 'C:\\Users\\Documents\\KookForwarder\\data\\images',
  maxStorageGB: 10,
  autoCleanupDays: 7
})

const storageStats = ref({
  used_gb: 0,
  usage_percentage: 0
})

// 邮件设置
const emailSettings = ref({
  enabled: false,
  smtp_host: 'smtp.gmail.com',
  smtp_port: 587,
  smtp_use_tls: true,
  sender_email: '',
  sender_password: '',
  receiver_email: '',
  alert_conditions: ['service_down', 'account_offline']
})

// 备份设置
const backupSettings = ref({
  autoBackup: true,
  keepDays: 30
})

const lastBackupTime = ref('')
const backupFiles = ref([])

// 高级设置
const advancedSettings = ref({
  logLevel: 'info',
  logRetentionDays: 3,
  notifications: ['service_error', 'account_offline'],
  language: 'zh-CN',
  theme: 'auto',
  autoUpdate: 'auto'
})

const logStats = ref({
  size_mb: 0
})

// 方法
const startService = async () => {
  try {
    await api.post('/api/system/start')
    ElMessage.success('服务启动成功')
    serviceRunning.value = true
  } catch (error) {
    ElMessage.error('启动失败: ' + error.message)
  }
}

const stopService = async () => {
  try {
    await api.post('/api/system/stop')
    ElMessage.success('服务已停止')
    serviceRunning.value = false
  } catch (error) {
    ElMessage.error('停止失败: ' + error.message)
  }
}

const restartService = async () => {
  try {
    await api.post('/api/system/restart')
    ElMessage.success('服务重启成功')
  } catch (error) {
    ElMessage.error('重启失败: ' + error.message)
  }
}

const formatUptime = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}小时${minutes}分钟`
}

const getProgressColor = (percentage) => {
  if (percentage >= 90) return '#F56C6C'
  if (percentage >= 70) return '#E6A23C'
  return '#67C23A'
}

const openStorageFolder = () => {
  if (window.electron) {
    window.electron.openPath(imageSettings.value.storagePath)
  }
}

const changeStoragePath = async () => {
  if (window.electron) {
    const path = await window.electron.selectFolder()
    if (path) {
      imageSettings.value.storagePath = path
    }
  }
}

const cleanupNow = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清理 ${imageSettings.value.autoCleanupDays} 天前的图片吗？`,
      '确认清理',
      { type: 'warning' }
    )
    
    await api.post('/api/image-storage/cleanup', {
      strategy: 'days',
      days: imageSettings.value.autoCleanupDays
    })
    
    ElMessage.success('清理完成')
    loadStorageStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清理失败')
    }
  }
}

const sendTestEmail = async () => {
  try {
    await api.post('/api/email/test', emailSettings.value)
    ElMessage.success('测试邮件已发送，请检查收件箱')
  } catch (error) {
    ElMessage.error('发送失败: ' + (error.response?.data?.detail || error.message))
  }
}

const backupNow = async () => {
  try {
    const response = await api.post('/api/backup/create')
    ElMessage.success('备份成功: ' + response.data.filename)
    loadBackupFiles()
  } catch (error) {
    ElMessage.error('备份失败')
  }
}

const showRestoreDialog = () => {
  if (backupFiles.value.length === 0) {
    ElMessage.warning('没有可恢复的备份文件')
    return
  }
  // 显示备份文件列表供用户选择
}

const restoreBackup = async (filename) => {
  try {
    await ElMessageBox.confirm(
      `确定要恢复备份 "${filename}" 吗？当前配置将被覆盖！`,
      '确认恢复',
      { type: 'warning' }
    )
    
    await api.post('/api/backup/restore', { filename })
    ElMessage.success('恢复成功，请重启服务')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('恢复失败')
    }
  }
}

const deleteBackup = async (filename) => {
  try {
    await ElMessageBox.confirm('确定要删除这个备份吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete('/api/backup/delete', { data: { filename } })
    ElMessage.success('删除成功')
    loadBackupFiles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const openLogFolder = () => {
  if (window.electron) {
    window.electron.openPath('logs')
  }
}

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有日志吗？', '确认清空', {
      type: 'warning'
    })
    
    await api.delete('/api/logs/clear')
    ElMessage.success('日志已清空')
    logStats.value.size_mb = 0
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败')
    }
  }
}

const checkUpdate = async () => {
  try {
    const response = await api.get('/api/updates/check')
    if (response.data.has_update) {
      ElMessageBox.confirm(
        `发现新版本 ${response.data.latest_version}，是否立即下载？`,
        '发现更新',
        { type: 'success' }
      )
    } else {
      ElMessage.info('当前已是最新版本')
    }
  } catch (error) {
    ElMessage.error('检查更新失败')
  }
}

const saveAllSettings = async () => {
  saving.value = true
  
  try {
    await api.post('/api/settings/save', {
      basic: basicSettings.value,
      image: imageSettings.value,
      email: emailSettings.value,
      backup: backupSettings.value,
      advanced: advancedSettings.value
    })
    
    ElMessage.success('设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const resetSettings = async () => {
  try {
    await ElMessageBox.confirm('确定要重置所有设置为默认值吗？', '确认重置', {
      type: 'warning'
    })
    
    // 重置逻辑
    ElMessage.info('已重置为默认设置')
  } catch {
    // 用户取消
  }
}

const loadStorageStats = async () => {
  try {
    const response = await api.get('/api/image-storage/stats')
    storageStats.value = response.data
  } catch (error) {
    console.error('加载存储统计失败:', error)
  }
}

const loadBackupFiles = async () => {
  try {
    const response = await api.get('/api/backup/list')
    backupFiles.value = response.data
  } catch (error) {
    console.error('加载备份文件失败:', error)
  }
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadStorageStats()
  loadBackupFiles()
})
</script>

<style scoped>
.settings-ultimate {
  padding: 20px;
}

.radio-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.radio-hint {
  font-size: 12px;
  color: #909399;
}

.storage-info,
.log-info {
  margin-top: 10px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.footer-actions {
  margin-top: 30px;
  text-align: center;
}

.footer-actions .el-button {
  min-width: 150px;
}

/* 暗黑模式 */
.dark .storage-info,
.dark .log-info {
  background: #2c2c2c;
}
</style>
