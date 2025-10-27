<template>
  <div class="filter-enhanced">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span><el-icon><Filter /></el-icon> 消息过滤规则</span>
          <el-button type="primary" :icon="MagicStick" @click="showTestDialog">
            测试规则
          </el-button>
        </div>
      </template>
      
      <!-- 应用范围 -->
      <el-form-item label="应用范围">
        <el-select v-model="filterScope" placeholder="选择应用范围" style="width: 300px">
          <el-option label="全局规则（所有频道）" value="global" />
          <el-option label="仅特定频道" value="channel" />
        </el-select>
      </el-form-item>
      
      <el-divider content-position="left">
        <el-icon><Key /></el-icon>
        关键词过滤
      </el-divider>
      
      <!-- 黑名单关键词 -->
      <el-form-item label="黑名单">
        <div class="keyword-section">
          <p class="section-hint">包含以下关键词的消息将不会转发</p>
          
          <!-- Tag输入器 -->
          <div class="tag-input-container">
            <el-tag
              v-for="tag in blacklistKeywords"
              :key="tag"
              closable
              @close="removeBlacklistTag(tag)"
              type="danger"
              size="large"
              class="keyword-tag"
            >
              {{ tag }}
            </el-tag>
            
            <el-input
              v-if="showBlacklistInput"
              ref="blacklistInputRef"
              v-model="newBlacklistKeyword"
              placeholder="输入关键词后按回车"
              @keyup.enter="addBlacklistTag"
              @blur="addBlacklistTag"
              size="small"
              class="tag-input"
              style="width: 150px"
            />
            
            <el-button
              v-else
              size="small"
              :icon="Plus"
              @click="showBlacklistInputBox"
            >
              添加关键词
            </el-button>
          </div>
        </div>
      </el-form-item>
      
      <!-- 白名单关键词 -->
      <el-form-item label="白名单">
        <div class="keyword-section">
          <p class="section-hint">仅转发包含以下关键词的消息（留空则不限制）</p>
          
          <div class="tag-input-container">
            <el-tag
              v-for="tag in whitelistKeywords"
              :key="tag"
              closable
              @close="removeWhitelistTag(tag)"
              type="success"
              size="large"
              class="keyword-tag"
            >
              {{ tag }}
            </el-tag>
            
            <el-input
              v-if="showWhitelistInput"
              ref="whitelistInputRef"
              v-model="newWhitelistKeyword"
              placeholder="输入关键词后按回车"
              @keyup.enter="addWhitelistTag"
              @blur="addWhitelistTag"
              size="small"
              class="tag-input"
              style="width: 150px"
            />
            
            <el-button
              v-else
              size="small"
              :icon="Plus"
              @click="showWhitelistInputBox"
            >
              添加关键词
            </el-button>
          </div>
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-switch
          v-model="keywordFilterEnabled"
          active-text="启用关键词过滤"
          inactive-text="禁用"
        />
      </el-form-item>
      
      <el-divider content-position="left">
        <el-icon><User /></el-icon>
        用户过滤
      </el-divider>
      
      <!-- 黑名单用户 -->
      <el-form-item label="黑名单用户">
        <div class="user-section">
          <p class="section-hint">不转发以下用户的消息</p>
          
          <el-table :data="blacklistUsers" stripe max-height="200">
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="user_id" label="用户ID" width="200" />
            <el-table-column label="操作" width="100">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  @click="removeBlacklistUser($index)"
                />
              </template>
            </el-table-column>
          </el-table>
          
          <el-button
            :icon="Plus"
            style="margin-top: 10px"
            @click="showUserSelector('blacklist')"
          >
            添加用户
          </el-button>
        </div>
      </el-form-item>
      
      <!-- 白名单用户 -->
      <el-form-item label="白名单用户">
        <div class="user-section">
          <p class="section-hint">仅转发以下用户的消息（留空则不限制）</p>
          
          <el-table :data="whitelistUsers" stripe max-height="200">
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="user_id" label="用户ID" width="200" />
            <el-table-column label="操作" width="100">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  @click="removeWhitelistUser($index)"
                />
              </template>
            </el-table-column>
          </el-table>
          
          <el-button
            :icon="Plus"
            style="margin-top: 10px"
            @click="showUserSelector('whitelist')"
          >
            添加用户
          </el-button>
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-switch
          v-model="userFilterEnabled"
          active-text="启用用户过滤"
          inactive-text="禁用"
        />
      </el-form-item>
      
      <el-divider content-position="left">
        <el-icon><Document /></el-icon>
        消息类型过滤
      </el-divider>
      
      <el-form-item label="转发的消息类型">
        <el-checkbox-group v-model="allowedMessageTypes">
          <el-checkbox value="text" label="文本消息" />
          <el-checkbox value="image" label="图片消息" />
          <el-checkbox value="link" label="链接消息" />
          <el-checkbox value="file" label="文件附件" />
          <el-checkbox value="reaction" label="表情反应" />
          <el-checkbox value="mention_all" label="@全体成员的消息" />
        </el-checkbox-group>
      </el-form-item>
      
      <!-- 保存按钮 -->
      <el-form-item>
        <el-button type="primary" size="large" :loading="saving" @click="saveRules">
          <el-icon><Check /></el-icon>
          保存规则
        </el-button>
        <el-button size="large" @click="resetRules">
          <el-icon><RefreshLeft /></el-icon>
          重置为默认
        </el-button>
      </el-form-item>
    </el-card>
    
    <!-- 用户选择器对话框 -->
    <el-dialog
      v-model="userSelectorVisible"
      title="选择用户"
      width="600px"
    >
      <el-input
        v-model="userSearchQuery"
        placeholder="搜索用户..."
        :prefix-icon="Search"
        clearable
        @input="searchUsers"
      />
      
      <el-table
        :data="userSearchResults"
        stripe
        max-height="400"
        @row-click="selectUser"
        style="margin-top: 15px"
      >
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="user_id" label="用户ID" />
      </el-table>
      
      <template #footer>
        <el-button @click="userSelectorVisible = false">取消</el-button>
      </template>
    </el-dialog>
    
    <!-- 规则测试对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="测试过滤规则"
      width="700px"
    >
      <el-form label-width="100px">
        <el-form-item label="测试消息">
          <el-input
            v-model="testMessage.content"
            type="textarea"
            :rows="4"
            placeholder="输入要测试的消息内容..."
          />
        </el-form-item>
        
        <el-form-item label="发送者">
          <el-input v-model="testMessage.sender" placeholder="用户名" />
        </el-form-item>
        
        <el-form-item label="消息类型">
          <el-select v-model="testMessage.type">
            <el-option label="文本消息" value="text" />
            <el-option label="图片消息" value="image" />
            <el-option label="链接消息" value="link" />
            <el-option label="文件附件" value="file" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="runTest">运行测试</el-button>
        </el-form-item>
        
        <!-- 测试结果 -->
        <el-alert
          v-if="testResult"
          :type="testResult.passed ? 'success' : 'error'"
          :title="testResult.passed ? '✅ 通过过滤' : '❌ 被过滤'"
          :closable="false"
          show-icon
        >
          <template v-if="!testResult.passed">
            <p><strong>原因:</strong> {{ testResult.reason }}</p>
            <p v-if="testResult.matched_rule">
              <strong>匹配规则:</strong> {{ testResult.matched_rule }}
            </p>
          </template>
        </el-alert>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Filter,
  MagicStick,
  Key,
  User,
  Document,
  Plus,
  Delete,
  Check,
  RefreshLeft,
  Search
} from '@element-plus/icons-vue'
import api from '@/api'

// 状态
const filterScope = ref('global')
const saving = ref(false)

// 关键词过滤
const blacklistKeywords = ref(['广告', '代练', '外挂'])
const whitelistKeywords = ref([])
const keywordFilterEnabled = ref(true)
const showBlacklistInput = ref(false)
const showWhitelistInput = ref(false)
const newBlacklistKeyword = ref('')
const newWhitelistKeyword = ref('')
const blacklistInputRef = ref(null)
const whitelistInputRef = ref(null)

// 用户过滤
const blacklistUsers = ref([])
const whitelistUsers = ref([])
const userFilterEnabled = ref(false)
const userSelectorVisible = ref(false)
const userSelectorType = ref('blacklist')
const userSearchQuery = ref('')
const userSearchResults = ref([])

// 消息类型过滤
const allowedMessageTypes = ref(['text', 'image', 'link'])

// 规则测试
const testDialogVisible = ref(false)
const testMessage = ref({
  content: '',
  sender: '',
  type: 'text'
})
const testResult = ref(null)

// 方法
const showBlacklistInputBox = () => {
  showBlacklistInput.value = true
  nextTick(() => {
    blacklistInputRef.value?.focus()
  })
}

const addBlacklistTag = () => {
  const keyword = newBlacklistKeyword.value.trim()
  if (keyword && !blacklistKeywords.value.includes(keyword)) {
    blacklistKeywords.value.push(keyword)
  }
  newBlacklistKeyword.value = ''
  showBlacklistInput.value = false
}

const removeBlacklistTag = (tag) => {
  const index = blacklistKeywords.value.indexOf(tag)
  blacklistKeywords.value.splice(index, 1)
}

const showWhitelistInputBox = () => {
  showWhitelistInput.value = true
  nextTick(() => {
    whitelistInputRef.value?.focus()
  })
}

const addWhitelistTag = () => {
  const keyword = newWhitelistKeyword.value.trim()
  if (keyword && !whitelistKeywords.value.includes(keyword)) {
    whitelistKeywords.value.push(keyword)
  }
  newWhitelistKeyword.value = ''
  showWhitelistInput.value = false
}

const removeWhitelistTag = (tag) => {
  const index = whitelistKeywords.value.indexOf(tag)
  whitelistKeywords.value.splice(index, 1)
}

const showUserSelector = (type) => {
  userSelectorType.value = type
  userSelectorVisible.value = true
  userSearchQuery.value = ''
  userSearchResults.value = []
}

const searchUsers = async () => {
  if (!userSearchQuery.value.trim()) {
    userSearchResults.value = []
    return
  }
  
  try {
    const response = await api.get('/api/users/search', {
      params: { query: userSearchQuery.value }
    })
    userSearchResults.value = response.data
  } catch (error) {
    console.error('搜索用户失败:', error)
    ElMessage.error('搜索用户失败')
  }
}

const selectUser = (user) => {
  if (userSelectorType.value === 'blacklist') {
    if (!blacklistUsers.value.some(u => u.user_id === user.user_id)) {
      blacklistUsers.value.push(user)
    }
  } else {
    if (!whitelistUsers.value.some(u => u.user_id === user.user_id)) {
      whitelistUsers.value.push(user)
    }
  }
  
  userSelectorVisible.value = false
  ElMessage.success('用户已添加')
}

const removeBlacklistUser = (index) => {
  blacklistUsers.value.splice(index, 1)
}

const removeWhitelistUser = (index) => {
  whitelistUsers.value.splice(index, 1)
}

const showTestDialog = () => {
  testDialogVisible.value = true
  testResult.value = null
}

const runTest = () => {
  /**
   * 测试消息是否通过过滤规则（✨ P0-7核心功能）
   */
  const result = {
    passed: true,
    reason: '',
    matched_rule: ''
  }
  
  const content = testMessage.value.content
  const sender = testMessage.value.sender
  const type = testMessage.value.type
  
  // 测试1: 消息类型过滤
  if (!allowedMessageTypes.value.includes(type)) {
    result.passed = false
    result.reason = `消息类型 "${type}" 未被允许`
    result.matched_rule = '消息类型过滤'
    testResult.value = result
    return
  }
  
  // 测试2: 黑名单关键词
  if (keywordFilterEnabled.value && blacklistKeywords.value.length > 0) {
    for (const keyword of blacklistKeywords.value) {
      if (content.includes(keyword)) {
        result.passed = false
        result.reason = `包含黑名单关键词: "${keyword}"`
        result.matched_rule = '关键词黑名单'
        testResult.value = result
        return
      }
    }
  }
  
  // 测试3: 白名单关键词
  if (keywordFilterEnabled.value && whitelistKeywords.value.length > 0) {
    const hasWhitelisted = whitelistKeywords.value.some(kw => content.includes(kw))
    if (!hasWhitelisted) {
      result.passed = false
      result.reason = '不包含任何白名单关键词'
      result.matched_rule = '关键词白名单'
      testResult.value = result
      return
    }
  }
  
  // 测试4: 黑名单用户
  if (userFilterEnabled.value && blacklistUsers.value.length > 0) {
    const isBlacklisted = blacklistUsers.value.some(u => u.username === sender)
    if (isBlacklisted) {
      result.passed = false
      result.reason = `发送者 "${sender}" 在黑名单中`
      result.matched_rule = '用户黑名单'
      testResult.value = result
      return
    }
  }
  
  // 测试5: 白名单用户
  if (userFilterEnabled.value && whitelistUsers.value.length > 0) {
    const isWhitelisted = whitelistUsers.value.some(u => u.username === sender)
    if (!isWhitelisted) {
      result.passed = false
      result.reason = `发送者 "${sender}" 不在白名单中`
      result.matched_rule = '用户白名单'
      testResult.value = result
      return
    }
  }
  
  // 全部通过
  result.passed = true
  result.reason = '消息通过所有过滤规则'
  testResult.value = result
}

const saveRules = async () => {
  saving.value = true
  
  try {
    await api.post('/api/filter/rules', {
      scope: filterScope.value,
      keyword_blacklist: blacklistKeywords.value,
      keyword_whitelist: whitelistKeywords.value,
      keyword_enabled: keywordFilterEnabled.value,
      user_blacklist: blacklistUsers.value,
      user_whitelist: whitelistUsers.value,
      user_enabled: userFilterEnabled.value,
      allowed_message_types: allowedMessageTypes.value
    })
    
    ElMessage.success('规则保存成功')
  } catch (error) {
    console.error('保存规则失败:', error)
    ElMessage.error('保存规则失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const resetRules = async () => {
  try {
    await ElMessageBox.confirm('确定要重置为默认规则吗？', '确认重置', {
      type: 'warning'
    })
    
    // 重置为默认值
    filterScope.value = 'global'
    blacklistKeywords.value = ['广告', '代练', '外挂']
    whitelistKeywords.value = []
    keywordFilterEnabled.value = true
    blacklistUsers.value = []
    whitelistUsers.value = []
    userFilterEnabled.value = false
    allowedMessageTypes.value = ['text', 'image', 'link']
    
    ElMessage.info('已重置为默认规则')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.filter-enhanced {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.keyword-section,
.user-section {
  width: 100%;
}

.section-hint {
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
}

.tag-input-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  min-height: 60px;
}

.keyword-tag {
  font-size: 14px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.keyword-tag:hover {
  transform: scale(1.05);
}

.tag-input {
  flex-shrink: 0;
}

/* 暗黑模式 */
.dark .tag-input-container {
  background: #2c2c2c;
}
</style>
