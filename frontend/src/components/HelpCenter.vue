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
                <el-button 
                  :type="tutorial.video_status === 'available' ? 'primary' : 'info'" 
                  size="small" 
                  @click="openTutorial(tutorial)"
                  :disabled="tutorial.video_status === 'placeholder'"
                >
                  <el-icon><VideoPlay /></el-icon>
                  {{ tutorial.video_status === 'placeholder' ? '视频制作中' : '观看视频' }}
                </el-button>
                <el-button size="small" @click="openDocument(tutorial.doc_link)">
                  <el-icon><Document /></el-icon>
                  图文版
                </el-button>
                <el-button 
                  v-if="tutorial.video_status === 'placeholder'"
                  size="small" 
                  type="success"
                  @click="showRecordingGuide(tutorial)"
                >
                  <el-icon><Memo /></el-icon>
                  录制脚本
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
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  VideoPlay,
  Document,
  Search,
  QuestionFilled,
  ChatLineRound,
  Message,
  Link,
  Memo
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
    title: '快速入门教程',
    description: '5分钟快速上手KOOK消息转发系统，从安装到首次使用',
    duration: '5分钟',
    views: 1523,
    difficulty: 'easy',
    video_url: 'https://www.bilibili.com/video/BV1xxxxxxxxx',  // 待录制后更新
    video_status: 'placeholder',  // placeholder(制作中)/available(可用)/coming_soon(即将上线)
    doc_link: '/docs/完整用户手册.md',
    tags: ['新手必看', '安装', '配置']
  },
  {
    id: 2,
    icon: '🍪',
    title: 'Cookie获取教程',
    description: '详细讲解如何从浏览器获取KOOK Cookie，支持Chrome/Edge/Firefox',
    duration: '3分钟',
    views: 892,
    difficulty: 'easy',
    video_url: 'https://www.bilibili.com/video/BV2xxxxxxxxx',
    video_status: 'placeholder',
    doc_link: '/docs/完整用户手册.md',
    tags: ['账号登录', 'Cookie']
  },
  {
    id: 3,
    icon: '💬',
    title: 'Discord Webhook配置',
    description: '如何创建Discord Webhook并配置到本系统',
    duration: '2分钟',
    views: 1876,
    difficulty: 'easy',
    video_url: 'https://www.bilibili.com/video/BV3xxxxxxxxx',
    video_status: 'placeholder',
    doc_link: '/docs/Discord配置教程.md',
    tags: ['Discord', 'Webhook']
  },
  {
    id: 4,
    icon: '✈️',
    title: 'Telegram Bot配置',
    description: '与BotFather创建Bot，获取Token和Chat ID',
    duration: '4分钟',
    views: 1654,
    difficulty: 'easy',
    video_url: 'https://www.bilibili.com/video/BV4xxxxxxxxx',
    video_status: 'placeholder',
    doc_link: '/docs/Telegram配置教程.md',
    tags: ['Telegram', 'Bot']
  },
  {
    id: 5,
    icon: '🐦',
    title: '飞书应用配置',
    description: '在飞书开放平台创建自建应用并配置',
    duration: '5分钟',
    views: 987,
    difficulty: 'medium',
    video_url: 'https://www.bilibili.com/video/BV5xxxxxxxxx',
    video_status: 'placeholder',
    doc_link: '/docs/飞书配置教程.md',
    tags: ['飞书', '自建应用']
  },
  {
    id: 6,
    icon: '🔀',
    title: '频道映射配置详解',
    description: '传统映射和拖拽映射两种方式的使用',
    duration: '5分钟',
    views: 1432,
    difficulty: 'easy',
    video_url: 'https://www.bilibili.com/video/BV6xxxxxxxxx',
    video_status: 'placeholder',
    doc_link: '/docs/用户手册.md',
    tags: ['频道映射', '拖拽']
  },
  {
    id: 7,
    icon: '🎯',
    title: '过滤规则使用技巧',
    description: '关键词、用户、消息类型过滤的实用技巧',
    duration: '4分钟',
    views: 765,
    difficulty: 'easy',
    video_url: 'https://www.bilibili.com/video/BV7xxxxxxxxx',
    video_status: 'placeholder',
    doc_link: '/docs/用户手册.md',
    tags: ['过滤规则', '技巧']
  },
  {
    id: 8,
    icon: '🐛',
    title: '常见问题排查',
    description: 'Cookie过期、转发失败、图片上传等问题的解决',
    duration: '7分钟',
    views: 1098,
    difficulty: 'medium',
    video_url: 'https://www.bilibili.com/video/BV8xxxxxxxxx',
    video_status: 'placeholder',
    doc_link: '/docs/用户手册.md',
    tags: ['故障排查', 'FAQ']
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
  if (tutorial.video_status === 'placeholder') {
    ElMessageBox.alert(
      '<div style="text-align: left;">' +
      '<p><strong>📹 视频教程正在制作中</strong></p>' +
      '<p>我们正在努力录制这个视频教程，预计将在近期完成。</p>' +
      '<p><strong>您可以：</strong></p>' +
      '<ul style="padding-left: 20px; margin: 10px 0;">' +
      '<li>点击"图文版"按钮查看详细的图文教程</li>' +
      '<li>点击"录制脚本"查看视频内容大纲</li>' +
      '<li>关注项目获取最新进展</li>' +
      '</ul>' +
      '<p style="margin-top: 15px; color: #67C23A;">' +
      '💡 如果您有录制视频的能力，欢迎贡献教程！' +
      '</p>' +
      '</div>',
      '视频制作中',
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '查看图文教程',
        cancelButtonText: '知道了',
        showCancelButton: true,
        type: 'info'
      }
    ).then(() => {
      openDocument(tutorial.doc_link)
    }).catch(() => {})
  } else if (tutorial.video_url && tutorial.video_status === 'available') {
    window.open(tutorial.video_url, '_blank')
    // 记录观看次数
    tutorial.views++
  } else {
    ElMessage.info('视频教程即将上线，敬请期待！')
  }
}

// 显示录制指南
const showRecordingGuide = (tutorial) => {
  ElMessageBox.alert(
    '<div style="text-align: left; max-height: 500px; overflow-y: auto;">' +
    `<h3 style="margin-top: 0;">📝 ${tutorial.title} - 录制脚本</h3>` +
    '<p><strong>录制要点：</strong></p>' +
    '<ul style="padding-left: 20px; margin: 10px 0;">' +
    '<li>分辨率：1920x1080（高清）</li>' +
    '<li>时长：' + tutorial.duration + '</li>' +
    '<li>语速：适中，吐字清晰</li>' +
    '<li>建议添加中文字幕</li>' +
    '<li>工具：OBS Studio（免费）或 ScreenFlow</li>' +
    '</ul>' +
    '<p><strong>录制内容：</strong></p>' +
    '<div style="background: #f5f5f5; padding: 15px; border-radius: 4px; margin: 10px 0;">' +
    getRecordingScript(tutorial.id) +
    '</div>' +
    '<p style="margin-top: 15px;"><strong>📚 参考文档：</strong></p>' +
    '<p><a href="' + tutorial.doc_link + '" style="color: #409EFF;">点击查看详细图文教程</a></p>' +
    '<p style="margin-top: 15px; color: #909399; font-size: 12px;">' +
    '💡 完整的录制指南请查看：docs/视频教程录制指南.md' +
    '</p>' +
    '</div>',
    '录制脚本',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭',
      customClass: 'recording-guide-dialog'
    }
  )
}

// 获取录制脚本内容
const getRecordingScript = (tutorialId) => {
  const scripts = {
    1: '<p><strong>第1部分：欢迎和简介（30秒）</strong></p><p>- 欢迎观看KOOK消息转发系统快速入门教程<br/>- 本教程将带您5分钟快速上手<br/>- 您将学会：安装、配置账号、设置转发</p><p><strong>第2部分：安装演示（1分钟）</strong></p><p>- 展示下载安装包<br/>- 演示Windows安装过程<br/>- 首次启动界面</p><p><strong>第3部分：配置向导（2分钟）</strong></p><p>- 步骤1：阅读免责声明<br/>- 步骤2：添加KOOK账号<br/>- 步骤3：选择服务器和频道<br/>- 步骤4：配置Discord Webhook<br/>- 步骤5：完成配置</p><p><strong>第4部分：测试转发（1分钟）</strong></p><p>- 在KOOK发送测试消息<br/>- 查看Discord接收<br/>- 查看实时日志</p><p><strong>第5部分：总结（30秒）</strong></p><p>- 恭喜您已成功配置！<br/>- 更多教程请观看其他视频</p>',
    2: '<p><strong>第1部分：简介（20秒）</strong></p><p>- 为什么需要Cookie<br/>- Cookie是什么</p><p><strong>第2部分：Chrome浏览器（1分钟）</strong></p><p>- 打开kookapp.cn并登录<br/>- 按F12打开开发者工具<br/>- Application → Cookies<br/>- 全选并复制</p><p><strong>第3部分：Edge/Firefox浏览器（1分钟）</strong></p><p>- 步骤类似展示</p><p><strong>第4部分：导入软件（40秒）</strong></p><p>- 粘贴Cookie<br/>- 验证成功</p>',
    3: '<p><strong>第1部分：创建Webhook（1分钟）</strong></p><p>- Discord服务器设置<br/>- 集成 → Webhooks<br/>- 新建Webhook<br/>- 复制URL</p><p><strong>第2部分：配置到软件（1分钟）</strong></p><p>- 打开机器人配置<br/>- 粘贴URL<br/>- 测试连接</p>',
    4: '<p><strong>第1部分：创建Bot（2分钟）</strong></p><p>- 搜索@BotFather<br/>- /newbot命令<br/>- 设置名称<br/>- 获取Token</p><p><strong>第2部分：获取Chat ID（1分钟）</strong></p><p>- 添加Bot到群组<br/>- 使用工具获取ID</p><p><strong>第3部分：配置（1分钟）</strong></p><p>- 填入Token和ID<br/>- 测试</p>',
    5: '<p><strong>第1部分：创建应用（2分钟）</strong></p><p>- 飞书开放平台<br/>- 创建自建应用<br/>- 开启机器人<br/>- 获取凭证</p><p><strong>第2部分：配置权限（1分钟）</strong></p><p>- 消息权限<br/>- 图片权限</p><p><strong>第3部分：配置到软件（2分钟）</strong></p><p>- 填入App ID/Secret<br/>- 测试连接</p>',
    6: '<p><strong>第1部分：传统映射（2分钟）</strong></p><p>- 选择KOOK频道<br/>- 选择目标平台<br/>- 填写频道ID<br/>- 保存</p><p><strong>第2部分：拖拽映射（2分钟）</strong></p><p>- 拖拽操作<br/>- 可视化连接<br/>- 一对多支持</p><p><strong>第3部分：测试（1分钟）</strong></p><p>- 发送测试消息</p>',
    7: '<p><strong>第1部分：关键词过滤（1.5分钟）</strong></p><p>- 黑名单设置<br/>- 白名单设置</p><p><strong>第2部分：用户过滤（1分钟）</strong></p><p>- 用户黑白名单</p><p><strong>第3部分：消息类型过滤（1分钟）</strong></p><p>- 选择消息类型</p><p><strong>第4部分：技巧（30秒）</strong></p><p>- 规则优先级</p>',
    8: '<p><strong>第1部分：Cookie过期（2分钟）</strong></p><p>- 判断过期<br/>- 重新获取</p><p><strong>第2部分：转发失败（2分钟）</strong></p><p>- 查看日志<br/>- 检查配置<br/>- 网络测试</p><p><strong>第3部分：图片问题（1.5分钟）</strong></p><p>- 大小限制<br/>- 切换策略</p><p><strong>第4部分：其他问题（1.5分钟）</strong></p><p>- 服务启动<br/>- Redis连接</p>'
  }
  
  return scripts[tutorialId] || '<p>暂无详细脚本，请参考图文教程</p>'
}

// 打开文档
const openDocument = (link) => {
  ElMessage.info(`打开文档：${link}（功能开发中）`)
  // 实际实现可以跳转到文档页面或打开外部链接
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
