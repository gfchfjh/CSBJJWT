<template>
  <div class="filter-enhanced">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>🔧 消息过滤规则</h2>
          <div class="header-actions">
            <el-button @click="loadTemplate">
              <el-icon><Document /></el-icon> 加载模板
            </el-button>
            <el-button type="primary" @click="saveRules" :loading="isSaving">
              <el-icon><Check /></el-icon> 保存规则
            </el-button>
          </div>
        </div>
      </template>

      <el-alert
        title="过滤规则说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #default>
          过滤规则用于控制哪些消息需要转发。黑名单中的消息会被拦截，白名单中的消息会被优先转发。
        </template>
      </el-alert>

      <el-tabs v-model="activeTab">
        <!-- 关键词过滤 -->
        <el-tab-pane label="📝 关键词过滤" name="keyword">
          <el-row :gutter="20">
            <el-col :span="12">
              <h3>🚫 黑名单（包含以下词不转发）</h3>
              
              <!-- 批量输入 -->
              <el-input
                v-model="blacklistText"
                type="textarea"
                :rows="6"
                placeholder="输入关键词，用逗号分隔（例如：广告, 代练, 外挂）"
                @blur="parseKeywords('blacklist')"
              />
              
              <!-- 关键词标签 -->
              <div class="keyword-tags">
                <el-tag
                  v-for="(kw, index) in rules.keywordBlacklist"
                  :key="index"
                  closable
                  @close="removeKeyword('blacklist', index)"
                  style="margin: 5px;"
                >
                  {{ kw }}
                </el-tag>
              </div>
              
              <div class="keyword-actions">
                <el-button size="small" @click="addKeyword('blacklist')">
                  添加关键词
                </el-button>
                <el-button size="small" @click="clearKeywords('blacklist')">
                  清空
                </el-button>
              </div>
            </el-col>

            <el-col :span="12">
              <h3>✅ 白名单（仅转发包含以下词）</h3>
              
              <!-- 批量输入 -->
              <el-input
                v-model="whitelistText"
                type="textarea"
                :rows="6"
                placeholder="输入关键词，用逗号分隔（例如：官方公告, 版本更新, 重要通知）"
                @blur="parseKeywords('whitelist')"
              />
              
              <!-- 关键词标签 -->
              <div class="keyword-tags">
                <el-tag
                  v-for="(kw, index) in rules.keywordWhitelist"
                  :key="index"
                  closable
                  type="success"
                  @close="removeKeyword('whitelist', index)"
                  style="margin: 5px;"
                >
                  {{ kw }}
                </el-tag>
              </div>
              
              <div class="keyword-actions">
                <el-button size="small" type="success" @click="addKeyword('whitelist')">
                  添加关键词
                </el-button>
                <el-button size="small" @click="clearKeywords('whitelist')">
                  清空
                </el-button>
              </div>
            </el-col>
          </el-row>

          <el-divider />

          <el-checkbox v-model="rules.keywordEnabled">
            启用关键词过滤
          </el-checkbox>
        </el-tab-pane>

        <!-- 正则表达式 -->
        <el-tab-pane label="🔍 正则表达式" name="regex">
          <el-alert
            title="正则表达式功能"
            type="warning"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <template #default>
              正则表达式是高级功能，适合有编程经验的用户。错误的正则表达式可能导致所有消息被过滤。
            </template>
          </el-alert>

          <div class="regex-section">
            <h3>正则表达式规则</h3>
            
            <div v-for="(rule, index) in rules.regexRules" :key="index" class="regex-rule">
              <el-input
                v-model="rule.pattern"
                placeholder="正则表达式（例如：^\\[广告\\].*）"
                style="flex: 1;"
              >
                <template #prepend>模式</template>
              </el-input>
              
              <el-input
                v-model="rule.description"
                placeholder="规则描述"
                style="flex: 1; margin-left: 10px;"
              >
                <template #prepend>说明</template>
              </el-input>
              
              <el-select
                v-model="rule.type"
                placeholder="类型"
                style="width: 120px; margin-left: 10px;"
              >
                <el-option label="黑名单" value="blacklist" />
                <el-option label="白名单" value="whitelist" />
              </el-select>
              
              <el-button
                type="danger"
                :icon="Delete"
                @click="removeRegexRule(index)"
                style="margin-left: 10px;"
              />
            </div>
            
            <el-button @click="addRegexRule" style="width: 100%; margin-top: 10px;">
              <el-icon><Plus /></el-icon> 添加正则规则
            </el-button>
          </div>

          <el-divider />

          <el-checkbox v-model="rules.regexEnabled">
            启用正则表达式过滤
          </el-checkbox>
        </el-tab-pane>

        <!-- 用户过滤 -->
        <el-tab-pane label="👤 用户过滤" name="user">
          <el-row :gutter="20">
            <el-col :span="12">
              <h3>🚫 黑名单用户（不转发这些用户的消息）</h3>
              
              <div class="user-list">
                <div
                  v-for="(user, index) in rules.userBlacklist"
                  :key="index"
                  class="user-item"
                >
                  <span>{{ user }}</span>
                  <el-button
                    type="danger"
                    size="small"
                    :icon="Delete"
                    @click="removeUser('blacklist', index)"
                  />
                </div>
              </div>
              
              <div class="user-actions">
                <el-input
                  v-model="newUserBlacklist"
                  placeholder="输入用户名或ID"
                  @keyup.enter="addUser('blacklist')"
                  style="flex: 1;"
                />
                <el-button @click="addUser('blacklist')" style="margin-left: 10px;">
                  添加
                </el-button>
              </div>
            </el-col>

            <el-col :span="12">
              <h3>✅ 白名单用户（仅转发这些用户的消息）</h3>
              
              <div class="user-list">
                <div
                  v-for="(user, index) in rules.userWhitelist"
                  :key="index"
                  class="user-item"
                >
                  <span>{{ user }}</span>
                  <el-button
                    type="danger"
                    size="small"
                    :icon="Delete"
                    @click="removeUser('whitelist', index)"
                  />
                </div>
              </div>
              
              <div class="user-actions">
                <el-input
                  v-model="newUserWhitelist"
                  placeholder="输入用户名或ID"
                  @keyup.enter="addUser('whitelist')"
                  style="flex: 1;"
                />
                <el-button type="success" @click="addUser('whitelist')" style="margin-left: 10px;">
                  添加
                </el-button>
              </div>
            </el-col>
          </el-row>

          <el-divider />

          <el-checkbox v-model="rules.userEnabled">
            启用用户过滤
          </el-checkbox>
        </el-tab-pane>

        <!-- 消息类型 -->
        <el-tab-pane label="📦 消息类型" name="type">
          <h3>转发的消息类型</h3>
          
          <el-checkbox-group v-model="rules.messageTypes">
            <el-checkbox label="text">文本消息</el-checkbox>
            <el-checkbox label="image">图片消息</el-checkbox>
            <el-checkbox label="link">链接消息</el-checkbox>
            <el-checkbox label="reaction">表情反应</el-checkbox>
            <el-checkbox label="file">文件附件</el-checkbox>
            <el-checkbox label="mention">@提及</el-checkbox>
          </el-checkbox-group>

          <el-divider />

          <h3>特殊规则</h3>
          
          <el-checkbox v-model="rules.onlyMentionAll">
            仅转发@全体成员的消息
          </el-checkbox>
          
          <el-checkbox v-model="rules.ignoreBot">
            忽略Bot发送的消息
          </el-checkbox>
        </el-tab-pane>

        <!-- 测试过滤 -->
        <el-tab-pane label="🧪 测试过滤" name="test">
          <h3>测试过滤规则</h3>
          
          <el-alert
            title="测试说明"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <template #default>
              输入测试消息，查看当前过滤规则是否会拦截该消息。
            </template>
          </el-alert>

          <el-form label-width="100px">
            <el-form-item label="测试消息">
              <el-input
                v-model="testMessage.content"
                type="textarea"
                :rows="4"
                placeholder="输入测试消息内容..."
              />
            </el-form-item>

            <el-form-item label="发送者">
              <el-input
                v-model="testMessage.author"
                placeholder="输入发送者用户名"
              />
            </el-form-item>

            <el-form-item label="消息类型">
              <el-select v-model="testMessage.type">
                <el-option label="文本" value="text" />
                <el-option label="图片" value="image" />
                <el-option label="链接" value="link" />
                <el-option label="文件" value="file" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="runTest" :loading="isTesting">
                <el-icon><VideoPlay /></el-icon> 运行测试
              </el-button>
              <el-button @click="clearTest">
                清空
              </el-button>
            </el-form-item>
          </el-form>

          <el-divider />

          <div v-if="testResult" class="test-result">
            <el-result
              :icon="testResult.passed ? 'success' : 'error'"
              :title="testResult.passed ? '✅ 消息会被转发' : '❌ 消息会被拦截'"
              :sub-title="testResult.reason"
            >
              <template #extra v-if="!testResult.passed">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="拦截原因">
                    {{ testResult.reason }}
                  </el-descriptions-item>
                  <el-descriptions-item label="匹配规则">
                    {{ testResult.matchedRule || '无' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="建议">
                    {{ testResult.suggestion || '检查过滤规则设置' }}
                  </el-descriptions-item>
                </el-descriptions>
              </template>
            </el-result>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 规则模板对话框 -->
    <el-dialog v-model="templateDialogVisible" title="过滤规则模板" width="600px">
      <el-radio-group v-model="selectedTemplate" style="width: 100%;">
        <el-radio
          v-for="template in templates"
          :key="template.id"
          :label="template.id"
          style="display: block; margin-bottom: 15px;"
        >
          <div>
            <strong>{{ template.name }}</strong>
            <p style="margin: 5px 0; color: #909399; font-size: 12px;">
              {{ template.description }}
            </p>
          </div>
        </el-radio>
      </el-radio-group>

      <template #footer>
        <el-button @click="templateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="applyTemplate">应用模板</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Check, Delete, Plus, Document, VideoPlay
} from '@element-plus/icons-vue';
import axios from 'axios';

// 数据
const activeTab = ref('keyword');
const isSaving = ref(false);
const isTesting = ref(false);

// 规则
const rules = ref({
  keywordBlacklist: [],
  keywordWhitelist: [],
  keywordEnabled: true,
  
  regexRules: [],
  regexEnabled: false,
  
  userBlacklist: [],
  userWhitelist: [],
  userEnabled: false,
  
  messageTypes: ['text', 'image', 'link', 'file'],
  onlyMentionAll: false,
  ignoreBot: false
});

// 文本输入
const blacklistText = ref('');
const whitelistText = ref('');
const newUserBlacklist = ref('');
const newUserWhitelist = ref('');

// 测试
const testMessage = ref({
  content: '',
  author: '',
  type: 'text'
});
const testResult = ref(null);

// 模板
const templateDialogVisible = ref(false);
const selectedTemplate = ref('');
const templates = ref([
  {
    id: 'strict',
    name: '严格模式',
    description: '拦截所有广告、代练、外挂等垃圾消息',
    rules: {
      keywordBlacklist: ['广告', '代练', '外挂', '刷钻', '代刷', '卖号', '买号'],
      keywordEnabled: true
    }
  },
  {
    id: 'official_only',
    name: '仅官方公告',
    description: '只转发包含"官方"、"公告"等关键词的消息',
    rules: {
      keywordWhitelist: ['官方公告', '版本更新', '重要通知', '系统维护'],
      keywordEnabled: true
    }
  },
  {
    id: 'no_bot',
    name: '忽略Bot消息',
    description: '不转发来自Bot的消息',
    rules: {
      ignoreBot: true
    }
  }
]);

// 方法
const parseKeywords = (type) => {
  const text = type === 'blacklist' ? blacklistText.value : whitelistText.value;
  const keywords = text.split(',').map(k => k.trim()).filter(k => k);
  
  if (type === 'blacklist') {
    rules.value.keywordBlacklist = [...new Set([...rules.value.keywordBlacklist, ...keywords])];
  } else {
    rules.value.keywordWhitelist = [...new Set([...rules.value.keywordWhitelist, ...keywords])];
  }
};

const addKeyword = (type) => {
  ElMessageBox.prompt('请输入关键词', '添加关键词').then(({ value }) => {
    if (value) {
      if (type === 'blacklist') {
        rules.value.keywordBlacklist.push(value);
      } else {
        rules.value.keywordWhitelist.push(value);
      }
    }
  }).catch(() => {});
};

const removeKeyword = (type, index) => {
  if (type === 'blacklist') {
    rules.value.keywordBlacklist.splice(index, 1);
  } else {
    rules.value.keywordWhitelist.splice(index, 1);
  }
};

const clearKeywords = (type) => {
  ElMessageBox.confirm('确定要清空所有关键词吗？', '确认', {
    type: 'warning'
  }).then(() => {
    if (type === 'blacklist') {
      rules.value.keywordBlacklist = [];
      blacklistText.value = '';
    } else {
      rules.value.keywordWhitelist = [];
      whitelistText.value = '';
    }
  }).catch(() => {});
};

const addRegexRule = () => {
  rules.value.regexRules.push({
    pattern: '',
    description: '',
    type: 'blacklist'
  });
};

const removeRegexRule = (index) => {
  rules.value.regexRules.splice(index, 1);
};

const addUser = (type) => {
  const value = type === 'blacklist' ? newUserBlacklist.value : newUserWhitelist.value;
  
  if (value) {
    if (type === 'blacklist') {
      rules.value.userBlacklist.push(value);
      newUserBlacklist.value = '';
    } else {
      rules.value.userWhitelist.push(value);
      newUserWhitelist.value = '';
    }
  }
};

const removeUser = (type, index) => {
  if (type === 'blacklist') {
    rules.value.userBlacklist.splice(index, 1);
  } else {
    rules.value.userWhitelist.splice(index, 1);
  }
};

const runTest = async () => {
  if (!testMessage.value.content) {
    ElMessage.warning('请输入测试消息');
    return;
  }
  
  isTesting.value = true;
  
  try {
    const response = await axios.post('http://localhost:9527/api/filter/test', {
      message: testMessage.value,
      rules: rules.value
    });
    
    testResult.value = response.data;
  } catch (error) {
    ElMessage.error(`测试失败：${error.message}`);
  } finally {
    isTesting.value = false;
  }
};

const clearTest = () => {
  testMessage.value = {
    content: '',
    author: '',
    type: 'text'
  };
  testResult.value = null;
};

const loadTemplate = () => {
  templateDialogVisible.value = true;
};

const applyTemplate = () => {
  const template = templates.value.find(t => t.id === selectedTemplate.value);
  
  if (template) {
    Object.assign(rules.value, template.rules);
    ElMessage.success(`已应用模板：${template.name}`);
    templateDialogVisible.value = false;
  }
};

const saveRules = async () => {
  isSaving.value = true;
  
  try {
    await axios.post('http://localhost:9527/api/filter/rules', rules.value);
    ElMessage.success('过滤规则保存成功');
  } catch (error) {
    ElMessage.error(`保存失败：${error.message}`);
  } finally {
    isSaving.value = false;
  }
};

const loadRules = async () => {
  try {
    const response = await axios.get('http://localhost:9527/api/filter/rules');
    Object.assign(rules.value, response.data);
    
    // 同步到文本框
    blacklistText.value = rules.value.keywordBlacklist.join(', ');
    whitelistText.value = rules.value.keywordWhitelist.join(', ');
  } catch (error) {
    console.error('加载过滤规则失败:', error);
  }
};

onMounted(() => {
  loadRules();
});
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

.header-actions {
  display: flex;
  gap: 10px;
}

.keyword-tags {
  min-height: 80px;
  padding: 10px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  margin: 10px 0;
}

.keyword-actions {
  display: flex;
  gap: 10px;
}

.regex-section {
  margin: 20px 0;
}

.regex-rule {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.user-list {
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  margin-bottom: 5px;
  background: #f5f7fa;
  border-radius: 4px;
}

.user-actions {
  display: flex;
  align-items: center;
}

.test-result {
  margin-top: 20px;
}
</style>
