<template>
  <div class="filter-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔧 消息过滤规则</span>
          <div>
            <el-button type="primary" @click="saveRules" :loading="saving">
              💾 保存规则
            </el-button>
            <el-button @click="resetRules">
              🔄 重置为默认
            </el-button>
          </div>
        </div>
      </template>

      <el-form :model="filterRules" label-width="150px">
        <!-- 应用范围 -->
        <el-form-item label="应用范围">
          <el-select v-model="filterRules.scope" placeholder="选择应用范围">
            <el-option label="全局规则（所有频道）" value="global" />
            <el-option label="特定频道" value="channel" />
          </el-select>
          <el-input
            v-if="filterRules.scope === 'channel'"
            v-model="filterRules.channel_id"
            placeholder="输入频道ID"
            style="width: 300px; margin-left: 10px"
          />
        </el-form-item>

        <el-divider content-position="left">📝 关键词过滤</el-divider>

        <!-- 关键词黑名单 -->
        <el-form-item label="关键词黑名单">
          <div class="keyword-input">
            <el-tag
              v-for="(keyword, index) in filterRules.keyword_blacklist"
              :key="index"
              closable
              @close="removeKeyword('blacklist', index)"
              style="margin-right: 10px; margin-bottom: 10px"
            >
              {{ keyword }}
            </el-tag>
            <el-input
              v-model="newKeywordBlacklist"
              placeholder="输入关键词后按回车添加"
              style="width: 200px"
              @keyup.enter="addKeyword('blacklist')"
            >
              <template #append>
                <el-button @click="addKeyword('blacklist')">添加</el-button>
              </template>
            </el-input>
          </div>
          <div class="help-text">
            包含以下关键词的消息不会被转发
          </div>
        </el-form-item>

        <!-- 关键词白名单 -->
        <el-form-item label="关键词白名单">
          <div class="keyword-input">
            <el-tag
              v-for="(keyword, index) in filterRules.keyword_whitelist"
              :key="index"
              closable
              type="success"
              @close="removeKeyword('whitelist', index)"
              style="margin-right: 10px; margin-bottom: 10px"
            >
              {{ keyword }}
            </el-tag>
            <el-input
              v-model="newKeywordWhitelist"
              placeholder="输入关键词后按回车添加"
              style="width: 200px"
              @keyup.enter="addKeyword('whitelist')"
            >
              <template #append>
                <el-button @click="addKeyword('whitelist')">添加</el-button>
              </template>
            </el-input>
          </div>
          <div class="help-text">
            仅转发包含以下关键词的消息（如果白名单为空则不限制）
          </div>
        </el-form-item>

        <!-- 启用关键词过滤 -->
        <el-form-item label="启用关键词过滤">
          <el-switch v-model="filterRules.keyword_filter_enabled" />
        </el-form-item>

        <el-divider content-position="left">👤 用户过滤</el-divider>

        <!-- 用户黑名单 -->
        <el-form-item label="用户黑名单">
          <div class="user-list">
            <div
              v-for="(user, index) in filterRules.user_blacklist"
              :key="index"
              class="user-item"
            >
              <span>{{ user.name || user.id }}</span>
              <el-button
                type="danger"
                size="small"
                text
                @click="removeUser('blacklist', index)"
              >
                删除
              </el-button>
            </div>
            <el-button
              type="primary"
              size="small"
              @click="showAddUserDialog('blacklist')"
            >
              ➕ 添加用户
            </el-button>
          </div>
          <div class="help-text">
            以下用户的消息不会被转发
          </div>
        </el-form-item>

        <!-- 用户白名单 -->
        <el-form-item label="用户白名单">
          <div class="user-list">
            <div
              v-for="(user, index) in filterRules.user_whitelist"
              :key="index"
              class="user-item"
            >
              <span>{{ user.name || user.id }}</span>
              <el-button
                type="danger"
                size="small"
                text
                @click="removeUser('whitelist', index)"
              >
                删除
              </el-button>
            </div>
            <el-button
              type="success"
              size="small"
              @click="showAddUserDialog('whitelist')"
            >
              ➕ 添加用户
            </el-button>
          </div>
          <div class="help-text">
            仅转发以下用户的消息（如果白名单为空则不限制）
          </div>
        </el-form-item>

        <!-- 启用用户过滤 -->
        <el-form-item label="启用用户过滤">
          <el-switch v-model="filterRules.user_filter_enabled" />
        </el-form-item>

        <el-divider content-position="left">📦 消息类型过滤</el-divider>

        <!-- 转发的消息类型 -->
        <el-form-item label="转发的消息类型">
          <el-checkbox-group v-model="filterRules.message_types">
            <el-checkbox label="text">文本消息</el-checkbox>
            <el-checkbox label="image">图片消息</el-checkbox>
            <el-checkbox label="file">文件附件</el-checkbox>
            <el-checkbox label="link">链接消息</el-checkbox>
            <el-checkbox label="reaction">表情反应</el-checkbox>
            <el-checkbox label="mention">@提及</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <!-- 特殊过滤选项 -->
        <el-form-item label="特殊选项">
          <el-checkbox v-model="filterRules.only_mention_all">
            仅转发@全体成员的消息
          </el-checkbox>
        </el-form-item>

        <el-divider />

        <!-- 规则统计 -->
        <el-form-item label="规则统计">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="关键词黑名单">
              {{ filterRules.keyword_blacklist.length }} 个
            </el-descriptions-item>
            <el-descriptions-item label="关键词白名单">
              {{ filterRules.keyword_whitelist.length }} 个
            </el-descriptions-item>
            <el-descriptions-item label="用户黑名单">
              {{ filterRules.user_blacklist.length }} 个
            </el-descriptions-item>
            <el-descriptions-item label="用户白名单">
              {{ filterRules.user_whitelist.length }} 个
            </el-descriptions-item>
          </el-descriptions>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 添加用户对话框 -->
    <el-dialog
      v-model="addUserDialogVisible"
      :title="addUserType === 'blacklist' ? '添加到黑名单' : '添加到白名单'"
      width="500px"
    >
      <el-form :model="newUser" label-width="100px">
        <el-form-item label="用户ID">
          <el-input v-model="newUser.id" placeholder="输入KOOK用户ID" />
        </el-form-item>
        <el-form-item label="用户名称">
          <el-input v-model="newUser.name" placeholder="输入用户名（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addUserDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

// 过滤规则
const filterRules = ref({
  scope: 'global',
  channel_id: '',
  keyword_blacklist: [],
  keyword_whitelist: [],
  keyword_filter_enabled: false,
  user_blacklist: [],
  user_whitelist: [],
  user_filter_enabled: false,
  message_types: ['text', 'image', 'file', 'link'],
  only_mention_all: false
})

// 新关键词
const newKeywordBlacklist = ref('')
const newKeywordWhitelist = ref('')

// 添加用户对话框
const addUserDialogVisible = ref(false)
const addUserType = ref('blacklist')
const newUser = ref({ id: '', name: '' })

// 保存中
const saving = ref(false)

// 加载规则
const loadRules = async () => {
  try {
    const response = await api.getFilterRules()
    if (response.data) {
      Object.assign(filterRules.value, response.data)
    }
  } catch (error) {
    console.error('加载规则失败:', error)
  }
}

// 保存规则
const saveRules = async () => {
  try {
    saving.value = true
    await api.saveFilterRules(filterRules.value)
    ElMessage.success('规则保存成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 重置规则
const resetRules = () => {
  if (confirm('确定要重置为默认规则吗？')) {
    filterRules.value = {
      scope: 'global',
      channel_id: '',
      keyword_blacklist: [],
      keyword_whitelist: [],
      keyword_filter_enabled: false,
      user_blacklist: [],
      user_whitelist: [],
      user_filter_enabled: false,
      message_types: ['text', 'image', 'file', 'link'],
      only_mention_all: false
    }
    ElMessage.success('已重置为默认规则')
  }
}

// 添加关键词
const addKeyword = (type) => {
  const keyword = type === 'blacklist' ? newKeywordBlacklist.value : newKeywordWhitelist.value
  
  if (!keyword.trim()) {
    ElMessage.warning('请输入关键词')
    return
  }

  const list = type === 'blacklist' 
    ? filterRules.value.keyword_blacklist 
    : filterRules.value.keyword_whitelist

  if (list.includes(keyword.trim())) {
    ElMessage.warning('关键词已存在')
    return
  }

  list.push(keyword.trim())
  
  if (type === 'blacklist') {
    newKeywordBlacklist.value = ''
  } else {
    newKeywordWhitelist.value = ''
  }
}

// 删除关键词
const removeKeyword = (type, index) => {
  const list = type === 'blacklist' 
    ? filterRules.value.keyword_blacklist 
    : filterRules.value.keyword_whitelist
  list.splice(index, 1)
}

// 显示添加用户对话框
const showAddUserDialog = (type) => {
  addUserType.value = type
  newUser.value = { id: '', name: '' }
  addUserDialogVisible.value = true
}

// 添加用户
const addUser = () => {
  if (!newUser.value.id) {
    ElMessage.warning('请输入用户ID')
    return
  }

  const list = addUserType.value === 'blacklist'
    ? filterRules.value.user_blacklist
    : filterRules.value.user_whitelist

  if (list.some(u => u.id === newUser.value.id)) {
    ElMessage.warning('用户已存在')
    return
  }

  list.push({ ...newUser.value })
  addUserDialogVisible.value = false
  ElMessage.success('用户添加成功')
}

// 删除用户
const removeUser = (type, index) => {
  const list = type === 'blacklist'
    ? filterRules.value.user_blacklist
    : filterRules.value.user_whitelist
  list.splice(index, 1)
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.filter-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.keyword-input {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.help-text {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.user-list {
  width: 100%;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 10px;
}

.user-item:hover {
  background: #f5f7fa;
}
</style>
