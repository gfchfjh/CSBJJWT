<template>
  <div class="filter-rules-editor-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>
        <el-icon><Filter /></el-icon>
        过滤规则编辑器
      </h1>
      
      <el-button-group>
        <el-button :icon="Plus" type="primary" @click="addRule">
          添加规则
        </el-button>
        <el-button :icon="Upload" @click="importRules">
          导入规则
        </el-button>
        <el-button :icon="Download" @click="exportRules">
          导出规则
        </el-button>
      </el-button-group>
    </div>
    
    <!-- 规则模板库 -->
    <el-card class="templates-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>
            <el-icon><Collection /></el-icon>
            规则模板库
          </span>
          <el-tag type="info">{{ templates.length }}个模板</el-tag>
        </div>
      </template>
      
      <el-row :gutter="16">
        <el-col 
          :span="6" 
          v-for="template in templates" 
          :key="template.id"
        >
          <el-card class="template-card" shadow="hover" @click="useTemplate(template)">
            <div class="template-icon">
              <el-icon :size="32">
                <component :is="template.icon" />
              </el-icon>
            </div>
            <div class="template-name">{{ template.name }}</div>
            <div class="template-desc">{{ template.description }}</div>
            <el-button type="primary" size="small" style="margin-top: 12px;">
              使用模板
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 规则列表 -->
    <el-card class="rules-card">
      <template #header>
        <div class="card-header">
          <span>
            <el-icon><List /></el-icon>
            已配置规则（{{ rules.length }}个）
          </span>
          
          <el-space>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索规则..."
              :prefix-icon="Search"
              clearable
              style="width: 200px;"
            />
            
            <el-select v-model="filterType" placeholder="规则类型" clearable style="width: 150px;">
              <el-option label="全部类型" value="" />
              <el-option label="关键词过滤" value="keyword" />
              <el-option label="用户过滤" value="user" />
              <el-option label="正则表达式" value="regex" />
              <el-option label="频道过滤" value="channel" />
            </el-select>
          </el-space>
        </div>
      </template>
      
      <el-empty 
        v-if="filteredRules.length === 0"
        description="还没有配置任何规则"
      >
        <el-button type="primary" :icon="Plus" @click="addRule">
          添加第一条规则
        </el-button>
      </el-empty>
      
      <el-table v-else :data="filteredRules" style="width: 100%">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="rule-detail">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="规则ID">
                  {{ row.id }}
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">
                  {{ formatTime(row.created_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="最后修改">
                  {{ formatTime(row.updated_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="匹配次数">
                  {{ row.match_count || 0 }}次
                </el-descriptions-item>
                <el-descriptions-item label="详细配置" :span="2">
                  <pre>{{ JSON.stringify(row.config, null, 2) }}</pre>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="规则名称" width="200">
          <template #default="{ row }">
            <el-text>{{ row.name }}</el-text>
            <el-tag v-if="row.is_template" type="info" size="small" style="margin-left: 8px;">
              模板
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getRuleTypeTag(row.type)">
              {{ getRuleTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="action" label="动作" width="100">
          <template #default="{ row }">
            <el-tag :type="row.action === 'allow' ? 'success' : 'danger'">
              {{ row.action === 'allow' ? '允许' : '阻止' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="pattern" label="匹配模式" min-width="200">
          <template #default="{ row }">
            <el-text class="pattern-text" truncated>
              {{ row.pattern || row.config?.pattern || 'N/A' }}
            </el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="scope" label="应用范围" width="150">
          <template #default="{ row }">
            <el-tag size="small">
              {{ getScopeLabel(row.scope) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.enabled"
              @change="toggleRule(row)"
              active-text="启用"
              inactive-text="禁用"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="优先级" width="120">
          <template #default="{ row }">
            <el-input-number
              v-model="row.priority"
              :min="0"
              :max="100"
              size="small"
              @change="updatePriority(row)"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group size="small">
              <el-button :icon="View" @click="testRule(row)">
                测试
              </el-button>
              <el-button :icon="Edit" @click="editRule(row)">
                编辑
              </el-button>
              <el-button :icon="Delete" type="danger" @click="deleteRule(row)">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 规则编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editMode === 'add' ? '添加规则' : '编辑规则'"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="ruleForm" label-width="100px">
        <el-form-item label="规则名称">
          <el-input v-model="ruleForm.name" placeholder="给规则起个名字" />
        </el-form-item>
        
        <el-form-item label="规则类型">
          <el-select v-model="ruleForm.type" placeholder="选择规则类型" @change="onRuleTypeChange">
            <el-option label="关键词过滤" value="keyword">
              <el-icon><Key /></el-icon> 关键词过滤
            </el-option>
            <el-option label="用户过滤" value="user">
              <el-icon><User /></el-icon> 用户过滤
            </el-option>
            <el-option label="正则表达式" value="regex">
              <el-icon><Operation /></el-icon> 正则表达式
            </el-option>
            <el-option label="频道过滤" value="channel">
              <el-icon><ChatDotRound /></el-icon> 频道过滤
            </el-option>
            <el-option label="消息类型" value="message_type">
              <el-icon><Message /></el-icon> 消息类型
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="动作">
          <el-radio-group v-model="ruleForm.action">
            <el-radio label="allow">允许通过</el-radio>
            <el-radio label="block">阻止转发</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 关键词规则 -->
        <template v-if="ruleForm.type === 'keyword'">
          <el-form-item label="关键词">
            <el-input
              v-model="ruleForm.pattern"
              type="textarea"
              :rows="3"
              placeholder="每行一个关键词，支持英文逗号分隔"
            />
          </el-form-item>
          
          <el-form-item label="匹配选项">
            <el-checkbox-group v-model="ruleForm.options">
              <el-checkbox label="case_sensitive">区分大小写</el-checkbox>
              <el-checkbox label="whole_word">全词匹配</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </template>
        
        <!-- 用户规则 -->
        <template v-if="ruleForm.type === 'user'">
          <el-form-item label="用户ID">
            <el-select
              v-model="ruleForm.users"
              multiple
              filterable
              allow-create
              placeholder="输入用户ID或昵称"
              style="width: 100%;"
            >
              <!-- 这里可以从API加载用户列表 -->
            </el-select>
          </el-form-item>
        </template>
        
        <!-- 正则表达式规则 -->
        <template v-if="ruleForm.type === 'regex'">
          <el-form-item label="正则表达式">
            <el-input
              v-model="ruleForm.pattern"
              placeholder="例如: ^\\[公告\\].*"
            />
          </el-form-item>
          
          <el-form-item label="测试文本">
            <el-input
              v-model="regexTestText"
              type="textarea"
              :rows="3"
              placeholder="输入文本测试正则表达式"
            />
            <el-button 
              @click="testRegex" 
              size="small" 
              style="margin-top: 8px;"
              :type="regexTestResult ? 'success' : 'danger'"
            >
              测试 {{ regexTestResult !== null ? (regexTestResult ? '✓ 匹配' : '✗ 不匹配') : '' }}
            </el-button>
          </el-form-item>
          
          <el-form-item label="正则选项">
            <el-checkbox-group v-model="ruleForm.regexFlags">
              <el-checkbox label="i">忽略大小写(i)</el-checkbox>
              <el-checkbox label="m">多行模式(m)</el-checkbox>
              <el-checkbox label="s">单行模式(s)</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </template>
        
        <!-- 频道规则 -->
        <template v-if="ruleForm.type === 'channel'">
          <el-form-item label="选择频道">
            <el-tree-select
              v-model="ruleForm.channels"
              :data="channelTree"
              multiple
              node-key="id"
              show-checkbox
              placeholder="选择要过滤的频道"
              style="width: 100%;"
            />
          </el-form-item>
        </template>
        
        <!-- 消息类型规则 -->
        <template v-if="ruleForm.type === 'message_type'">
          <el-form-item label="消息类型">
            <el-checkbox-group v-model="ruleForm.messageTypes">
              <el-checkbox label="text">文本</el-checkbox>
              <el-checkbox label="image">图片</el-checkbox>
              <el-checkbox label="video">视频</el-checkbox>
              <el-checkbox label="file">文件</el-checkbox>
              <el-checkbox label="audio">音频</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </template>
        
        <el-form-item label="应用范围">
          <el-radio-group v-model="ruleForm.scope">
            <el-radio label="global">全局</el-radio>
            <el-radio label="channel">指定频道</el-radio>
            <el-radio label="server">指定服务器</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="ruleForm.scope !== 'global'" label="选择范围">
          <!-- 根据scope显示不同的选择器 -->
          <el-select 
            v-model="ruleForm.scopeIds" 
            multiple 
            placeholder="选择..."
            style="width: 100%;"
          >
            <!-- 这里可以从API加载频道/服务器列表 -->
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级">
          <el-slider v-model="ruleForm.priority" :min="0" :max="100" show-input />
          <el-text type="info" size="small">
            优先级越高的规则越先执行（0-100）
          </el-text>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="ruleForm.description"
            type="textarea"
            :rows="2"
            placeholder="简要描述这个规则的作用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRule" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 规则测试对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="测试规则"
      width="600px"
    >
      <el-form>
        <el-form-item label="测试消息">
          <el-input
            v-model="testMessage"
            type="textarea"
            :rows="4"
            placeholder="输入要测试的消息内容"
          />
        </el-form-item>
        
        <el-form-item label="测试结果">
          <el-alert
            v-if="testResult"
            :type="testResult.matched ? 'success' : 'info'"
            :title="testResult.matched ? '✓ 匹配成功' : '✗ 不匹配'"
            :closable="false"
            show-icon
          >
            <template #default>
              <div>{{ testResult.message }}</div>
            </template>
          </el-alert>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="testDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="runTest">
          运行测试
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Filter, Plus, Upload, Download, Collection, List, Search,
  View, Edit, Delete, Key, User, Operation, ChatDotRound, Message
} from '@element-plus/icons-vue'
import axios from 'axios'

// 状态
const loading = ref(false)
const saving = ref(false)
const rules = ref([])
const searchKeyword = ref('')
const filterType = ref('')
const editDialogVisible = ref(false)
const testDialogVisible = ref(false)
const editMode = ref('add')
const currentRule = ref(null)
const channelTree = ref([])

// 规则表单
const ruleForm = ref({
  name: '',
  type: 'keyword',
  action: 'block',
  pattern: '',
  scope: 'global',
  scopeIds: [],
  priority: 50,
  enabled: true,
  options: [],
  users: [],
  channels: [],
  messageTypes: [],
  regexFlags: [],
  description: ''
})

// 正则测试
const regexTestText = ref('')
const regexTestResult = ref(null)

// 规则测试
const testMessage = ref('')
const testResult = ref(null)

// 规则模板
const templates = ref([
  {
    id: 1,
    name: '广告过滤',
    description: '阻止包含广告关键词的消息',
    icon: 'Warning',
    type: 'keyword',
    action: 'block',
    pattern: '广告,代练,外挂,加群,优惠,促销',
    scope: 'global'
  },
  {
    id: 2,
    name: '仅官方消息',
    description: '只转发官方管理员的消息',
    icon: 'User',
    type: 'user',
    action: 'allow',
    users: ['admin', 'official'],
    scope: 'global'
  },
  {
    id: 3,
    name: '重要公告',
    description: '只转发标题为【公告】的消息',
    icon: 'Bell',
    type: 'regex',
    action: 'allow',
    pattern: '^\\[公告\\]|^【公告】',
    scope: 'global'
  },
  {
    id: 4,
    name: '纯文本消息',
    description: '只转发文本类型消息',
    icon: 'Document',
    type: 'message_type',
    action: 'allow',
    messageTypes: ['text'],
    scope: 'global'
  }
])

// 过滤后的规则
const filteredRules = computed(() => {
  let result = rules.value
  
  if (filterType.value) {
    result = result.filter(r => r.type === filterType.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(r => 
      r.name.toLowerCase().includes(keyword) ||
      (r.pattern && r.pattern.toLowerCase().includes(keyword))
    )
  }
  
  return result
})

// 加载规则
async function loadRules() {
  loading.value = true
  
  try {
    const response = await axios.get('/api/filter-rules')
    rules.value = response.data
  } catch (error) {
    ElMessage.error('加载规则失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 添加规则
function addRule() {
  editMode.value = 'add'
  currentRule.value = null
  ruleForm.value = {
    name: '',
    type: 'keyword',
    action: 'block',
    pattern: '',
    scope: 'global',
    scopeIds: [],
    priority: 50,
    enabled: true,
    options: [],
    users: [],
    channels: [],
    messageTypes: [],
    regexFlags: [],
    description: ''
  }
  editDialogVisible.value = true
}

// 编辑规则
function editRule(rule) {
  editMode.value = 'edit'
  currentRule.value = rule
  ruleForm.value = { ...rule }
  editDialogVisible.value = true
}

// 保存规则
async function saveRule() {
  if (!ruleForm.value.name) {
    ElMessage.warning('请输入规则名称')
    return
  }
  
  saving.value = true
  
  try {
    if (editMode.value === 'add') {
      await axios.post('/api/filter-rules', ruleForm.value)
      ElMessage.success('规则添加成功')
    } else {
      await axios.put(`/api/filter-rules/${currentRule.value.id}`, ruleForm.value)
      ElMessage.success('规则更新成功')
    }
    
    editDialogVisible.value = false
    await loadRules()
    
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

// 删除规则
function deleteRule(rule) {
  ElMessageBox.confirm(
    `确定要删除规则"${rule.name}"吗？`,
    '删除规则',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/filter-rules/${rule.id}`)
      ElMessage.success('删除成功')
      await loadRules()
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  }).catch(() => {})
}

// 切换规则状态
async function toggleRule(rule) {
  try {
    await axios.patch(`/api/filter-rules/${rule.id}`, {
      enabled: rule.enabled
    })
    ElMessage.success(rule.enabled ? '规则已启用' : '规则已禁用')
  } catch (error) {
    ElMessage.error('更新失败: ' + error.message)
    rule.enabled = !rule.enabled
  }
}

// 更新优先级
async function updatePriority(rule) {
  try {
    await axios.patch(`/api/filter-rules/${rule.id}`, {
      priority: rule.priority
    })
  } catch (error) {
    ElMessage.error('更新失败: ' + error.message)
  }
}

// 测试规则
function testRule(rule) {
  currentRule.value = rule
  testMessage.value = ''
  testResult.value = null
  testDialogVisible.value = true
}

// 运行测试
async function runTest() {
  if (!testMessage.value) {
    ElMessage.warning('请输入测试消息')
    return
  }
  
  try {
    const response = await axios.post(`/api/filter-rules/${currentRule.value.id}/test`, {
      message: testMessage.value
    })
    
    testResult.value = response.data
    
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  }
}

// 测试正则表达式
function testRegex() {
  if (!ruleForm.value.pattern || !regexTestText.value) {
    ElMessage.warning('请输入正则表达式和测试文本')
    return
  }
  
  try {
    const flags = ruleForm.value.regexFlags.join('')
    const regex = new RegExp(ruleForm.value.pattern, flags)
    regexTestResult.value = regex.test(regexTestText.value)
  } catch (error) {
    ElMessage.error('正则表达式无效: ' + error.message)
    regexTestResult.value = null
  }
}

// 使用模板
function useTemplate(template) {
  ruleForm.value = {
    ...ruleForm.value,
    ...template,
    name: template.name + ' (副本)',
    id: undefined
  }
  editMode.value = 'add'
  editDialogVisible.value = true
}

// 导入规则
function importRules() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    try {
      const text = await file.text()
      const importedRules = JSON.parse(text)
      
      await axios.post('/api/filter-rules/batch', { rules: importedRules })
      
      ElMessage.success(`导入了${importedRules.length}条规则`)
      await loadRules()
      
    } catch (error) {
      ElMessage.error('导入失败: ' + error.message)
    }
  }
  input.click()
}

// 导出规则
function exportRules() {
  const data = JSON.stringify(rules.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `filter-rules-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success(`已导出${rules.value.length}条规则`)
}

// 工具函数
function getRuleTypeTag(type) {
  const tags = {
    keyword: 'primary',
    user: 'success',
    regex: 'warning',
    channel: 'info',
    message_type: 'danger'
  }
  return tags[type] || 'info'
}

function getRuleTypeLabel(type) {
  const labels = {
    keyword: '关键词',
    user: '用户',
    regex: '正则',
    channel: '频道',
    message_type: '类型'
  }
  return labels[type] || type
}

function getScopeLabel(scope) {
  const labels = {
    global: '全局',
    channel: '指定频道',
    server: '指定服务器'
  }
  return labels[scope] || scope
}

function formatTime(timestamp) {
  if (!timestamp) return 'N/A'
  return new Date(timestamp).toLocaleString('zh-CN')
}

function onRuleTypeChange() {
  // 规则类型变化时重置相关字段
  ruleForm.value.pattern = ''
  ruleForm.value.users = []
  ruleForm.value.channels = []
  ruleForm.value.messageTypes = []
}

// 初始化
onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.filter-rules-editor-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.templates-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.template-icon {
  margin-bottom: 12px;
  color: #409EFF;
}

.template-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.template-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.rules-card {
  margin-bottom: 24px;
}

.rule-detail {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.pattern-text {
  font-family: 'Courier New', monospace;
}
</style>
