<template>
  <div class="video-tutorial">
    <!-- 视频教程按钮 -->
    <el-button
      :type="buttonType"
      :size="buttonSize"
      :icon="VideoPlay"
      @click="openDialog"
    >
      {{ buttonText }}
    </el-button>

    <!-- 视频教程对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="currentTutorial.title"
      width="80%"
      :close-on-click-modal="false"
      class="video-dialog"
    >
      <div class="video-container">
        <!-- 视频播放器 -->
        <div v-if="currentTutorial.videoUrl" class="video-player">
          <iframe
            :src="getEmbedUrl(currentTutorial.videoUrl)"
            frameborder="0"
            allowfullscreen
            class="video-frame"
          ></iframe>
        </div>

        <!-- 暂无视频时显示占位 -->
        <div v-else class="video-placeholder">
          <el-icon :size="64" color="#909399"><VideoCamera /></el-icon>
          <p class="placeholder-text">视频教程录制中，敬请期待...</p>
          <el-alert
            title="临时方案"
            type="info"
            :closable="false"
            show-icon
          >
            <p>在视频教程完成前，您可以：</p>
            <ul>
              <li>查看图文教程文档</li>
              <li>参考配置向导中的提示</li>
              <li>查看项目GitHub仓库的Wiki</li>
            </ul>
          </el-alert>
        </div>

        <!-- 教程描述 -->
        <el-card class="tutorial-info" v-if="currentTutorial.description">
          <template #header>
            <span>📝 教程说明</span>
          </template>
          <p>{{ currentTutorial.description }}</p>
          
          <div v-if="currentTutorial.steps" class="tutorial-steps">
            <h4>📋 主要步骤：</h4>
            <ol>
              <li v-for="(step, index) in currentTutorial.steps" :key="index">
                {{ step }}
              </li>
            </ol>
          </div>

          <div v-if="currentTutorial.duration" class="tutorial-meta">
            <el-tag type="info">
              <el-icon><Timer /></el-icon>
              时长：{{ currentTutorial.duration }}
            </el-tag>
            <el-tag type="success" v-if="currentTutorial.difficulty">
              <el-icon><Star /></el-icon>
              难度：{{ currentTutorial.difficulty }}
            </el-tag>
          </div>
        </el-card>

        <!-- 相关教程推荐 -->
        <el-card class="related-tutorials" v-if="relatedTutorials.length > 0">
          <template #header>
            <span>🔗 相关教程</span>
          </template>
          <div class="tutorial-list">
            <el-button
              v-for="tutorial in relatedTutorials"
              :key="tutorial.id"
              text
              @click="switchTutorial(tutorial.id)"
            >
              {{ tutorial.title }} ({{ tutorial.duration }})
            </el-button>
          </div>
        </el-card>

        <!-- 外部链接 -->
        <div class="external-links">
          <el-link
            type="primary"
            :href="currentTutorial.bilibiliUrl"
            target="_blank"
            v-if="currentTutorial.bilibiliUrl"
          >
            <el-icon><Link /></el-icon>
            在Bilibili观看
          </el-link>
          <el-link
            type="primary"
            :href="currentTutorial.youtubeUrl"
            target="_blank"
            v-if="currentTutorial.youtubeUrl"
          >
            <el-icon><Link /></el-icon>
            在YouTube观看
          </el-link>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="markAsWatched">
            标记为已观看
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { VideoPlay, VideoCamera, Timer, Star, Link } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  tutorialId: {
    type: String,
    required: true
  },
  buttonText: {
    type: String,
    default: '📺 观看视频教程'
  },
  buttonType: {
    type: String,
    default: 'primary'
  },
  buttonSize: {
    type: String,
    default: 'default'
  }
})

const dialogVisible = ref(false)

// 教程数据库（v1.4.0 - 待录制）
const tutorials = {
  quickstart: {
    id: 'quickstart',
    title: '快速入门教程',
    duration: '10分钟',
    difficulty: '入门',
    description: '从零开始，10分钟快速上手KOOK消息转发系统',
    steps: [
      '下载并安装应用',
      '添加KOOK账号',
      '配置目标平台Bot',
      '设置频道映射',
      '启动服务并测试'
    ],
    videoUrl: '', // 待录制
    bilibiliUrl: 'https://www.bilibili.com',
    youtubeUrl: '',
    category: 'beginner'
  },
  cookie: {
    id: 'cookie',
    title: 'KOOK Cookie获取教程',
    duration: '3分钟',
    difficulty: '简单',
    description: '详细演示如何从浏览器中获取KOOK的Cookie',
    steps: [
      '打开KOOK网页版并登录',
      '按F12打开开发者工具',
      '切换到Application标签',
      '找到并复制Cookie',
      '粘贴到应用中'
    ],
    videoUrl: '',
    bilibiliUrl: '',
    youtubeUrl: '',
    category: 'account'
  },
  discord: {
    id: 'discord',
    title: 'Discord Webhook配置',
    duration: '2分钟',
    difficulty: '简单',
    description: '如何创建和配置Discord Webhook',
    steps: [
      '进入Discord服务器设置',
      '打开集成页面',
      '创建新Webhook',
      '复制Webhook URL',
      '在应用中配置并测试'
    ],
    videoUrl: '',
    bilibiliUrl: '',
    youtubeUrl: '',
    category: 'bot'
  },
  telegram: {
    id: 'telegram',
    title: 'Telegram Bot配置',
    duration: '4分钟',
    difficulty: '中等',
    description: '使用BotFather创建Telegram Bot并配置',
    steps: [
      '与@BotFather对话',
      '发送/newbot命令创建Bot',
      '获取Bot Token',
      '将Bot添加到群组',
      '获取Chat ID并配置'
    ],
    videoUrl: '',
    bilibiliUrl: '',
    youtubeUrl: '',
    category: 'bot'
  },
  feishu: {
    id: 'feishu',
    title: '飞书自建应用配置',
    duration: '5分钟',
    difficulty: '中等',
    description: '在飞书开放平台创建自建应用',
    steps: [
      '访问飞书开放平台',
      '创建企业自建应用',
      '开启机器人能力',
      '获取App ID和Secret',
      '将机器人添加到群组'
    ],
    videoUrl: '',
    bilibiliUrl: '',
    youtubeUrl: '',
    category: 'bot'
  },
  mapping: {
    id: 'mapping',
    title: '智能频道映射',
    duration: '3分钟',
    difficulty: '简单',
    description: '使用智能映射功能快速配置频道',
    steps: [
      '选择KOOK源频道',
      '启用智能映射',
      '自动匹配目标频道',
      '手动调整映射关系',
      '保存并测试'
    ],
    videoUrl: '',
    bilibiliUrl: '',
    youtubeUrl: '',
    category: 'config'
  },
  filter: {
    id: 'filter',
    title: '消息过滤规则',
    duration: '4分钟',
    difficulty: '中等',
    description: '配置关键词、用户和类型过滤规则',
    steps: [
      '了解过滤规则类型',
      '配置关键词黑白名单',
      '设置用户过滤',
      '选择消息类型',
      '测试过滤效果'
    ],
    videoUrl: '',
    bilibiliUrl: '',
    youtubeUrl: '',
    category: 'config'
  },
  troubleshooting: {
    id: 'troubleshooting',
    title: '常见问题排查',
    duration: '6分钟',
    difficulty: '进阶',
    description: '快速定位和解决常见问题',
    steps: [
      'KOOK账号掉线处理',
      '消息转发失败排查',
      '图片上传问题解决',
      'Redis连接问题',
      '查看日志和错误信息'
    ],
    videoUrl: '',
    bilibiliUrl: '',
    youtubeUrl: '',
    category: 'advanced'
  }
}

// 当前教程
const currentTutorial = computed(() => {
  return tutorials[props.tutorialId] || tutorials.quickstart
})

// 相关教程推荐
const relatedTutorials = computed(() => {
  const current = currentTutorial.value
  return Object.values(tutorials).filter(t => 
    t.id !== current.id && 
    (t.category === current.category || t.difficulty === current.difficulty)
  ).slice(0, 3)
})

// 打开对话框
const openDialog = () => {
  dialogVisible.value = true
}

// 切换教程
const switchTutorial = (tutorialId) => {
  // 通知父组件切换教程
  emit('change-tutorial', tutorialId)
}

// 获取嵌入式视频URL
const getEmbedUrl = (url) => {
  if (!url) return ''
  
  // Bilibili嵌入式URL转换
  if (url.includes('bilibili.com')) {
    const bvMatch = url.match(/BV[a-zA-Z0-9]+/)
    if (bvMatch) {
      return `https://player.bilibili.com/player.html?bvid=${bvMatch[0]}&autoplay=0`
    }
  }
  
  // YouTube嵌入式URL转换
  if (url.includes('youtube.com') || url.includes('youtu.be')) {
    const videoIdMatch = url.match(/(?:v=|\/)([\w-]{11})/)
    if (videoIdMatch) {
      return `https://www.youtube.com/embed/${videoIdMatch[1]}`
    }
  }
  
  return url
}

// 标记为已观看
const markAsWatched = () => {
  // 保存到本地存储
  const watched = JSON.parse(localStorage.getItem('watchedTutorials') || '[]')
  if (!watched.includes(props.tutorialId)) {
    watched.push(props.tutorialId)
    localStorage.setItem('watchedTutorials', JSON.stringify(watched))
  }
  
  ElMessage.success('已标记为已观看')
  dialogVisible.value = false
}

const emit = defineEmits(['change-tutorial'])
</script>

<style scoped>
.video-tutorial {
  display: inline-block;
}

.video-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 80vh;
  overflow-y: auto;
}

.video-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.video-player {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 比例 */
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-frame {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 2px dashed #dcdfe6;
}

.placeholder-text {
  margin: 20px 0;
  font-size: 16px;
  color: #606266;
}

.video-placeholder .el-alert {
  max-width: 500px;
  margin-top: 20px;
  text-align: left;
}

.video-placeholder ul {
  margin: 10px 0 0 20px;
}

.tutorial-info {
  margin-top: 20px;
}

.tutorial-steps {
  margin-top: 15px;
}

.tutorial-steps h4 {
  margin-bottom: 10px;
  color: #409eff;
}

.tutorial-steps ol {
  margin-left: 20px;
}

.tutorial-steps li {
  margin: 8px 0;
  line-height: 1.6;
}

.tutorial-meta {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.tutorial-meta .el-tag {
  display: flex;
  align-items: center;
  gap: 5px;
}

.related-tutorials {
  margin-top: 20px;
}

.tutorial-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tutorial-list .el-button {
  justify-content: flex-start;
  text-align: left;
}

.external-links {
  display: flex;
  gap: 15px;
  justify-content: center;
  padding: 15px 0;
}

.external-links .el-link {
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
