<template>
  <div class="mapping-view">
    <!-- 视图切换 -->
    <div class="view-switcher">
      <el-radio-group v-model="viewMode" size="large">
        <el-radio-button value="visual">
          <el-icon><Connection /></el-icon>
          可视化编辑器
        </el-radio-button>
        <el-radio-button value="table">
          <el-icon><List /></el-icon>
          表格模式
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 可视化编辑器 -->
    <MappingVisualEditor v-if="viewMode === 'visual'" />

    <!-- 传统表格模式 -->
    <el-card v-else>
      <template #header>
        <div class="card-header">
          <span>🔀 频道映射配置</span>
          <div>
            <el-button @click="exportMappings">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
            <el-button @click="showImportDialog = true">
              <el-icon><Upload /></el-icon>
              导入
            </el-button>
            <el-button @click="showTemplateDialog = true">
              <el-icon><Document /></el-icon>
              使用模板
            </el-button>
            <el-button type="success" @click="showSmartMappingDialog = true">
              <el-icon><MagicStick /></el-icon>
              智能映射
            </el-button>
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              添加映射
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- v1.12.0+ 优化：更醒目的快捷操作提示 -->
      <el-row :gutter="20" style="margin-bottom: 20px" v-if="mappings.length === 0">
        <el-col :span="24">
          <el-alert
            title="🎉 欢迎使用频道映射配置"
            type="success"
            :closable="false"
            show-icon
          >
            <template #default>
              <p style="margin-bottom: 15px">
                <strong>频道映射</strong>用于将KOOK频道的消息自动转发到Discord、Telegram或飞书。
                您还没有配置任何映射，可以选择以下方式快速开始：
              </p>
              <el-row :gutter="15">
                <el-col :span="8">
                  <el-card shadow="hover" class="feature-card" @click="showSmartMappingDialog = true">
                    <div class="feature-content">
                      <div class="feature-icon">🧙</div>
                      <h3>智能映射</h3>
                      <p>自动匹配同名频道</p>
                      <el-tag type="success" size="small">推荐</el-tag>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="feature-card" @click="showTemplateDialog = true">
                    <div class="feature-content">
                      <div class="feature-icon">📋</div>
                      <h3>使用模板</h3>
                      <p>预置配置，一键导入</p>
                      <el-tag type="primary" size="small">快速</el-tag>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="feature-card" @click="showAddDialog = true">
                    <div class="feature-content">
                      <div class="feature-icon">✏️</div>
                      <h3>手动配置</h3>
                      <p>逐个添加映射</p>
                      <el-tag type="info" size="small">精确</el-tag>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </template>
          </el-alert>
        </el-col>
      </el-row>
      
      <!-- 已有映射时的常规提示 -->
      <el-alert
        v-else
        title="💡 提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          <p>频道映射用于将KOOK频道的消息转发到目标平台。一个KOOK频道可以同时转发到多个目标。</p>
          <div style="margin-top: 10px">
            <el-button size="small" type="primary" @click="showSmartMappingDialog = true">
              <el-icon><MagicStick /></el-icon>
              使用智能映射快速添加
            </el-button>
            <el-button size="small" type="success" @click="showTemplateDialog = true">
              <el-icon><Document /></el-icon>
              从模板导入
            </el-button>
          </div>
        </template>
      </el-alert>
      
      <el-table :data="mappings" border style="width: 100%">
        <el-table-column prop="kook_channel_name" label="KOOK频道" width="200" />
        <el-table-column prop="target_platform" label="目标平台" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.target_platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_channel_id" label="目标频道ID" />
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="deleteMapping(row.id)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- ✅ P1-2优化: 智能映射对话框（完全重构） -->
    <el-dialog
      v-model="showSmartMappingDialog"
      title="🪄 智能频道映射"
      width="90%"
      fullscreen
      :close-on-click-modal="false"
    >
      <SmartMappingWizard
        @finish="handleSmartMappingFinish"
        @cancel="showSmartMappingDialog = false"
      />
    </el-dialog>

    <!-- 添加映射对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加频道映射"
      width="600px"
    >
      <el-form :model="mappingForm" label-width="120px">
        <el-form-item label="KOOK服务器ID">
          <el-input v-model="mappingForm.kook_server_id" placeholder="服务器ID" />
        </el-form-item>
        
        <el-form-item label="KOOK频道ID">
          <el-input v-model="mappingForm.kook_channel_id" placeholder="频道ID" />
        </el-form-item>
        
        <el-form-item label="频道名称">
          <el-input v-model="mappingForm.kook_channel_name" placeholder="用于显示的名称" />
        </el-form-item>
        
        <el-form-item label="目标平台">
          <el-select v-model="mappingForm.target_platform" placeholder="请选择">
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标机器人">
          <el-select v-model="mappingForm.target_bot_id" placeholder="请选择">
            <el-option
              v-for="bot in targetBots"
              :key="bot.id"
              :label="bot.name"
              :value="bot.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标频道ID">
          <el-input v-model="mappingForm.target_channel_id" placeholder="目标频道/群组ID" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addMapping">确定</el-button>
      </template>
    </el-dialog>

    <!-- 模板选择对话框 v1.11.0新增 -->
    <el-dialog
      v-model="showTemplateDialog"
      title="📄 使用映射模板"
      width="700px"
    >
      <el-alert
        title="模板说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p style="margin: 0 0 10px 0;">选择一个预置模板快速创建频道映射配置。模板将根据你已配置的机器人自动调整。</p>
        <p style="margin: 0; color: #E6A23C;">⚠️ 应用模板将替换当前所有映射配置</p>
      </el-alert>

      <el-row :gutter="20">
        <!-- 游戏公告模板 -->
        <el-col :span="8">
          <el-card 
            shadow="hover" 
            class="template-card" 
            :class="{ 'selected': selectedTemplate === 'gaming' }"
            @click="selectedTemplate = 'gaming'"
          >
            <div class="template-header">
              <el-icon size="32" color="#409EFF"><Tickets /></el-icon>
              <h3>游戏公告模板</h3>
            </div>
            <div class="template-desc">
              <p>适用场景：游戏公会、游戏社区</p>
              <p><strong>包含频道：</strong></p>
              <ul>
                <li>📢 公告频道</li>
                <li>🎉 活动频道</li>
                <li>📝 更新日志</li>
                <li>❓ 常见问题</li>
              </ul>
            </div>
          </el-card>
        </el-col>

        <!-- 社区管理模板 -->
        <el-col :span="8">
          <el-card 
            shadow="hover" 
            class="template-card"
            :class="{ 'selected': selectedTemplate === 'community' }"
            @click="selectedTemplate = 'community'"
          >
            <div class="template-header">
              <el-icon size="32" color="#67C23A"><User /></el-icon>
              <h3>社区管理模板</h3>
            </div>
            <div class="template-desc">
              <p>适用场景：社区管理、运营团队</p>
              <p><strong>包含频道：</strong></p>
              <ul>
                <li>👮 管理员频道</li>
                <li>💬 用户反馈</li>
                <li>🚨 举报处理</li>
                <li>📊 数据统计</li>
              </ul>
            </div>
          </el-card>
        </el-col>

        <!-- 全镜像模板 -->
        <el-col :span="8">
          <el-card 
            shadow="hover" 
            class="template-card"
            :class="{ 'selected': selectedTemplate === 'mirror' }"
            @click="selectedTemplate = 'mirror'"
          >
            <div class="template-header">
              <el-icon size="32" color="#F56C6C"><Connection /></el-icon>
              <h3>跨平台镜像模板</h3>
            </div>
            <div class="template-desc">
              <p>适用场景：多平台同步、备份</p>
              <p><strong>包含频道：</strong></p>
              <ul>
                <li>🔄 全频道镜像</li>
                <li>📤 自动同步</li>
                <li>💾 完整备份</li>
                <li>🌐 多平台覆盖</li>
              </ul>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <div style="margin-top: 20px">
        <el-alert
          v-if="selectedTemplate"
          :title="`已选择：${getTemplateName(selectedTemplate)}`"
          type="success"
          :closable="false"
        />
      </div>

      <template #footer>
        <el-button @click="showTemplateDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          :disabled="!selectedTemplate"
          :loading="applyingTemplate"
          @click="applyTemplate"
        >
          应用模板
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入映射对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="📥 导入频道映射"
      width="600px"
    >
      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <ul style="margin: 0; padding-left: 20px;">
          <li>支持导入之前导出的JSON文件</li>
          <li>可选择替换现有映射或追加到现有映射</li>
          <li>导入前请确保对应的机器人已配置</li>
        </ul>
      </el-alert>

      <el-form label-width="120px">
        <el-form-item label="选择文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".json"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处 或 <em>点击选择文件</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                仅支持 .json 文件
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="导入方式">
          <el-radio-group v-model="importReplaceExisting">
            <el-radio :label="false">追加到现有映射</el-radio>
            <el-radio :label="true">替换现有映射</el-radio>
          </el-radio-group>
          <div class="form-tip">
            <el-text type="warning" size="small">
              ⚠️ 替换模式将删除所有现有映射
            </el-text>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          :disabled="!importFile" 
          :loading="importing"
          @click="importMappings"
        >
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const showAddDialog = ref(false)
const showSmartMappingDialog = ref(false)
const showImportDialog = ref(false)
const showTemplateDialog = ref(false)  // v1.11.0新增
const mappings = ref([])
const bots = ref([])
const smartSuggestions = ref([])
const loadingSuggestions = ref(false)
const applyingMappings = ref(false)
const applyingTemplate = ref(false)  // v1.11.0新增
const importing = ref(false)
const importFile = ref(null)
const importReplaceExisting = ref(false)
const selectedTemplate = ref(null)  // v1.11.0新增

const mappingForm = ref({
  kook_server_id: '',
  kook_channel_id: '',
  kook_channel_name: '',
  target_platform: '',
  target_bot_id: null,
  target_channel_id: ''
})

const targetBots = computed(() => {
  if (!mappingForm.value.target_platform) return []
  return bots.value.filter(b => b.platform === mappingForm.value.target_platform)
})

const fetchMappings = async () => {
  try {
    mappings.value = await api.getMappings()
  } catch (error) {
    console.error('获取映射列表失败:', error)
  }
}

const fetchBots = async () => {
  try {
    bots.value = await api.getBotConfigs()
  } catch (error) {
    console.error('获取机器人列表失败:', error)
  }
}

const addMapping = async () => {
  try {
    await api.addMapping(mappingForm.value)
    ElMessage.success('映射添加成功')
    showAddDialog.value = false
    await fetchMappings()
    
    // 重置表单
    mappingForm.value = {
      kook_server_id: '',
      kook_channel_id: '',
      kook_channel_name: '',
      target_platform: '',
      target_bot_id: null,
      target_channel_id: ''
    }
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  }
}

const deleteMapping = async (mappingId) => {
  try {
    await ElMessageBox.confirm('确定要删除此映射吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.deleteMapping(mappingId)
    ElMessage.success('映射已删除')
    await fetchMappings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

// 生成智能映射建议
const generateSmartSuggestions = async () => {
  try {
    loadingSuggestions.value = true
    
    // 获取账号列表（简化版，实际应该让用户选择）
    const accounts = await api.getAccounts()
    if (!accounts || accounts.length === 0) {
      ElMessage.warning('请先添加KOOK账号')
      return
    }
    
    // 使用第一个账号（实际应该让用户选择）
    const accountId = accounts[0].id
    
    // 获取KOOK服务器和频道
    const serversData = await api.getServers(accountId)
    const servers = serversData.servers || []
    
    if (servers.length === 0) {
      ElMessage.warning('未找到服务器，请确保账号已启动')
      return
    }
    
    // 获取所有服务器的频道
    const kookServers = []
    for (const server of servers) {
      try {
        const channelsData = await api.getChannels(accountId, server.id)
        kookServers.push({
          id: server.id,
          name: server.name,
          channels: channelsData.channels || []
        })
      } catch (error) {
        console.error(`获取服务器 ${server.name} 的频道失败:`, error)
      }
    }
    
    // 生成智能映射建议
    const result = await api.suggestMappings({
      account_id: accountId,
      kook_servers: kookServers,
      target_bots: bots.value
    })
    
    smartSuggestions.value = result
    
    if (result.length === 0) {
      ElMessage.info('未找到匹配的频道映射建议')
    } else {
      ElMessage.success(`找到 ${result.length} 条映射建议`)
    }
  } catch (error) {
    console.error('生成智能映射建议失败:', error)
    ElMessage.error('生成建议失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loadingSuggestions.value = false
  }
}

// 应用智能映射建议
const applySmartSuggestions = async () => {
  try {
    applyingMappings.value = true
    
    if (smartSuggestions.value.length === 0) {
      ElMessage.warning('没有可应用的建议')
      return
    }
    
    await api.applySmartMappings(smartSuggestions.value)
    ElMessage.success('智能映射应用成功')
    
    showSmartMappingDialog.value = false
    smartSuggestions.value = []
    await fetchMappings()
  } catch (error) {
    console.error('应用智能映射失败:', error)
    ElMessage.error('应用失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    applyingMappings.value = false
  }
}

// 获取置信度颜色
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67C23A'
  if (confidence >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

// 导出映射
const exportMappings = async () => {
  try {
    const response = await api.exportMappings()
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // 生成文件名（带时间戳）
    const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0]
    link.setAttribute('download', `channel_mappings_${timestamp}.json`)
    
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('映射导出成功')
  } catch (error) {
    console.error('导出映射失败:', error)
    ElMessage.error('导出失败: ' + (error.message || '未知错误'))
  }
}

// 处理文件选择
const handleFileChange = (file) => {
  importFile.value = file.raw
}

// 处理文件移除
const handleFileRemove = () => {
  importFile.value = null
}

// 导入映射
const importMappings = async () => {
  if (!importFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  try {
    importing.value = true
    
    // 读取文件内容
    const fileContent = await readFileAsText(importFile.value)
    const data = JSON.parse(fileContent)
    
    if (!data.mappings || !Array.isArray(data.mappings)) {
      ElMessage.error('文件格式错误：缺少mappings字段或格式不正确')
      return
    }
    
    // 调用导入API
    const result = await api.importMappings({
      mappings: data.mappings,
      replace_existing: importReplaceExisting.value
    })
    
    // 显示结果
    if (result.failed_count === 0) {
      ElMessage.success(`导入成功！共导入 ${result.success_count} 条映射`)
    } else {
      ElMessage.warning({
        message: `导入完成！成功 ${result.success_count} 条，失败 ${result.failed_count} 条`,
        duration: 5000
      })
      
      // 如果有错误，显示详情
      if (result.errors && result.errors.length > 0) {
        console.error('导入错误详情:', result.errors)
      }
    }
    
    // 关闭对话框并刷新列表
    showImportDialog.value = false
    importFile.value = null
    await fetchMappings()
    
  } catch (error) {
    console.error('导入映射失败:', error)
    if (error instanceof SyntaxError) {
      ElMessage.error('文件格式错误：不是有效的JSON文件')
    } else {
      ElMessage.error('导入失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    importing.value = false
  }
}

// 读取文件为文本
const readFileAsText = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = (e) => reject(e)
    reader.readAsText(file)
  })
}

// v1.11.0新增：获取模板名称
const getTemplateName = (templateKey) => {
  const names = {
    'gaming': '游戏公告模板',
    'community': '社区管理模板',
    'mirror': '跨平台镜像模板'
  }
  return names[templateKey] || '未知模板'
}

// v1.11.0新增：应用模板
const applyTemplate = async () => {
  if (!selectedTemplate.value) {
    ElMessage.warning('请先选择一个模板')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要应用「${getTemplateName(selectedTemplate.value)}」吗？这将替换当前所有映射配置。`,
      '确认应用模板',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    applyingTemplate.value = true

    // 获取模板配置
    const template = getTemplate(selectedTemplate.value)

    // 检查是否有配置的机器人
    if (bots.value.length === 0) {
      ElMessage.warning('请先配置至少一个机器人')
      return
    }

    // 为模板分配机器人（使用第一个可用的机器人）
    const discordBot = bots.value.find(b => b.platform === 'discord')
    const telegramBot = bots.value.find(b => b.platform === 'telegram')
    const feishuBot = bots.value.find(b => b.platform === 'feishu')

    // 将模板转换为映射配置
    const templateMappings = []
    for (const channel of template.channels) {
      // 为每个目标平台创建映射
      if (channel.discord_channel && discordBot) {
        templateMappings.push({
          kook_server_id: channel.kook_server_id || 'template',
          kook_channel_id: channel.kook_channel_id || `${channel.name}_id`,
          kook_channel_name: channel.name,
          target_platform: 'discord',
          target_bot_id: discordBot.id,
          target_channel_id: channel.discord_channel
        })
      }
      
      if (channel.telegram_channel && telegramBot) {
        templateMappings.push({
          kook_server_id: channel.kook_server_id || 'template',
          kook_channel_id: channel.kook_channel_id || `${channel.name}_id`,
          kook_channel_name: channel.name,
          target_platform: 'telegram',
          target_bot_id: telegramBot.id,
          target_channel_id: channel.telegram_channel
        })
      }
      
      if (channel.feishu_channel && feishuBot) {
        templateMappings.push({
          kook_server_id: channel.kook_server_id || 'template',
          kook_channel_id: channel.kook_channel_id || `${channel.name}_id`,
          kook_channel_name: channel.name,
          target_platform: 'feishu',
          target_bot_id: feishuBot.id,
          target_channel_id: channel.feishu_channel
        })
      }
    }

    // 使用导入API应用模板（replace_existing=true）
    const result = await api.importMappings({
      mappings: templateMappings,
      replace_existing: true
    })

    ElMessage.success({
      message: `模板应用成功！共创建 ${result.success_count} 条映射`,
      duration: 3000
    })

    // 关闭对话框并刷新列表
    showTemplateDialog.value = false
    selectedTemplate.value = null
    await fetchMappings()

  } catch (error) {
    if (error !== 'cancel') {
      console.error('应用模板失败:', error)
      ElMessage.error('应用模板失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    applyingTemplate.value = false
  }
}

// v1.11.0新增：获取模板配置
const getTemplate = (templateKey) => {
  const templates = {
    'gaming': {
      name: '游戏公告模板',
      description: '适用于游戏公会、游戏社区',
      channels: [
        {
          name: '📢 公告频道',
          kook_channel_id: 'announcements',
          discord_channel: 'announcements',
          telegram_channel: 'announcements',
          feishu_channel: 'announcements'
        },
        {
          name: '🎉 活动频道',
          kook_channel_id: 'events',
          discord_channel: 'events',
          telegram_channel: 'events',
          feishu_channel: 'events'
        },
        {
          name: '📝 更新日志',
          kook_channel_id: 'changelog',
          discord_channel: 'changelog',
          telegram_channel: 'changelog',
          feishu_channel: 'changelog'
        },
        {
          name: '❓ 常见问题',
          kook_channel_id: 'faq',
          discord_channel: 'faq',
          telegram_channel: 'faq',
          feishu_channel: 'faq'
        }
      ]
    },
    'community': {
      name: '社区管理模板',
      description: '适用于社区管理、运营团队',
      channels: [
        {
          name: '👮 管理员频道',
          kook_channel_id: 'admin',
          discord_channel: 'admin',
          telegram_channel: 'admin',
          feishu_channel: 'admin'
        },
        {
          name: '💬 用户反馈',
          kook_channel_id: 'feedback',
          discord_channel: 'feedback',
          telegram_channel: 'feedback',
          feishu_channel: 'feedback'
        },
        {
          name: '🚨 举报处理',
          kook_channel_id: 'reports',
          discord_channel: 'reports',
          telegram_channel: 'reports',
          feishu_channel: 'reports'
        },
        {
          name: '📊 数据统计',
          kook_channel_id: 'analytics',
          discord_channel: 'analytics',
          telegram_channel: 'analytics',
          feishu_channel: 'analytics'
        }
      ]
    },
    'mirror': {
      name: '跨平台镜像模板',
      description: '全频道镜像同步',
      channels: [
        {
          name: '🔄 全频道镜像',
          kook_channel_id: 'general',
          discord_channel: 'general',
          telegram_channel: 'general',
          feishu_channel: 'general'
        },
        {
          name: '📢 重要通知',
          kook_channel_id: 'important',
          discord_channel: 'important',
          telegram_channel: 'important',
          feishu_channel: 'important'
        }
      ]
    }
  }

  return templates[templateKey] || templates['gaming']
}

watch(() => mappingForm.value.target_platform, () => {
  mappingForm.value.target_bot_id = null
})

onMounted(() => {
  fetchMappings()
  fetchBots()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-top: 8px;
}

.el-icon--upload {
  font-size: 67px;
  color: #8c939d;
  margin: 40px 0 16px;
}

.el-upload__text {
  color: #606266;
  font-size: 14px;
  text-align: center;
}

.el-upload__text em {
  color: #409EFF;
  font-style: normal;
}

/* v1.11.0新增：模板卡片样式 */
.template-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  height: 100%;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.template-card.selected {
  border-color: #409EFF;
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.3);
}

.template-header {
  text-align: center;
  padding: 16px 0;
  border-bottom: 1px solid #EBEEF5;
  margin-bottom: 16px;
}

.template-header h3 {
  margin: 12px 0 0 0;
  font-size: 16px;
  color: #303133;
}

.template-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.template-desc p {
  margin: 8px 0;
}

.template-desc ul {
  margin: 8px 0;
  padding-left: 20px;
}

.template-desc li {
  margin: 4px 0;
}
</style>
