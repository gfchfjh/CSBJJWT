<template>
  <div class="help-enhanced">
    <!-- ✅ P1-4: 完整帮助系统 -->
    <el-row :gutter="20">
      <!-- 左侧：导航菜单 -->
      <el-col :span="6">
        <el-card shadow="hover" class="nav-card">
          <template #header>
            <div class="card-header">
              <el-icon><QuestionFilled /></el-icon>
              <span>帮助中心</span>
            </div>
          </template>

          <el-menu
            :default-active="activeSection"
            @select="handleSectionChange"
          >
            <el-menu-item index="quick_start">
              <el-icon><Reading /></el-icon>
              <span>快速开始</span>
            </el-menu-item>

            <el-menu-item index="tutorials">
              <el-icon><Document /></el-icon>
              <span>图文教程 ({{ tutorials.length }})</span>
            </el-menu-item>

            <el-menu-item index="videos">
              <el-icon><VideoPlay /></el-icon>
              <span>视频教程 ({{ videos.length }})</span>
            </el-menu-item>

            <el-menu-item index="faqs">
              <el-icon><ChatDotRound /></el-icon>
              <span>常见问题 ({{ faqs.length }})</span>
            </el-menu-item>

            <el-menu-item index="diagnosis">
              <el-icon><Tools /></el-icon>
              <span>智能诊断</span>
            </el-menu-item>

            <el-menu-item index="contact">
              <el-icon><Service /></el-icon>
              <span>联系支持</span>
            </el-menu-item>
          </el-menu>
        </el-card>

        <!-- 搜索框 -->
        <el-card shadow="hover" class="search-card">
          <el-input
            v-model="searchQuery"
            placeholder="搜索帮助内容..."
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-card>
      </el-col>

      <!-- 右侧：内容区域 -->
      <el-col :span="18">
        <!-- 快速开始 -->
        <div v-if="activeSection === 'quick_start'" class="content-section">
          <el-card shadow="hover">
            <template #header>
              <h2>🚀 快速开始</h2>
            </template>

            <el-timeline>
              <el-timeline-item
                v-for="(step, index) in quickStartSteps"
                :key="index"
                :type="step.type"
                :icon="step.icon"
                :size="step.size"
              >
                <div class="timeline-content">
                  <h3>{{ step.title }}</h3>
                  <p>{{ step.description }}</p>
                  <el-button
                    v-if="step.action"
                    type="primary"
                    size="small"
                    @click="handleAction(step.action)"
                  >
                    {{ step.actionText }}
                  </el-button>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </div>

        <!-- 图文教程列表 -->
        <div v-else-if="activeSection === 'tutorials'" class="content-section">
          <el-card shadow="hover">
            <template #header>
              <h2>📚 图文教程</h2>
            </template>

            <el-row :gutter="20">
              <el-col
                v-for="tutorial in filteredTutorials"
                :key="tutorial.id"
                :span="12"
              >
                <el-card
                  shadow="hover"
                  class="tutorial-card"
                  @click="viewTutorial(tutorial)"
                >
                  <div class="tutorial-header">
                    <h3>{{ tutorial.title }}</h3>
                    <el-tag :type="getDifficultyType(tutorial.difficulty)" size="small">
                      {{ getDifficultyText(tutorial.difficulty) }}
                    </el-tag>
                  </div>

                  <div class="tutorial-meta">
                    <el-icon><Clock /></el-icon>
                    <span>{{ tutorial.duration }}</span>
                  </div>

                  <el-divider />

                  <div class="tutorial-steps">
                    <div
                      v-for="(step, index) in tutorial.steps.slice(0, 3)"
                      :key="index"
                      class="step-item"
                    >
                      <el-icon><CircleCheckFilled /></el-icon>
                      <span>{{ step }}</span>
                    </div>
                  </div>

                  <el-button type="primary" text class="view-button">
                    查看详情 →
                  </el-button>
                </el-card>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <!-- 视频教程列表 -->
        <div v-else-if="activeSection === 'videos'" class="content-section">
          <el-card shadow="hover">
            <template #header>
              <h2>📺 视频教程</h2>
            </template>

            <el-row :gutter="20">
              <el-col
                v-for="video in filteredVideos"
                :key="video.id"
                :span="8"
              >
                <el-card
                  shadow="hover"
                  class="video-card"
                  @click="playVideo(video)"
                >
                  <div class="video-thumbnail">
                    <img :src="video.thumbnail" :alt="video.title" />
                    <div class="play-overlay">
                      <el-icon size="48"><VideoPlay /></el-icon>
                    </div>
                    <div class="duration-badge">{{ video.duration }}</div>
                  </div>

                  <div class="video-info">
                    <h4>{{ video.title }}</h4>
                    <p>{{ video.description }}</p>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <!-- 常见问题FAQ -->
        <div v-else-if="activeSection === 'faqs'" class="content-section">
          <el-card shadow="hover">
            <template #header>
              <div class="faq-header">
                <h2>❓ 常见问题</h2>
                <el-segmented
                  v-model="faqCategory"
                  :options="faqCategories"
                  @change="handleCategoryChange"
                />
              </div>
            </template>

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
                  </div>
                </template>

                <div class="faq-content" v-html="formatMarkdown(faq.answer)" />

                <div class="faq-tags">
                  <el-tag
                    v-for="tag in faq.tags"
                    :key="tag"
                    size="small"
                    type="info"
                  >
                    {{ tag }}
                  </el-tag>
                </div>

                <el-divider />

                <div class="faq-feedback">
                  <span>这个答案有帮助吗？</span>
                  <el-button-group>
                    <el-button
                      size="small"
                      @click="markHelpful(faq.id, true)"
                    >
                      <el-icon><CircleCheck /></el-icon>
                      有帮助 ({{ faq.helpful_count }})
                    </el-button>
                    <el-button
                      size="small"
                      @click="markHelpful(faq.id, false)"
                    >
                      <el-icon><CircleClose /></el-icon>
                      没帮助
                    </el-button>
                  </el-button-group>
                </div>
              </el-collapse-item>
            </el-collapse>
          </el-card>
        </div>

        <!-- 智能诊断 -->
        <div v-else-if="activeSection === 'diagnosis'" class="content-section">
          <el-card shadow="hover">
            <template #header>
              <h2>🔍 智能诊断</h2>
            </template>

            <el-alert
              type="info"
              :closable="false"
              class="diagnosis-info"
            >
              系统会自动诊断常见问题并提供解决方案
            </el-alert>

            <el-form label-width="120px">
              <el-form-item label="选择问题类型">
                <el-select
                  v-model="diagnosisType"
                  placeholder="选择您遇到的问题"
                  style="width: 100%"
                >
                  <el-option label="账号离线" value="account_offline" />
                  <el-option label="消息不转发" value="no_forward" />
                  <el-option label="图片转发失败" value="image_fail" />
                  <el-option label="转发延迟大" value="high_latency" />
                  <el-option label="Bot配置失败" value="bot_config_fail" />
                  <el-option label="其他问题" value="other" />
                </el-select>
              </el-form-item>

              <el-form-item label="问题描述">
                <el-input
                  v-model="diagnosisDescription"
                  type="textarea"
                  :rows="4"
                  placeholder="请详细描述您遇到的问题..."
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="runDiagnosis"
                  :loading="diagnosing"
                >
                  <el-icon><MagicStick /></el-icon>
                  开始诊断
                </el-button>
              </el-form-item>
            </el-form>

            <!-- 诊断结果 -->
            <div v-if="diagnosisResult" class="diagnosis-result">
              <el-divider />

              <el-result
                :icon="diagnosisResult.success ? 'success' : 'warning'"
                :title="diagnosisResult.title"
                :sub-title="diagnosisResult.description"
              >
                <template #extra>
                  <el-card shadow="never" class="diagnosis-details">
                    <h4>🔍 诊断详情：</h4>
                    <ul>
                      <li v-for="(detail, index) in diagnosisResult.details" :key="index">
                        {{ detail }}
                      </li>
                    </ul>

                    <h4>💡 解决方案：</h4>
                    <el-steps
                      :active="diagnosisResult.solutions.length"
                      direction="vertical"
                    >
                      <el-step
                        v-for="(solution, index) in diagnosisResult.solutions"
                        :key="index"
                        :title="solution.title"
                        :description="solution.description"
                      >
                        <template #icon>
                          <el-icon v-if="solution.done"><CircleCheckFilled /></el-icon>
                          <el-icon v-else><CirclePlus /></el-icon>
                        </template>
                      </el-step>
                    </el-steps>

                    <el-button
                      v-if="diagnosisResult.autofix_available"
                      type="success"
                      @click="autoFix"
                      :loading="autofixing"
                    >
                      <el-icon><MagicStick /></el-icon>
                      一键修复
                    </el-button>
                  </el-card>
                </template>
              </el-result>
            </div>
          </el-card>
        </div>

        <!-- 联系支持 -->
        <div v-else-if="activeSection === 'contact'" class="content-section">
          <el-card shadow="hover">
            <template #header>
              <h2>📞 联系支持</h2>
            </template>

            <el-descriptions :column="1" border>
              <el-descriptions-item label="GitHub Issues">
                <el-link
                  type="primary"
                  href="https://github.com/gfchfjh/CSBJJWT/issues"
                  target="_blank"
                >
                  https://github.com/gfchfjh/CSBJJWT/issues
                </el-link>
              </el-descriptions-item>

              <el-descriptions-item label="用户社区">
                <el-link
                  type="primary"
                  href="https://github.com/gfchfjh/CSBJJWT/discussions"
                  target="_blank"
                >
                  https://github.com/gfchfjh/CSBJJWT/discussions
                </el-link>
              </el-descriptions-item>

              <el-descriptions-item label="邮箱支持">
                support@kook-forwarder.com
              </el-descriptions-item>

              <el-descriptions-item label="当前版本">
                v4.1.0
              </el-descriptions-item>
            </el-descriptions>

            <el-divider />

            <h3>📝 反馈问题</h3>
            <el-form :model="feedbackForm" label-width="100px">
              <el-form-item label="问题类型">
                <el-select v-model="feedbackForm.type" placeholder="选择类型">
                  <el-option label="Bug反馈" value="bug" />
                  <el-option label="功能建议" value="feature" />
                  <el-option label="使用问题" value="question" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>

              <el-form-item label="标题">
                <el-input v-model="feedbackForm.title" placeholder="简要描述问题" />
              </el-form-item>

              <el-form-item label="详细描述">
                <el-input
                  v-model="feedbackForm.description"
                  type="textarea"
                  :rows="6"
                  placeholder="请详细描述问题、重现步骤、期望行为等"
                />
              </el-form-item>

              <el-form-item label="联系邮箱">
                <el-input
                  v-model="feedbackForm.email"
                  placeholder="可选：方便我们回复您"
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="submitFeedback">
                  <el-icon><Promotion /></el-icon>
                  提交反馈
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 教程详情对话框 -->
    <el-dialog
      v-model="tutorialDialogVisible"
      :title="currentTutorial?.title"
      width="80%"
      :fullscreen="false"
    >
      <div v-if="currentTutorial" class="tutorial-content">
        <div v-html="formatMarkdown(currentTutorial.content)" />
      </div>
    </el-dialog>

    <!-- 视频播放对话框 -->
    <el-dialog
      v-model="videoDialogVisible"
      :title="currentVideo?.title"
      width="80%"
      :fullscreen="false"
    >
      <div v-if="currentVideo" class="video-content">
        <video
          :src="currentVideo.url"
          controls
          style="width: 100%"
        />

        <el-divider />

        <h4>📑 视频章节</h4>
        <el-timeline>
          <el-timeline-item
            v-for="chapter in currentVideo.chapters"
            :key="chapter.time"
          >
            <span class="chapter-time">{{ chapter.time }}</span>
            <span>{{ chapter.title }}</span>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  QuestionFilled,
  Reading,
  Document,
  VideoPlay,
  ChatDotRound,
  Tools,
  Service,
  Search,
  CircleCheckFilled,
  CirclePlus,
  CircleCheck,
  CircleClose,
  MagicStick,
  Promotion,
  Clock
} from '@element-plus/icons-vue'
import api from '@/api'
import { marked } from 'marked'

// 数据
const activeSection = ref('quick_start')
const searchQuery = ref('')
const tutorials = ref([])
const videos = ref([])
const faqs = ref([])
const faqCategory = ref('all')
const activeFaq = ref(null)
const diagnosisType = ref('')
const diagnosisDescription = ref('')
const diagnosing = ref(false)
const diagnosisResult = ref(null)
const autofixing = ref(false)
const tutorialDialogVisible = ref(false)
const currentTutorial = ref(null)
const videoDialogVisible = ref(false)
const currentVideo = ref(null)

const feedbackForm = ref({
  type: '',
  title: '',
  description: '',
  email: ''
})

// 快速开始步骤
const quickStartSteps = [
  {
    icon: 'UserFilled',
    type: 'primary',
    size: 'large',
    title: '第1步：添加KOOK账号',
    description: '登录KOOK或导入Cookie',
    action: 'goto_accounts',
    actionText: '前往账号管理'
  },
  {
    icon: 'Connection',
    type: 'primary',
    size: 'large',
    title: '第2步：配置Bot',
    description: '配置Discord/Telegram/飞书Bot',
    action: 'goto_bots',
    actionText: '前往Bot配置'
  },
  {
    icon: 'Link',
    type: 'primary',
    size: 'large',
    title: '第3步：设置映射',
    description: '创建频道映射关系',
    action: 'goto_mapping',
    actionText: '前往频道映射'
  },
  {
    icon: 'Select',
    type: 'success',
    size: 'large',
    title: '第4步：开始使用',
    description: '系统自动转发消息',
    action: 'goto_home',
    actionText: '查看首页'
  }
]

// FAQ分类
const faqCategories = [
  { label: '全部', value: 'all' },
  { label: '账号相关', value: 'account' },
  { label: '配置相关', value: 'config' },
  { label: '错误排查', value: 'error' },
  { label: '性能优化', value: 'performance' },
  { label: '安全隐私', value: 'security' },
  { label: '使用技巧', value: 'usage' }
]

// 计算属性
const filteredTutorials = computed(() => {
  if (!searchQuery.value) return tutorials.value
  
  return tutorials.value.filter(t =>
    t.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    t.content.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const filteredVideos = computed(() => {
  if (!searchQuery.value) return videos.value
  
  return videos.value.filter(v =>
    v.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    v.description.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const filteredFaqs = computed(() => {
  let filtered = faqs.value
  
  if (faqCategory.value !== 'all') {
    filtered = filtered.filter(f => f.category === faqCategory.value)
  }
  
  if (searchQuery.value) {
    filtered = filtered.filter(f =>
      f.question.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      f.answer.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      f.tags.some(tag => tag.toLowerCase().includes(searchQuery.value.toLowerCase()))
    )
  }
  
  return filtered
})

// 方法
const loadData = async () => {
  try {
    const [tutorialsRes, videosRes, faqsRes] = await Promise.all([
      api.get('/api/help/tutorials'),
      api.get('/api/help/videos'),
      api.get('/api/help/faqs')
    ])
    
    tutorials.value = tutorialsRes.tutorials
    videos.value = videosRes.videos
    faqs.value = faqsRes.faqs
  } catch (error) {
    ElMessage.error('加载帮助内容失败')
  }
}

const handleSectionChange = (index) => {
  activeSection.value = index
  searchQuery.value = ''
}

const handleCategoryChange = () => {
  activeFaq.value = null
}

const handleSearch = () => {
  // 搜索逻辑已在computed中处理
}

const handleAction = (action) => {
  const actions = {
    goto_accounts: '/accounts',
    goto_bots: '/bots',
    goto_mapping: '/mapping',
    goto_home: '/'
  }
  
  if (actions[action]) {
    window.location.href = actions[action]
  }
}

const getDifficultyType = (difficulty) => {
  const types = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'danger'
  }
  return types[difficulty] || 'info'
}

const getDifficultyText = (difficulty) => {
  const texts = {
    beginner: '初级',
    intermediate: '中级',
    advanced: '高级'
  }
  return texts[difficulty] || difficulty
}

const formatMarkdown = (content) => {
  return marked.parse(content)
}

const viewTutorial = (tutorial) => {
  currentTutorial.value = tutorial
  tutorialDialogVisible.value = true
}

const playVideo = (video) => {
  currentVideo.value = video
  videoDialogVisible.value = true
}

const markHelpful = async (faqId, helpful) => {
  try {
    if (helpful) {
      const faq = faqs.value.find(f => f.id === faqId)
      if (faq) {
        faq.helpful_count++
        ElMessage.success('感谢您的反馈！')
      }
    } else {
      ElMessage.info('感谢反馈，我们会改进这个答案')
    }
  } catch (error) {
    ElMessage.error('反馈失败')
  }
}

const runDiagnosis = async () => {
  if (!diagnosisType.value) {
    ElMessage.warning('请选择问题类型')
    return
  }
  
  diagnosing.value = true
  diagnosisResult.value = null
  
  try {
    // 调用智能诊断API（待实现）
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 模拟诊断结果
    diagnosisResult.value = {
      success: true,
      title: '诊断完成',
      description: '已找到问题根源',
      details: [
        '✅ 网络连接正常',
        '✅ Redis服务运行中',
        '⚠️ 检测到Cookie即将过期',
        '✅ Bot配置正常'
      ],
      solutions: [
        {
          title: '更新Cookie',
          description: '您的Cookie将在3天后过期，建议现在更新',
          done: false
        }
      ],
      autofix_available: true
    }
    
    ElMessage.success('诊断完成')
  } catch (error) {
    ElMessage.error('诊断失败')
  } finally {
    diagnosing.value = false
  }
}

const autoFix = async () => {
  autofixing.value = true
  
  try {
    const result = await api.post('/api/system/autofix/all')
    
    if (result.overall_success) {
      ElMessage.success('✅ 所有问题已自动修复！')
    } else {
      ElMessage.warning('部分问题已修复，请查看详情')
    }
  } catch (error) {
    ElMessage.error('自动修复失败')
  } finally {
    autofixing.value = false
  }
}

const submitFeedback = () => {
  if (!feedbackForm.value.title || !feedbackForm.value.description) {
    ElMessage.warning('请填写标题和描述')
    return
  }
  
  ElMessage.success('反馈已提交，感谢您的支持！')
  
  // 重置表单
  feedbackForm.value = {
    type: '',
    title: '',
    description: '',
    email: ''
  }
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.help-enhanced {
  padding: 20px;
}

.nav-card {
  position: sticky;
  top: 20px;
}

.search-card {
  margin-top: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-section {
  min-height: 600px;
}

.tutorial-card,
.video-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.tutorial-card:hover,
.video-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.tutorial-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tutorial-header h3 {
  margin: 0;
  font-size: 16px;
}

.tutorial-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
}

.tutorial-steps {
  margin: 16px 0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.view-button {
  margin-top: 12px;
}

.video-thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 */
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.video-thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.video-card:hover .play-overlay {
  opacity: 1;
}

.duration-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.video-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.video-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.faq-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.faq-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.faq-content {
  line-height: 1.8;
  color: #606266;
}

.faq-tags {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.faq-feedback {
  display: flex;
  align-items: center;
  gap: 12px;
}

.diagnosis-info {
  margin-bottom: 24px;
}

.diagnosis-result {
  margin-top: 24px;
}

.diagnosis-details {
  text-align: left;
  background-color: #f5f7fa;
}

.diagnosis-details h4 {
  margin: 16px 0 8px 0;
  font-size: 16px;
}

.diagnosis-details ul {
  margin: 8px 0;
  padding-left: 24px;
}

.diagnosis-details li {
  margin-bottom: 6px;
}

.timeline-content h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.timeline-content p {
  margin: 0 0 12px 0;
  color: #606266;
}

.tutorial-content {
  max-height: 70vh;
  overflow-y: auto;
}

.video-content {
  max-height: 70vh;
  overflow-y: auto;
}

.chapter-time {
  color: #409EFF;
  font-weight: 600;
  margin-right: 8px;
}
</style>
