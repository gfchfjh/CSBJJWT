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

        <!-- 外观主题 -->
        <el-tab-pane label="🎨 外观主题" name="theme">
          <el-form :model="settings" label-width="150px">
            <el-form-item label="主题模式">
              <el-radio-group v-model="settings.theme" @change="handleThemeChange">
                <el-radio label="light">
                  <div class="theme-option">
                    <el-icon><Sunny /></el-icon>
                    <span>浅色模式</span>
                  </div>
                </el-radio>
                <el-radio label="dark">
                  <div class="theme-option">
                    <el-icon><Moon /></el-icon>
                    <span>深色模式</span>
                  </div>
                </el-radio>
                <el-radio label="auto">
                  <div class="theme-option">
                    <el-icon><Monitor /></el-icon>
                    <span>跟随系统</span>
                  </div>
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="当前主题">
              <el-tag :type="isDark ? 'info' : 'primary'" size="large">
                {{ isDark ? '🌙 深色' : '☀️ 浅色' }}
              </el-tag>
            </el-form-item>

            <el-divider content-position="left">主题预览</el-divider>

            <div class="theme-preview">
              <el-card>
                <template #header>
                  <span>示例卡片</span>
                </template>
                <p>这是当前主题的预览效果</p>
                <el-button type="primary">主要按钮</el-button>
                <el-button>普通按钮</el-button>
              </el-card>
            </div>
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

        <!-- 消息同步设置 -->
        <el-tab-pane label="🔄 消息同步" name="sync">
          <el-form :model="settings" label-width="180px">
            <el-alert
              title="历史消息同步"
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            >
              <p>启动服务时，可以选择同步最近一段时间的历史消息。</p>
              <p style="margin-top: 10px; color: #E6A23C;">
                <strong>注意：</strong>同步时间过长可能导致大量消息重复转发，请谨慎设置。
              </p>
            </el-alert>

            <el-form-item label="启用历史消息同步">
              <el-switch v-model="settings.enableHistorySync" />
              <span class="help-text">启动服务时同步历史消息</span>
            </el-form-item>

            <template v-if="settings.enableHistorySync">
              <el-form-item label="同步时间范围">
                <el-input-number
                  v-model="settings.historySyncMinutes"
                  :min="1"
                  :max="1440"
                  :step="5"
                />
                <span style="margin-left: 10px">分钟</span>
                <div class="help-text">同步最近N分钟的历史消息（建议不超过60分钟）</div>
              </el-form-item>

              <el-form-item label="快捷选择">
                <el-radio-group v-model="settings.historySyncMinutes">
                  <el-radio :label="5">最近5分钟</el-radio>
                  <el-radio :label="10">最近10分钟</el-radio>
                  <el-radio :label="30">最近30分钟</el-radio>
                  <el-radio :label="60">最近1小时</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="仅同步已映射频道">
                <el-switch v-model="settings.historySyncMappedOnly" />
                <span class="help-text">仅同步已配置映射关系的频道</span>
              </el-form-item>
            </template>

            <el-divider content-position="left">消息去重</el-divider>

            <el-form-item label="去重缓存大小">
              <el-input-number
                v-model="settings.dedupCacheSize"
                :min="1000"
                :max="100000"
                :step="1000"
              />
              <span style="margin-left: 10px">条</span>
              <div class="help-text">内存中保存的消息ID数量（越大越能避免重复）</div>
            </el-form-item>

            <el-form-item label="Redis去重保留时间">
              <el-input-number
                v-model="settings.dedupRedisDays"
                :min="1"
                :max="30"
              />
              <span style="margin-left: 10px">天</span>
              <div class="help-text">Redis中保存的消息ID过期时间</div>
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
              <el-alert
                title="邮件告警配置说明"
                type="info"
                :closable="false"
                style="margin-bottom: 20px"
              >
                <p><strong>常用SMTP配置：</strong></p>
                <ul style="margin: 10px 0; padding-left: 20px;">
                  <li>Gmail: smtp.gmail.com, 端口465 (需要应用专用密码)</li>
                  <li>QQ邮箱: smtp.qq.com, 端口465 (需要授权码)</li>
                  <li>163邮箱: smtp.163.com, 端口465 (需要授权码)</li>
                  <li>Outlook: smtp-mail.outlook.com, 端口587</li>
                </ul>
              </el-alert>

              <el-form-item label="SMTP服务器" required>
                <el-input
                  v-model="settings.smtpServer"
                  placeholder="例如：smtp.gmail.com"
                >
                  <template #prepend>
                    <el-icon><Message /></el-icon>
                  </template>
                </el-input>
                <span class="help-text">邮件服务器地址</span>
              </el-form-item>

              <el-form-item label="SMTP端口" required>
                <el-input-number
                  v-model="settings.smtpPort"
                  :min="1"
                  :max="65535"
                  placeholder="465"
                  style="width: 150px"
                />
                <el-radio-group v-model="settings.smtpPort" style="margin-left: 15px">
                  <el-radio :label="465">465 (SSL)</el-radio>
                  <el-radio :label="587">587 (TLS)</el-radio>
                  <el-radio :label="25">25 (普通)</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="发件邮箱" required>
                <el-input
                  v-model="settings.emailFrom"
                  placeholder="your-email@gmail.com"
                >
                  <template #prepend>📧</template>
                </el-input>
                <span class="help-text">发送告警邮件的邮箱地址</span>
              </el-form-item>

              <el-form-item label="邮箱密码/授权码" required>
                <el-input
                  v-model="settings.emailPassword"
                  type="password"
                  show-password
                  placeholder="邮箱密码或SMTP授权码"
                >
                  <template #prepend>🔑</template>
                </el-input>
                <span class="help-text">
                  Gmail需要"应用专用密码"，QQ/163邮箱需要"授权码"
                  <el-link
                    type="primary"
                    href="https://support.google.com/accounts/answer/185833"
                    target="_blank"
                    style="margin-left: 5px"
                  >
                    如何获取？
                  </el-link>
                </span>
              </el-form-item>

              <el-form-item label="收件邮箱" required>
                <el-input
                  v-model="settings.emailTo"
                  placeholder="admin@example.com"
                >
                  <template #prepend>📬</template>
                </el-input>
                <span class="help-text">接收告警邮件的邮箱地址（可与发件邮箱相同）</span>
              </el-form-item>

              <el-divider content-position="left">告警触发条件</el-divider>

              <el-form-item label="触发条件">
                <el-checkbox-group v-model="settings.emailAlertTriggers">
                  <el-checkbox label="service_error">
                    <strong>服务异常</strong>
                    <span class="help-text">- 后端服务崩溃或无法启动</span>
                  </el-checkbox>
                  <el-checkbox label="account_offline">
                    <strong>账号掉线</strong>
                    <span class="help-text">- KOOK账号连接断开超过5分钟</span>
                  </el-checkbox>
                  <el-checkbox label="forward_failed_batch">
                    <strong>批量转发失败</strong>
                    <span class="help-text">- 1小时内累计10次以上转发失败</span>
                  </el-checkbox>
                  <el-checkbox label="disk_full">
                    <strong>磁盘空间不足</strong>
                    <span class="help-text">- 图床或日志空间使用超过90%</span>
                  </el-checkbox>
                  <el-checkbox label="redis_error">
                    <strong>Redis连接失败</strong>
                    <span class="help-text">- 消息队列服务异常</span>
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item label="告警频率限制">
                <el-input-number
                  v-model="settings.emailAlertInterval"
                  :min="5"
                  :max="1440"
                  :step="5"
                  style="width: 150px"
                />
                <span> 分钟内同类告警仅发送一次</span>
                <span class="help-text" style="display: block; margin-top: 5px">
                  防止告警邮件过多，建议设置为30-60分钟
                </span>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="testEmail" :loading="testingEmail">
                  <el-icon><Promotion /></el-icon>
                  发送测试邮件
                </el-button>
                <span class="help-text" style="margin-left: 10px">
                  点击后将发送一封测试邮件到收件邮箱
                </span>
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
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { useTheme } from '@/composables/useTheme'

// 主题管理
const { currentTheme, isDark, setTheme } = useTheme()

// 处理主题变化
const handleThemeChange = (theme) => {
  setTheme(theme)
  ElMessage.success(`已切换到${theme === 'light' ? '浅色' : theme === 'dark' ? '深色' : '自动'}模式`)
}

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

// 测试邮件中
const testingEmail = ref(false)

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
  
  // 消息同步（新增）
  enableHistorySync: false,
  historySyncMinutes: 10,
  historySyncMappedOnly: true,
  dedupCacheSize: 10000,
  dedupRedisDays: 7,
  
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
  emailAlertTriggers: ['service_error', 'account_offline', 'disk_full'],
  emailAlertInterval: 30,
  
  // 其他
  language: 'zh-CN',
  theme: currentTheme.value || 'auto',  // 从主题管理器获取当前主题
  autoUpdate: 'check',
  autoBackup: true
})

// 监听主题变化并应用
watch(() => settings.value.theme, (newTheme) => {
  setTheme(newTheme)
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
    if (response.success && response.data) {
      Object.assign(settings.value, response.data)
    }
    
    // 加载保存的主题设置
    settings.value.theme = currentTheme.value
    
    // 获取图片存储路径（从配置或使用默认）
    settings.value.imageStoragePath = settings.value.imageStoragePath || 
      '用户文档/KookForwarder/data/images'
    
    // 获取存储使用情况
    await loadStorageUsage()
    
    // 获取最后备份时间
    lastBackupTime.value = localStorage.getItem('last_backup_time') || ''
    
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败：' + (error.response?.data?.detail || error.message))
  }
}

// 加载存储使用情况
const loadStorageUsage = async () => {
  try {
    const response = await api.getStorageUsage()
    if (response.success && response.data) {
      imageUsedGB.value = response.data.image.size_gb || 0
      logUsedMB.value = response.data.log.size_mb || 0
      // 更新路径
      if (response.data.image.path) {
        settings.value.imageStoragePath = response.data.image.path
      }
    }
  } catch (error) {
    console.error('获取存储使用情况失败:', error)
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
const openImageFolder = async () => {
  try {
    // 先获取路径
    const response = await api.getSystemPaths()
    if (response.success && response.data.image_storage) {
      const path = response.data.image_storage
      
      // 调用Electron API打开文件夹
      if (window.electronAPI && window.electronAPI.openPath) {
        await window.electronAPI.openPath(path)
      } else {
        // Web环境降级处理
        ElMessage.info(`图片文件夹路径：${path}`)
        // 复制路径到剪贴板
        if (navigator.clipboard) {
          await navigator.clipboard.writeText(path)
          ElMessage.success('路径已复制到剪贴板')
        }
      }
    }
  } catch (error) {
    ElMessage.error('打开文件夹失败：' + (error.response?.data?.detail || error.message))
  }
}

// 打开日志文件夹
const openLogFolder = async () => {
  try {
    // 先获取路径
    const response = await api.getSystemPaths()
    if (response.success && response.data.log_dir) {
      const path = response.data.log_dir
      
      // 调用Electron API打开文件夹
      if (window.electronAPI && window.electronAPI.openPath) {
        await window.electronAPI.openPath(path)
      } else {
        // Web环境降级处理
        ElMessage.info(`日志文件夹路径：${path}`)
        // 复制路径到剪贴板
        if (navigator.clipboard) {
          await navigator.clipboard.writeText(path)
          ElMessage.success('路径已复制到剪贴板')
        }
      }
    }
  } catch (error) {
    ElMessage.error('打开文件夹失败：' + (error.response?.data?.detail || error.message))
  }
}

// 清理旧图片
const cleanupOldImages = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清理 ${settings.value.imageCleanupDays} 天前的旧图片吗？此操作不可恢复！`,
      '确认清理',
      {
        confirmButtonText: '确定清理',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 调用清理API
    const response = await api.cleanupImages(settings.value.imageCleanupDays)
    if (response.success) {
      ElMessage.success(`清理完成，删除了 ${response.count} 个文件，释放 ${response.size_mb} MB 空间`)
      // 刷新存储使用情况
      await loadStorageUsage()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清理失败：' + (error.response?.data?.detail || error.message))
    }
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
        type: 'error',
        dangerouslyUseHTMLString: true,
        message: '<p>⚠️ <strong>此操作将删除所有日志文件！</strong></p><p>日志文件用于故障排查，删除后将无法追溯历史问题。</p>'
      }
    )
    
    // 调用清理API
    const response = await api.cleanupLogs()
    if (response.success) {
      ElMessage.success(`日志已清空，删除了 ${response.count} 个文件，释放 ${response.size_mb} MB 空间`)
      logUsedMB.value = 0
      // 刷新存储使用情况
      await loadStorageUsage()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空日志失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

// 测试邮件
const testEmail = async () => {
  // 验证必填字段
  if (!settings.value.smtpServer || !settings.value.emailFrom || 
      !settings.value.emailPassword || !settings.value.emailTo) {
    ElMessage.warning('请先填写完整的邮件配置信息')
    return
  }

  try {
    testingEmail.value = true
    
    // 先保存当前的邮件配置
    await saveSettings()
    
    ElMessage.info('正在发送测试邮件，请稍候...')
    
    // 发送测试邮件
    const response = await api.testEmail({
      smtp_host: settings.value.smtpServer,
      smtp_port: settings.value.smtpPort,
      smtp_user: settings.value.emailFrom,
      smtp_password: settings.value.emailPassword,
      recipient: settings.value.emailTo
    })
    
    if (response.success) {
      ElMessageBox.alert(
        '测试邮件已成功发送！请检查您的收件箱（包括垃圾邮件箱）。<br/><br/>' +
        `<strong>收件人：</strong>${settings.value.emailTo}<br/>` +
        `<strong>主题：</strong>KOOK消息转发系统 - 测试邮件<br/><br/>` +
        '如果未收到邮件，请检查：<br/>' +
        '1. SMTP服务器地址和端口是否正确<br/>' +
        '2. 邮箱密码/授权码是否正确<br/>' +
        '3. 邮箱是否开启了SMTP服务',
        '测试成功',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '知道了',
          type: 'success'
        }
      )
    } else {
      ElMessage.error('发送失败：' + (response.message || '未知错误'))
    }
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || '未知错误'
    ElMessageBox.alert(
      `<strong>发送测试邮件失败</strong><br/><br/>` +
      `<strong>错误信息：</strong>${errorMsg}<br/><br/>` +
      `<strong>可能的原因：</strong><br/>` +
      `1. SMTP服务器连接失败（请检查服务器地址和端口）<br/>` +
      `2. 认证失败（请检查邮箱和密码/授权码）<br/>` +
      `3. 邮箱未开启SMTP服务<br/>` +
      `4. 网络连接问题`,
      '发送失败',
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '知道了',
        type: 'error'
      }
    )
  } finally {
    testingEmail.value = false
  }
}

// 检查更新
const checkUpdate = async () => {
  checkingUpdate.value = true
  
  try {
    const response = await api.checkForUpdates()
    if (response.has_update) {
      ElMessageBox.confirm(
        `发现新版本 v${response.latest_version}！<br/><br/>` +
        `<strong>更新内容：</strong><br/>${response.release_notes || '查看完整更新日志'}`,
        '发现新版本',
        {
          confirmButtonText: '立即更新',
          cancelButtonText: '稍后提醒',
          type: 'success',
          dangerouslyUseHTMLString: true
        }
      ).then(() => {
        // 打开下载页面或触发自动更新
        if (response.download_url) {
          window.open(response.download_url, '_blank')
        }
      })
    } else {
      ElMessage.success(`当前已是最新版本 v${appVersion.value}`)
    }
  } catch (error) {
    console.error('检查更新失败:', error)
    ElMessage.warning('检查更新失败，请稍后重试')
  } finally {
    checkingUpdate.value = false
  }
}

// 备份配置
const backupConfig = async () => {
  try {
    const response = await api.backupConfig()
    if (response.success) {
      const now = new Date().toLocaleString('zh-CN')
      localStorage.setItem('last_backup_time', now)
      lastBackupTime.value = now
      
      // 如果返回了备份文件，触发下载
      if (response.backup_file) {
        ElMessage.success('配置备份成功，备份文件：' + response.backup_file)
      } else {
        ElMessage.success('配置备份成功')
      }
    }
  } catch (error) {
    ElMessage.error('备份失败：' + (error.response?.data?.detail || error.message))
  }
}

// 恢复配置
const restoreConfig = () => {
  // 创建文件选择输入框
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json,.zip'
  
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post('/api/backup/restore', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      ElMessage.success('配置恢复成功，将在3秒后重启应用')
      
      // 3秒后重启应用
      setTimeout(() => {
        if (window.electronAPI && window.electronAPI.relaunch) {
          window.electronAPI.relaunch()
        } else {
          window.location.reload()
        }
      }, 3000)
    } catch (error) {
      ElMessage.error('恢复配置失败：' + (error.response?.data?.detail || error.message))
    }
  }
  
  input.click()
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
