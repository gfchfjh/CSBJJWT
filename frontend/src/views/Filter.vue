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

        <!-- 正则表达式提示 -->
        <el-alert
          title="💡 支持正则表达式"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <div>
            <p>关键词过滤支持正则表达式，您可以使用更强大的匹配模式：</p>
            <ul style="margin: 10px 0; padding-left: 20px;">
              <li><code>广告|代练|外挂</code> - 匹配多个关键词（OR逻辑）</li>
              <li><code>^\d{11}$</code> - 匹配11位数字（手机号）</li>
              <li><code>http[s]?://.*</code> - 匹配所有链接</li>
              <li><code>.*vx.*加.*</code> - 匹配包含"vx"和"加"的消息</li>
              <li><code>普通文本</code> - 不使用正则，直接匹配文本</li>
            </ul>
            <div style="margin-top: 10px;">
              <el-button size="small" @click="showRegexHelp = true">
                查看更多正则表达式示例
              </el-button>
            </div>
          </div>
        </el-alert>

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
              placeholder="支持正则表达式，如：广告|代练|外挂"
              style="width: 300px"
              @keyup.enter="addKeyword('blacklist')"
            >
              <template #append>
                <el-button @click="addKeyword('blacklist')">添加</el-button>
              </template>
            </el-input>
          </div>
          <div class="help-text">
            <el-icon><InfoFilled /></el-icon>
            包含以下关键词（或匹配正则表达式）的消息不会被转发
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
              placeholder="支持正则表达式，如：官方|公告|更新"
              style="width: 300px"
              @keyup.enter="addKeyword('whitelist')"
            >
              <template #append>
                <el-button @click="addKeyword('whitelist')">添加</el-button>
              </template>
            </el-input>
          </div>
          <div class="help-text">
            <el-icon><InfoFilled /></el-icon>
            仅转发包含以下关键词（或匹配正则表达式）的消息（如果白名单为空则不限制）
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

    <!-- 正则表达式帮助对话框 -->
    <el-dialog
      v-model="showRegexHelp"
      title="📚 正则表达式使用指南"
      width="800px"
    >
      <el-collapse>
        <el-collapse-item title="1. 基础匹配" name="1">
          <el-table :data="regexExamples.basic" border>
            <el-table-column prop="pattern" label="表达式" width="200">
              <template #default="{ row }">
                <code>{{ row.pattern }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="example" label="示例匹配" />
          </el-table>
        </el-collapse-item>

        <el-collapse-item title="2. 数量匹配" name="2">
          <el-table :data="regexExamples.quantifier" border>
            <el-table-column prop="pattern" label="表达式" width="200">
              <template #default="{ row }">
                <code>{{ row.pattern }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="example" label="示例匹配" />
          </el-table>
        </el-collapse-item>

        <el-collapse-item title="3. 实用示例" name="3">
          <el-table :data="regexExamples.practical" border>
            <el-table-column prop="pattern" label="表达式" width="250">
              <template #default="{ row }">
                <code>{{ row.pattern }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
            <el-table-column prop="example" label="示例匹配" />
          </el-table>
        </el-collapse-item>

        <el-collapse-item title="4. 常见场景" name="4">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="过滤广告">
              <code>广告|代练|外挂|加V|薇信|vx</code>
            </el-descriptions-item>
            <el-descriptions-item label="过滤链接">
              <code>http[s]?://[^\s]+</code>
            </el-descriptions-item>
            <el-descriptions-item label="过滤手机号">
              <code>1[3-9]\d{9}</code>
            </el-descriptions-item>
            <el-descriptions-item label="过滤QQ号">
              <code>[1-9]\d{4,10}</code>
            </el-descriptions-item>
            <el-descriptions-item label="仅保留官方公告">
              <code>官方|公告|更新|维护|活动</code>
            </el-descriptions-item>
          </el-descriptions>
        </el-collapse-item>
      </el-collapse>

      <el-alert
        title="提示"
        type="warning"
        :closable="false"
        style="margin-top: 20px"
      >
        如果不熟悉正则表达式，也可以直接输入普通文本，系统会自动进行包含匹配。
      </el-alert>

      <template #footer>
        <el-button type="primary" @click="showRegexHelp = false">关闭</el-button>
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

// 正则表达式帮助
const showRegexHelp = ref(false)
const regexExamples = {
  basic: [
    { pattern: '.', description: '匹配任意单个字符', example: 'a, b, 1, @' },
    { pattern: '\\d', description: '匹配数字', example: '0-9' },
    { pattern: '\\w', description: '匹配字母、数字、下划线', example: 'a-z, A-Z, 0-9, _' },
    { pattern: '\\s', description: '匹配空白字符', example: '空格, Tab, 换行' },
    { pattern: '[abc]', description: '匹配方括号内任意字符', example: 'a, b, c' },
    { pattern: '[^abc]', description: '匹配不在方括号内的字符', example: 'd, e, 1, @' },
    { pattern: 'A|B', description: '匹配A或B', example: 'A 或 B' }
  ],
  quantifier: [
    { pattern: '*', description: '匹配0次或多次', example: 'a* 匹配 "", a, aa, aaa' },
    { pattern: '+', description: '匹配1次或多次', example: 'a+ 匹配 a, aa, aaa' },
    { pattern: '?', description: '匹配0次或1次', example: 'a? 匹配 "", a' },
    { pattern: '{n}', description: '匹配n次', example: 'a{3} 匹配 aaa' },
    { pattern: '{n,}', description: '匹配至少n次', example: 'a{2,} 匹配 aa, aaa, aaaa' },
    { pattern: '{n,m}', description: '匹配n到m次', example: 'a{2,4} 匹配 aa, aaa, aaaa' }
  ],
  practical: [
    { pattern: '^开头', description: '以"开头"开始的消息', example: '开头的文字' },
    { pattern: '结尾$', description: '以"结尾"结束的消息', example: '文字结尾' },
    { pattern: '.*包含.*', description: '包含"包含"的消息', example: '前面包含后面' },
    { pattern: '\\d{11}', description: '11位数字（手机号）', example: '13812345678' },
    { pattern: 'QQ[:：]\\s*\\d+', description: 'QQ号码', example: 'QQ: 12345678' },
    { pattern: '(微信|vx|VX)[:：]\\s*\\w+', description: '微信号', example: '微信: abc123' },
    { pattern: 'http[s]?://[^\\s]+', description: '网址链接', example: 'https://example.com' }
  ]
}

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
