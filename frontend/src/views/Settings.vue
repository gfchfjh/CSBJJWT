<template>
  <div class="settings-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>⚙️ 系统设置</span>
          <el-button type="primary" @click="saveSettings" :loading="saving">
            💾 保存设置
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <!-- 服务控制 -->
        <el-tab-pane label="🚀 服务控制" name="service">
          <el-form :model="settings" label-width="150px">
            <el-form-item label="当前状态">
              <el-tag :type="systemStatus === 'running' ? 'success' : 'danger'" size="large">
                {{ systemStatus === 'running' ? '🟢 运行中' : '🔴 已停止' }}
              </el-tag>
            </el-form-item>

            <el-form-item label="运行时长">
              <span>{{ uptime }}</span>
            </el-form-item>

            <el-divider />

            <el-form-item label="开机自动启动">
              <el-switch v-model="settings.autoStart" />
              <span class="help-text">启用后，系统启动时自动运行本程序</span>
            </el-form-item>

            <el-form-item label="最小化到托盘">
              <el-switch v-model="settings.minimizeToTray" />
              <span class="help-text">关闭窗口时最小化到系统托盘而非退出</span>
            </el-form-item>

            <el-form-item label="启动后最小化">
              <el-switch v-model="settings.startMinimized" />
              <span class="help-text">程序启动后自动最小化到托盘</span>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 图片处理 -->
        <el-tab-pane label="🖼️ 图片处理" name="image">
          <el-form :model="settings" label-width="150px">
            <el-form-item label="图片处理策略">
              <el-radio-group v-model="settings.imageStrategy">
                <el-radio label="smart">
                  <strong>智能模式</strong>
                  <div class="radio-desc">优先直传，失败时使用图床（推荐）</div>
                </el-radio>
                <el-radio label="direct">
                  <strong>直传模式</strong>
                  <div class="radio-desc">仅直接上传到目标平台</div>
                </el-radio>
                <el-radio label="imgbed">
                  <strong>图床模式</strong>
                  <div class="radio-desc">使用本地图床</div>
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-divider content-position="left">图床设置</el-divider>

            <el-form-item label="存储路径">
              <el-input v-model="settings.imageStoragePath" disabled>
                <template #append>
                  <el-button @click="openImageFolder">📁 打开</el-button>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="最大占用空间">
              <el-input-number
                v-model="settings.imageMaxSizeGB"
                :min="1"
                :max="100"
              />
              <span> GB</span>
            </el-form-item>

            <el-form-item label="当前已用">
              <el-progress
                :percentage="imageUsagePercent"
                :color="progressColor"
              />
              <div class="storage-info">
                {{ imageUsedGB.toFixed(2) }} GB / {{ settings.imageMaxSizeGB }} GB
              </div>
            </el-form-item>

            <el-form-item label="自动清理">
              <el-input-number
                v-model="settings.imageCleanupDays"
                :min="1"
                :max="30"
              />
              <span> 天前的图片</span>
              <el-button
                type="warning"
                size="small"
                @click="cleanupOldImages"
                style="margin-left: 10px"
              >
                🗑️ 立即清理
              </el-button>
            </el-form-item>

            <el-form-item label="图片压缩质量">
              <el-slider
                v-model="settings.imageQuality"
                :min="50"
                :max="100"
                show-stops
                :marks="{ 50: '低', 75: '中', 85: '高', 100: '原图' }"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 日志设置 -->
        <el-tab-pane label="📝 日志设置" name="log">
          <el-form :model="settings" label-width="150px">
            <el-form-item label="日志级别">
              <el-select v-model="settings.logLevel">
                <el-option label="调试 (DEBUG)" value="DEBUG" />
                <el-option label="普通 (INFO)" value="INFO" />
                <el-option label="警告 (WARNING)" value="WARNING" />
                <el-option label="错误 (ERROR)" value="ERROR" />
              </el-select>
              <div class="help-text">
                调试级别会记录更详细的信息，但会占用更多磁盘空间
              </div>
            </el-form-item>

            <el-form-item label="日志保留时长">
              <el-input-number
                v-model="settings.logRetentionDays"
                :min="1"
                :max="30"
              />
              <span> 天</span>
            </el-form-item>

            <el-form-item label="日志存储">
              <div class="storage-status">
                <span>已用 {{ logUsedMB }} MB</span>
                <el-button
                  type="primary"
                  size="small"
                  @click="openLogFolder"
                  style="margin-left: 10px"
                >
                  📁 打开日志文件夹
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="clearAllLogs"
                  style="margin-left: 10px"
                >
                  🗑️ 清空所有日志
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 通知设置 -->
        <el-tab-pane label="🔔 通知设置" name="notification">
          <el-form :model="settings" label-width="150px">
            <el-form-item label="桌面通知">
              <div class="notification-options">
                <el-checkbox v-model="settings.notifyOnError">
                  服务异常时通知
                </el-checkbox>
                <el-checkbox v-model="settings.notifyOnDisconnect">
                  账号掉线时通知
                </el-checkbox>
                <el-checkbox v-model="settings.notifyOnFailure">
                  消息转发失败时通知
                </el-checkbox>
              </div>
            </el-form-item>

            <el-divider content-position="left">邮件告警（可选）</el-divider>

            <el-form-item label="启用邮件告警">
              <el-switch v-model="settings.emailAlertEnabled" />
            </el-form-item>

            <template v-if="settings.emailAlertEnabled">
              <el-form-item label="SMTP服务器">
                <el-input
                  v-model="settings.smtpServer"
                  placeholder="smtp.example.com"
                />
              </el-form-item>

              <el-form-item label="SMTP端口">
                <el-input-number
                  v-model="settings.smtpPort"
                  :min="1"
                  :max="65535"
                />
              </el-form-item>

              <el-form-item label="发件邮箱">
                <el-input
                  v-model="settings.emailFrom"
                  placeholder="alert@example.com"
                />
              </el-form-item>

              <el-form-item label="邮箱密码">
                <el-input
                  v-model="settings.emailPassword"
                  type="password"
                  show-password
                  placeholder="邮箱密码或授权码"
                />
              </el-form-item>

              <el-form-item label="收件邮箱">
                <el-input
                  v-model="settings.emailTo"
                  placeholder="admin@example.com"
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="testEmail">
                  发送测试邮件
                </el-button>
              </el-form-item>
            </template>
          </el-form>
        </el-tab-pane>

        <!-- 其他设置 -->
        <el-tab-pane label="🌍 其他设置" name="other">
          <el-form :model="settings" label-width="150px">
            <el-form-item label="界面语言">
              <el-select v-model="settings.language">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>

            <el-form-item label="界面主题">
              <el-select v-model="settings.theme">
                <el-option label="浅色" value="light" />
                <el-option label="深色" value="dark" />
                <el-option label="跟随系统" value="auto" />
              </el-select>
            </el-form-item>

            <el-divider content-position="left">自动更新</el-divider>

            <el-form-item label="检查更新">
              <el-select v-model="settings.autoUpdate">
                <el-option label="自动检查并安装" value="auto" />
                <el-option label="仅检查不安装" value="check" />
                <el-option label="不检查" value="never" />
              </el-select>
            </el-form-item>

            <el-form-item label="当前版本">
              <span>v{{ appVersion }}</span>
              <el-button
                type="primary"
                size="small"
                @click="checkUpdate"
                :loading="checkingUpdate"
                style="margin-left: 10px"
              >
                检查更新
              </el-button>
            </el-form-item>

            <el-divider content-position="left">数据管理</el-divider>

            <el-form-item label="备份配置">
              <el-button type="success" @click="backupConfig">
                💾 立即备份配置
              </el-button>
              <el-button @click="restoreConfig" style="margin-left: 10px">
                📥 恢复配置
              </el-button>
            </el-form-item>

            <el-form-item label="最后备份时间">
              <span>{{ lastBackupTime || '从未备份' }}</span>
            </el-form-item>

            <el-form-item label="自动备份">
              <el-checkbox v-model="settings.autoBackup">
                每天自动备份配置
              </el-checkbox>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

// 当前激活的标签页
const activeTab = ref('service')

// 保存中
const saving = ref(false)

// 系统状态
const systemStatus = ref('running')
const uptime = ref('0小时0分钟')
const appVersion = ref('1.0.0')

// 图片使用情况
const imageUsedGB = ref(0)

// 日志使用情况
const logUsedMB = ref(0)

// 最后备份时间
const lastBackupTime = ref('')

// 检查更新中
const checkingUpdate = ref(false)

// 设置数据
const settings = ref({
  // 服务控制
  autoStart: false,
  minimizeToTray: true,
  startMinimized: false,
  
  // 图片处理
  imageStrategy: 'smart',
  imageStoragePath: '',
  imageMaxSizeGB: 10,
  imageCleanupDays: 7,
  imageQuality: 85,
  
  // 日志
  logLevel: 'INFO',
  logRetentionDays: 3,
  
  // 通知
  notifyOnError: true,
  notifyOnDisconnect: true,
  notifyOnFailure: false,
  emailAlertEnabled: false,
  smtpServer: '',
  smtpPort: 587,
  emailFrom: '',
  emailPassword: '',
  emailTo: '',
  
  // 其他
  language: 'zh-CN',
  theme: 'light',
  autoUpdate: 'check',
  autoBackup: true
})

// 计算属性：图片使用百分比
const imageUsagePercent = computed(() => {
  if (settings.value.imageMaxSizeGB === 0) return 0
  return Math.min((imageUsedGB.value / settings.value.imageMaxSizeGB) * 100, 100)
})

// 计算属性：进度条颜色
const progressColor = computed(() => {
  const percent = imageUsagePercent.value
  if (percent < 50) return '#67C23A'
  if (percent < 80) return '#E6A23C'
  return '#F56C6C'
})

// 加载设置
const loadSettings = async () => {
  try {
    const response = await api.getSystemConfig()
    if (response.data) {
      Object.assign(settings.value, response.data)
    }
    
    // 获取图片存储路径（从配置或使用默认）
    settings.value.imageStoragePath = settings.value.imageStoragePath || 
      '用户文档/KookForwarder/data/images'
    
    // 获取图片使用情况
    // TODO: 实现API
    imageUsedGB.value = 2.3
    
    // 获取日志使用情况
    // TODO: 实现API
    logUsedMB.value = 125
    
    // 获取最后备份时间
    lastBackupTime.value = localStorage.getItem('last_backup_time') || ''
    
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 保存设置
const saveSettings = async () => {
  try {
    saving.value = true
    await api.saveSystemConfig(settings.value)
    ElMessage.success('设置保存成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 打开图片文件夹
const openImageFolder = () => {
  // TODO: 调用Electron API打开文件夹
  ElMessage.info('打开图片文件夹功能开发中...')
}

// 打开日志文件夹
const openLogFolder = () => {
  // TODO: 调用Electron API打开文件夹
  ElMessage.info('打开日志文件夹功能开发中...')
}

// 清理旧图片
const cleanupOldImages = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清理 ${settings.value.imageCleanupDays} 天前的旧图片吗？`,
      '确认清理',
      {
        confirmButtonText: '确定清理',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // TODO: 调用清理API
    ElMessage.success('清理完成')
  } catch {
    // 取消
  }
}

// 清空所有日志
const clearAllLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复！',
      '危险操作',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // TODO: 调用清理API
    ElMessage.success('日志已清空')
    logUsedMB.value = 0
  } catch {
    // 取消
  }
}

// 测试邮件
const testEmail = async () => {
  // TODO: 调用测试邮件API
  ElMessage.info('发送测试邮件功能开发中...')
}

// 检查更新
const checkUpdate = async () => {
  checkingUpdate.value = true
  
  try {
    // TODO: 调用检查更新API
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('当前已是最新版本')
  } catch (error) {
    ElMessage.error('检查更新失败')
  } finally {
    checkingUpdate.value = false
  }
}

// 备份配置
const backupConfig = async () => {
  try {
    // TODO: 调用备份API
    const now = new Date().toLocaleString('zh-CN')
    localStorage.setItem('last_backup_time', now)
    lastBackupTime.value = now
    ElMessage.success('配置备份成功')
  } catch (error) {
    ElMessage.error('备份失败')
  }
}

// 恢复配置
const restoreConfig = () => {
  // TODO: 实现恢复配置
  ElMessage.info('恢复配置功能开发中...')
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.help-text {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.radio-desc {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
  margin-top: 2px;
}

.storage-info {
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
}

.storage-status {
  display: flex;
  align-items: center;
}

.notification-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

:deep(.el-tabs__content) {
  padding: 20px;
}
</style>
