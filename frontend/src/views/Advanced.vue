<template>
  <div class="advanced-view">
    <el-alert
      title="高级功能"
      type="info"
      :closable="false"
      style="margin-bottom: 20px"
    >
      <p>这些功能面向技术用户。如果您不熟悉相关技术，请谨慎修改。</p>
      <p style="margin-top: 10px">
        <el-button type="primary" size="small" @click="goToSelectors">
          🔍 配置选择器
        </el-button>
        <span style="margin-left: 10px; color: #909399;">
          （用于适配KOOK网页结构变化）
        </span>
      </p>
    </el-alert>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- 健康检查 -->
      <el-tab-pane label="🏥 健康检查" name="health">
        <div class="health-section">
          <div class="section-header">
            <h3>系统健康状态</h3>
            <el-button
              type="primary"
              :loading="checking"
              @click="performHealthCheck"
            >
              <el-icon><Refresh /></el-icon>
              立即检查
            </el-button>
          </div>

          <el-card v-if="healthStatus" class="health-card">
            <template #header>
              <div class="card-header">
                <span>总体状态</span>
                <el-tag :type="getStatusType(healthStatus.overall_status)">
                  {{ getStatusText(healthStatus.overall_status) }}
                </el-tag>
              </div>
            </template>

            <div class="health-components">
              <!-- Redis -->
              <div class="component-item">
                <div class="component-name">
                  <el-icon><Coin /></el-icon>
                  Redis
                </div>
                <div class="component-status">
                  <el-tag :type="getStatusType(healthStatus.components.redis?.status)">
                    {{ healthStatus.components.redis?.message }}
                  </el-tag>
                </div>
              </div>

              <!-- Worker -->
              <div class="component-item">
                <div class="component-name">
                  <el-icon><Tools /></el-icon>
                  消息Worker
                </div>
                <div class="component-status">
                  <el-tag :type="getStatusType(healthStatus.components.worker?.status)">
                    {{ healthStatus.components.worker?.message }}
                  </el-tag>
                </div>
              </div>

              <!-- Scrapers -->
              <div class="component-item">
                <div class="component-name">
                  <el-icon><View /></el-icon>
                  抓取器
                </div>
                <div class="component-status">
                  <el-tag :type="getStatusType(healthStatus.components.scrapers?.status)">
                    {{ healthStatus.components.scrapers?.message }}
                  </el-tag>
                </div>
              </div>

              <!-- Storage -->
              <div class="component-item">
                <div class="component-name">
                  <el-icon><FolderOpened /></el-icon>
                  存储空间
                </div>
                <div class="component-status">
                  <el-tag :type="getStatusType(healthStatus.components.storage?.status)">
                    {{ healthStatus.components.storage?.message }}
                  </el-tag>
                  <el-progress
                    v-if="healthStatus.components.storage?.usage_percent"
                    :percentage="healthStatus.components.storage.usage_percent"
                    :color="getProgressColor(healthStatus.components.storage.usage_percent)"
                    style="margin-top: 10px;"
                  />
                </div>
              </div>

              <!-- Bots -->
              <div v-if="healthStatus.components.bots?.length" class="component-item">
                <div class="component-name">
                  <el-icon><Robot /></el-icon>
                  Bot状态
                </div>
                <div class="bot-list">
                  <div
                    v-for="bot in healthStatus.components.bots"
                    :key="bot.bot_id"
                    class="bot-item"
                  >
                    <span>{{ bot.bot_name }} ({{ bot.platform }})</span>
                    <el-tag :type="getStatusType(bot.status)" size="small">
                      {{ bot.message }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <div class="health-footer">
              <span>最后检查: {{ healthStatus.timestamp ? new Date(healthStatus.timestamp).toLocaleString() : '未知' }}</span>
            </div>
          </el-card>

          <el-empty v-else description="暂无健康检查数据，点击上方按钮开始检查" />
        </div>
      </el-tab-pane>

      <!-- 更新检查 -->
      <el-tab-pane label="🔄 更新检查" name="updates">
        <div class="updates-section">
          <div class="section-header">
            <h3>检查更新</h3>
            <el-button
              type="primary"
              :loading="checkingUpdate"
              @click="checkUpdates"
            >
              <el-icon><Refresh /></el-icon>
              检查更新
            </el-button>
          </div>

          <el-card v-if="updateInfo" class="update-card">
            <div v-if="updateInfo.has_update" class="has-update">
              <el-result
                icon="success"
                title="发现新版本！"
                :sub-title="`v${updateInfo.latest_version} 可用`"
              >
                <template #extra>
                  <div class="update-info">
                    <p><strong>当前版本:</strong> v{{ updateInfo.current_version }}</p>
                    <p><strong>最新版本:</strong> v{{ updateInfo.latest_version }}</p>
                    <p><strong>发布时间:</strong> {{ new Date(updateInfo.published_at).toLocaleString() }}</p>
                    
                    <el-divider />
                    
                    <h4>更新内容</h4>
                    <div class="release-notes" v-html="formatMarkdown(updateInfo.release_notes)"></div>
                    
                    <el-divider />
                    
                    <h4>下载链接</h4>
                    <div class="download-links">
                      <el-button
                        v-if="updateInfo.downloads.windows"
                        type="primary"
                        @click="openDownloadLink(updateInfo.downloads.windows)"
                      >
                        <el-icon><Windows /></el-icon>
                        Windows
                      </el-button>
                      <el-button
                        v-if="updateInfo.downloads.macos"
                        type="primary"
                        @click="openDownloadLink(updateInfo.downloads.macos)"
                      >
                        <el-icon><Monitor /></el-icon>
                        macOS
                      </el-button>
                      <el-button
                        v-if="updateInfo.downloads.linux"
                        type="primary"
                        @click="openDownloadLink(updateInfo.downloads.linux)"
                      >
                        <el-icon><Monitor /></el-icon>
                        Linux
                      </el-button>
                    </div>
                    
                    <el-button
                      link
                      type="primary"
                      @click="openDownloadLink(updateInfo.release_url)"
                    >
                      在GitHub上查看完整发布说明 →
                    </el-button>
                  </div>
                </template>
              </el-result>
            </div>

            <div v-else class="no-update">
              <el-result
                icon="success"
                title="已是最新版本"
                :sub-title="`当前版本 v${updateInfo.current_version} 是最新版本`"
              >
                <template #extra>
                  <p>最后检查: {{ new Date(updateInfo.checked_at).toLocaleString() }}</p>
                </template>
              </el-result>
            </div>
          </el-card>

          <el-empty v-else description="暂无更新信息，点击上方按钮检查更新" />
        </div>
      </el-tab-pane>

      <!-- 选择器配置 -->
      <el-tab-pane label="🎯 选择器配置" name="selectors">
        <div class="selectors-section">
          <el-alert
            title="选择器配置说明"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            <p>选择器用于在KOOK页面上定位元素。如果KOOK页面更新导致无法获取服务器或频道，可能需要更新选择器配置。</p>
            <p><strong>警告：</strong>不正确的选择器配置可能导致程序无法正常工作，请谨慎修改。</p>
          </el-alert>

          <div class="section-header">
            <h3>选择器配置管理</h3>
            <div>
              <el-button @click="reloadConfig">
                <el-icon><Refresh /></el-icon>
                重新加载
              </el-button>
              <el-button @click="exportConfig">
                <el-icon><Download /></el-icon>
                导出配置
              </el-button>
              <el-button @click="showImportDialog = true">
                <el-icon><Upload /></el-icon>
                导入配置
              </el-button>
            </div>
          </div>

          <el-card v-if="selectorConfig" class="selector-card">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="配置版本">
                {{ selectorConfig.version }}
              </el-descriptions-item>
              <el-descriptions-item label="最后更新">
                {{ selectorConfig.last_updated }}
              </el-descriptions-item>
              <el-descriptions-item label="配置文件">
                {{ selectorFileInfo?.path || '未知' }}
              </el-descriptions-item>
            </el-descriptions>

            <el-divider />

            <el-collapse v-model="activeCategories">
              <el-collapse-item
                v-for="(value, key) in getSelectorCategories()"
                :key="key"
                :title="`${getCategoryLabel(key)} (${Array.isArray(value) ? value.length : Object.keys(value).length})`"
                :name="key"
              >
                <div v-if="Array.isArray(value)" class="selector-list">
                  <el-tag
                    v-for="(selector, index) in value"
                    :key="index"
                    closable
                    @close="removeSelector(key, selector)"
                    style="margin: 5px;"
                  >
                    {{ selector }}
                  </el-tag>
                  <el-button size="small" @click="showAddSelectorDialog(key)">
                    <el-icon><Plus /></el-icon>
                    添加
                  </el-button>
                </div>
                <div v-else class="selector-dict">
                  <pre>{{ JSON.stringify(value, null, 2) }}</pre>
                </div>
              </el-collapse-item>
            </el-collapse>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 导入配置对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="导入选择器配置"
      width="500px"
    >
      <el-form>
        <el-form-item label="配置格式">
          <el-radio-group v-model="importFormat">
            <el-radio label="json">JSON</el-radio>
            <el-radio label="yaml">YAML</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="配置内容">
          <el-input
            v-model="importConfig"
            type="textarea"
            :rows="10"
            placeholder="粘贴配置内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importConfig">导入</el-button>
      </template>
    </el-dialog>

    <!-- 添加选择器对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加选择器"
      width="400px"
    >
      <el-form>
        <el-form-item label="选择器">
          <el-input
            v-model="newSelector"
            placeholder="例如: .class-name 或 #element-id"
          />
        </el-form-item>
        <el-form-item label="插入位置">
          <el-input-number v-model="newSelectorPosition" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addSelectorConfirm">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const activeTab = ref('health')
const checking = ref(false)
const checkingUpdate = ref(false)
const healthStatus = ref(null)
const updateInfo = ref(null)
const selectorConfig = ref(null)
const selectorFileInfo = ref(null)
const activeCategories = ref([])

const showImportDialog = ref(false)
const importFormat = ref('json')
const importConfigContent = ref('')

const showAddDialog = ref(false)
const newSelector = ref('')
const newSelectorPosition = ref(0)
const currentCategory = ref('')

onMounted(async () => {
  await loadHealthStatus()
  await loadSelectorConfig()
})

// 健康检查相关
const performHealthCheck = async () => {
  checking.value = true
  try {
    const result = await api.performHealthCheck()
    if (result.success) {
      healthStatus.value = result.data
      ElMessage.success('健康检查完成')
    }
  } catch (error) {
    ElMessage.error('健康检查失败: ' + error.message)
  } finally {
    checking.value = false
  }
}

const loadHealthStatus = async () => {
  try {
    const result = await api.getHealthStatus()
    if (result.success) {
      healthStatus.value = result.data
    }
  } catch (error) {
    console.error('加载健康状态失败:', error)
  }
}

const getStatusType = (status) => {
  const statusMap = {
    'healthy': 'success',
    'warning': 'warning',
    'unhealthy': 'danger',
    'critical': 'danger',
    'error': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'healthy': '健康',
    'warning': '警告',
    'unhealthy': '异常',
    'critical': '严重',
    'error': '错误'
  }
  return textMap[status] || '未知'
}

const getProgressColor = (percent) => {
  if (percent >= 90) return '#f56c6c'
  if (percent >= 80) return '#e6a23c'
  return '#67c23a'
}

// 更新检查相关
const checkUpdates = async () => {
  checkingUpdate.value = true
  try {
    const result = await api.checkForUpdates()
    if (result.success) {
      updateInfo.value = result.data
      if (result.data.has_update) {
        ElMessage.success('发现新版本!')
      } else {
        ElMessage.info('当前已是最新版本')
      }
    }
  } catch (error) {
    ElMessage.error('检查更新失败: ' + error.message)
  } finally {
    checkingUpdate.value = false
  }
}

const formatMarkdown = (text) => {
  // 简单的Markdown转HTML
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const openDownloadLink = (url) => {
  window.open(url, '_blank')
}

// 选择器配置相关
const loadSelectorConfig = async () => {
  try {
    const result = await api.getSelectorConfig()
    if (result.success) {
      selectorConfig.value = result.data
    }
    
    const fileInfo = await api.getSelectorFileInfo()
    if (fileInfo.success) {
      selectorFileInfo.value = fileInfo.data
    }
  } catch (error) {
    console.error('加载选择器配置失败:', error)
  }
}

const getSelectorCategories = () => {
  if (!selectorConfig.value) return {}
  
  const { version, last_updated, description, ...categories } = selectorConfig.value
  return categories
}

const getCategoryLabel = (key) => {
  const labels = {
    'server_container': '服务器列表容器',
    'server_item': '服务器项',
    'server_name': '服务器名称',
    'channel_container': '频道列表容器',
    'channel_item': '频道项',
    'channel_name': '频道名称',
    'login': '登录表单',
    'message': '消息相关'
  }
  return labels[key] || key
}

const reloadConfig = async () => {
  try {
    const result = await api.reloadSelectorConfig()
    if (result.success) {
      await loadSelectorConfig()
      ElMessage.success('配置已重新加载')
    }
  } catch (error) {
    ElMessage.error('重新加载失败: ' + error.message)
  }
}

const exportConfig = async () => {
  try {
    const result = await api.exportSelectorConfig()
    if (result.success) {
      // 下载配置文件
      const blob = new Blob([result.data], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'selectors.json'
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('配置已导出')
    }
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

const importConfigConfirm = async () => {
  try {
    const result = await api.importSelectorConfig({
      config_str: importConfigContent.value,
      format: importFormat.value
    })
    
    if (result.success) {
      await loadSelectorConfig()
      showImportDialog.value = false
      ElMessage.success('配置已导入')
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + error.message)
  }
}

const showAddSelectorDialog = (category) => {
  currentCategory.value = category
  newSelector.value = ''
  newSelectorPosition.value = 0
  showAddDialog.value = true
}

const addSelectorConfirm = async () => {
  if (!newSelector.value) {
    ElMessage.warning('请输入选择器')
    return
  }
  
  try {
    const result = await api.addSelector({
      category: currentCategory.value,
      selector: newSelector.value,
      position: newSelectorPosition.value
    })
    
    if (result.success) {
      await loadSelectorConfig()
      showAddDialog.value = false
      ElMessage.success('选择器已添加')
    }
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  }
}

const removeSelector = async (category, selector) => {
  try {
    await ElMessageBox.confirm('确定要删除此选择器吗？', '确认删除', {
      type: 'warning'
    })
    
    const result = await api.removeSelector({
      category,
      selector
    })
    
    if (result.success) {
      await loadSelectorConfig()
      ElMessage.success('选择器已删除')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}
</script>

<style scoped>
.advanced-view {
  height: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.health-section, .updates-section, .selectors-section {
  padding: 20px;
}

.health-card, .update-card, .selector-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.health-components {
  margin-top: 20px;
}

.component-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.component-item:last-child {
  border-bottom: none;
}

.component-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.component-status {
  flex: 1;
  text-align: right;
}

.bot-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bot-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.health-footer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  color: #909399;
  font-size: 14px;
}

.update-info {
  text-align: left;
}

.release-notes {
  max-height: 300px;
  overflow-y: auto;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  white-space: pre-wrap;
}

.download-links {
  display: flex;
  gap: 10px;
  margin: 15px 0;
}

.selector-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.selector-dict {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
