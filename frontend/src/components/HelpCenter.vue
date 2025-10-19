<template>
  <el-dialog
    v-model="visible"
    title="📚 帮助中心"
    width="900px"
    :close-on-click-modal="false"
  >
    <el-tabs v-model="activeTab" type="card">
      <!-- 视频教程 -->
      <el-tab-pane label="视频教程" name="videos">
        <div class="tutorial-grid">
          <el-card
            v-for="tutorial in tutorials"
            :key="tutorial.id"
            class="tutorial-card"
            shadow="hover"
          >
            <template #header>
              <div class="tutorial-header">
                <span>{{ tutorial.icon }} {{ tutorial.title }}</span>
                <el-tag size="small" :type="tutorial.difficulty === 'easy' ? 'success' : 'warning'">
                  {{ difficultyText[tutorial.difficulty] }}
                </el-tag>
              </div>
            </template>

            <div class="tutorial-content">
              <p class="tutorial-description">{{ tutorial.description }}</p>
              <div class="tutorial-info">
                <span>⏱️ {{ tutorial.duration }}</span>
                <span>👁️ {{ tutorial.views }}次观看</span>
              </div>
            </div>

            <template #footer>
              <div class="tutorial-actions">
                <el-button type="primary" size="small" @click="openTutorial(tutorial)">
                  <el-icon><VideoPlay /></el-icon>
                  观看视频
                </el-button>
                <el-button size="small" @click="openDocument(tutorial.doc_link)">
                  <el-icon><Document /></el-icon>
                  图文版
                </el-button>
              </div>
            </template>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 图文教程 -->
      <el-tab-pane label="图文教程" name="docs">
        <el-collapse v-model="activeDoc" accordion>
          <el-collapse-item
            v-for="doc in documents"
            :key="doc.id"
            :name="doc.id"
          >
            <template #title>
              <div class="doc-title">
                <span>{{ doc.icon }} {{ doc.title }}</span>
              </div>
            </template>
            <div class="doc-content" v-html="doc.content"></div>
            <div style="margin-top: 15px">
              <el-button type="primary" size="small" @click="openFullDoc(doc.link)">
                查看完整文档
              </el-button>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-tab-pane>

      <!-- 常见问题 -->
      <el-tab-pane label="常见问题" name="faq">
        <el-input
          v-model="faqSearch"
          placeholder="搜索问题..."
          clearable
          style="margin-bottom: 20px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-collapse v-model="activeFaq" accordion>
          <el-collapse-item
            v-for="faq in filteredFaqs"
            :key="faq.id"
            :name="faq.id"
          >
            <template #title>
              <div class="faq-title">
                <el-icon><QuestionFilled /></el-icon>
                <span>{{ faq.question }}</span>
                <el-tag v-if="faq.hot" size="small" type="danger" effect="dark">热门</el-tag>
              </div>
            </template>
            <div class="faq-answer" v-html="faq.answer"></div>
          </el-collapse-item>
        </el-collapse>

        <el-empty v-if="filteredFaqs.length === 0" description="未找到相关问题" />
      </el-tab-pane>

      <!-- 快捷操作 -->
      <el-tab-pane label="快捷操作" name="shortcuts">
        <el-row :gutter="20">
          <el-col :span="12" v-for="shortcut in shortcuts" :key="shortcut.id">
            <el-card class="shortcut-card" shadow="hover">
              <div class="shortcut-icon">{{ shortcut.icon }}</div>
              <h4>{{ shortcut.title }}</h4>
              <p>{{ shortcut.description }}</p>
              <el-button type="primary" size="small" @click="handleShortcut(shortcut.action)">
                {{ shortcut.buttonText }}
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 联系支持 -->
      <el-tab-pane label="联系支持" name="contact">
        <div class="contact-section">
          <el-result icon="info" title="需要帮助？">
            <template #extra>
              <div class="contact-methods">
                <el-card class="contact-card">
                  <template #header>
                    <el-icon><ChatLineRound /></el-icon>
                    <span>在线反馈</span>
                  </template>
                  <p>通过GitHub Issues提交问题或建议</p>
                  <el-button type="primary" @click="openGitHubIssues">
                    提交Issue
                  </el-button>
                </el-card>

                <el-card class="contact-card">
                  <template #header>
                    <el-icon><Message /></el-icon>
                    <span>邮件联系</span>
                  </template>
                  <p>发送邮件至：support@example.com</p>
                  <el-button type="primary" @click="openEmail">
                    发送邮件
                  </el-button>
                </el-card>

                <el-card class="contact-card">
                  <template #header>
                    <el-icon><Link /></el-icon>
                    <span>查看文档</span>
                  </template>
                  <p>访问完整的在线文档</p>
                  <el-button type="primary" @click="openDocs">
                    打开文档
                  </el-button>
                </el-card>
              </div>
            </template>
          </el-result>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  VideoPlay,
  Document,
  Search,
  QuestionFilled,
  ChatLineRound,
  Message,
  Link
} from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])
const router = useRouter()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const activeTab = ref('videos')
const activeDoc = ref('')
const activeFaq = ref('')
const faqSearch = ref('')

const difficultyText = {
  easy: '简单',
  medium: '中级',
  hard: '进阶'
}

// 视频教程数据
const tutorials = ref([
  {
    id: 1,
    icon: '🎬',
    title: '完整配置演示',
    description: '从零开始完成所有配置，适合新手观看',
    duration: '10分钟',
    views: 1523,
    difficulty: 'easy',
    video_link: 'https://example.com/tutorial1',
    doc_link: '/docs/quick-start'
  },
  {
    id: 2,
    icon: '🍪',
    title: 'Cookie获取教程',
    description: '详细讲解如何获取KOOK账号Cookie',
    duration: '3分钟',
    views: 2341,
    difficulty: 'easy',
    video_link: 'https://example.com/tutorial2',
    doc_link: '/docs/cookie-guide'
  },
  {
    id: 3,
    icon: '💬',
    title: 'Discord配置教程',
    description: '如何创建Discord Webhook并配置',
    duration: '2分钟',
    views: 1876,
    difficulty: 'easy',
    video_link: 'https://example.com/tutorial3',
    doc_link: '/docs/discord-setup'
  },
  {
    id: 4,
    icon: '✈️',
    title: 'Telegram配置教程',
    description: '创建Telegram Bot并获取Chat ID',
    duration: '4分钟',
    views: 1654,
    difficulty: 'easy',
    video_link: 'https://example.com/tutorial4',
    doc_link: '/docs/telegram-setup'
  },
  {
    id: 5,
    icon: '🐦',
    title: '飞书配置教程',
    description: '飞书自建应用创建和配置',
    duration: '5分钟',
    views: 987,
    difficulty: 'medium',
    video_link: 'https://example.com/tutorial5',
    doc_link: '/docs/feishu-setup'
  },
  {
    id: 6,
    icon: '🔀',
    title: '频道映射设置',
    description: '学习如何设置频道映射关系',
    duration: '3分钟',
    views: 1432,
    difficulty: 'easy',
    video_link: 'https://example.com/tutorial6',
    doc_link: '/docs/channel-mapping'
  },
  {
    id: 7,
    icon: '🔧',
    title: '高级设置和优化',
    description: '深入了解系统设置和性能优化',
    duration: '8分钟',
    views: 765,
    difficulty: 'hard',
    video_link: 'https://example.com/tutorial7',
    doc_link: '/docs/advanced-settings'
  },
  {
    id: 8,
    icon: '🐛',
    title: '故障排查指南',
    description: '常见问题的诊断和解决方法',
    duration: '6分钟',
    views: 1098,
    difficulty: 'medium',
    video_link: 'https://example.com/tutorial8',
    doc_link: '/docs/troubleshooting'
  }
])

// 图文文档数据
const documents = ref([
  {
    id: 1,
    icon: '📘',
    title: '快速入门指南',
    content: '<p>5分钟快速上手KOOK消息转发系统...</p>',
    link: '/docs/quick-start'
  },
  {
    id: 2,
    icon: '📗',
    title: '完整用户手册',
    content: '<p>详细的功能说明和使用技巧...</p>',
    link: '/docs/user-manual'
  },
  {
    id: 3,
    icon: '📕',
    title: '开发者文档',
    content: '<p>API接口文档和扩展开发指南...</p>',
    link: '/docs/developer-guide'
  }
])

// 常见问题数据
const faqs = ref([
  {
    id: 1,
    question: 'KOOK账号一直显示"离线"怎么办？',
    answer: `
      <p>可能的原因和解决方法：</p>
      <ol>
        <li><strong>Cookie已过期</strong> → 重新登录获取新Cookie</li>
        <li><strong>IP被限制</strong> → 更换网络或使用代理</li>
        <li><strong>账号被封禁</strong> → 联系KOOK客服</li>
        <li><strong>网络不稳定</strong> → 检查网络连接</li>
      </ol>
    `,
    hot: true
  },
  {
    id: 2,
    question: '消息转发延迟很大（超过10秒）？',
    answer: `
      <p>可能的原因：</p>
      <ul>
        <li>消息队列积压 → 查看队列状态，等待消化</li>
        <li>目标平台限流 → 降低频道映射数量</li>
        <li>网络不稳定 → 检查网络连接</li>
      </ul>
    `,
    hot: true
  },
  {
    id: 3,
    question: '图片转发失败怎么办？',
    answer: `
      <p>解决方法：</p>
      <ol>
        <li>检查图片大小（建议小于10MB）</li>
        <li>切换图片处理策略（设置→图片处理）</li>
        <li>检查目标平台是否支持该图片格式</li>
      </ol>
    `,
    hot: false
  },
  {
    id: 4,
    question: '如何备份配置？',
    answer: `
      <p>配置备份方法：</p>
      <ol>
        <li>进入"设置"页面</li>
        <li>找到"备份与恢复"部分</li>
        <li>点击"立即备份配置"</li>
        <li>保存生成的JSON文件</li>
      </ol>
    `,
    hot: false
  }
])

// 过滤后的FAQ
const filteredFaqs = computed(() => {
  if (!faqSearch.value) return faqs.value
  
  const keyword = faqSearch.value.toLowerCase()
  return faqs.value.filter(faq => 
    faq.question.toLowerCase().includes(keyword) ||
    faq.answer.toLowerCase().includes(keyword)
  )
})

// 快捷操作
const shortcuts = ref([
  {
    id: 1,
    icon: '👤',
    title: '添加KOOK账号',
    description: '快速添加新的KOOK账号',
    buttonText: '前往添加',
    action: 'add-account'
  },
  {
    id: 2,
    icon: '🤖',
    title: '配置机器人',
    description: '添加Discord/Telegram/飞书Bot',
    buttonText: '前往配置',
    action: 'config-bot'
  },
  {
    id: 3,
    icon: '🔀',
    title: '设置映射',
    description: '配置频道转发映射关系',
    buttonText: '前往设置',
    action: 'setup-mapping'
  },
  {
    id: 4,
    icon: '📋',
    title: '查看日志',
    description: '查看消息转发日志',
    buttonText: '前往查看',
    action: 'view-logs'
  }
])

// 打开视频教程
const openTutorial = (tutorial) => {
  ElMessage.info(`视频教程：${tutorial.title}（开发中，将打开：${tutorial.video_link}）`)
  // 实际实现：window.open(tutorial.video_link, '_blank')
}

// 打开文档
const openDocument = (link) => {
  ElMessage.info(`打开文档：${link}（开发中）`)
}

// 打开完整文档
const openFullDoc = (link) => {
  ElMessage.info(`打开完整文档：${link}（开发中）`)
}

// 处理快捷操作
const handleShortcut = (action) => {
  const routes = {
    'add-account': '/accounts',
    'config-bot': '/bots',
    'setup-mapping': '/mapping',
    'view-logs': '/logs'
  }
  
  if (routes[action]) {
    router.push(routes[action])
    visible.value = false
  }
}

// 打开GitHub Issues
const openGitHubIssues = () => {
  window.open('https://github.com/gfchfjh/CSBJJWT/issues', '_blank')
}

// 打开邮件
const openEmail = () => {
  window.location.href = 'mailto:support@example.com'
}

// 打开文档
const openDocs = () => {
  ElMessage.info('文档中心开发中')
}
</script>

<style scoped>
.tutorial-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  max-height: 600px;
  overflow-y: auto;
}

.tutorial-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tutorial-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tutorial-content {
  flex: 1;
}

.tutorial-description {
  color: #606266;
  margin-bottom: 15px;
  font-size: 14px;
}

.tutorial-info {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #909399;
}

.tutorial-actions {
  display: flex;
  gap: 10px;
}

.doc-title,
.faq-title {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.doc-content,
.faq-answer {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  line-height: 1.8;
}

.doc-content :deep(p),
.faq-answer :deep(p) {
  margin: 10px 0;
}

.doc-content :deep(ol),
.faq-answer :deep(ol),
.doc-content :deep(ul),
.faq-answer :deep(ul) {
  margin: 10px 0;
  padding-left: 25px;
}

.doc-content :deep(li),
.faq-answer :deep(li) {
  margin: 5px 0;
}

.shortcut-card {
  text-align: center;
  padding: 20px;
  margin-bottom: 20px;
}

.shortcut-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.shortcut-card h4 {
  margin: 10px 0;
  color: #303133;
}

.shortcut-card p {
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
}

.contact-section {
  padding: 20px;
}

.contact-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.contact-card {
  text-align: center;
}

.contact-card :deep(.el-card__header) {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  font-weight: bold;
}

.contact-card p {
  margin: 15px 0;
  color: #606266;
}
</style>
