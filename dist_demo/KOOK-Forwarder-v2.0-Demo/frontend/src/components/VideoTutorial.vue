<template>
  <div class="video-tutorial">
    <div class="video-container">
      <video
        ref="videoRef"
        controls
        :src="currentVideoUrl"
        :poster="videoPoster"
        @error="handleVideoError"
        class="video-player"
      >
        您的浏览器不支持视频播放
      </video>
    </div>

    <div class="video-info">
      <h3>{{ currentVideo.title }}</h3>
      <p class="description">{{ currentVideo.description }}</p>
      <div class="video-meta">
        <el-tag>{{ currentVideo.duration }}</el-tag>
        <el-tag type="info">{{ currentVideo.difficulty }}</el-tag>
        <span class="views">👁️ {{ currentVideo.views }} 次观看</span>
      </div>
    </div>

    <!-- 相关视频列表 -->
    <div class="related-videos">
      <h4>📺 相关教程</h4>
      <el-scrollbar height="300px">
        <div
          v-for="video in relatedVideos"
          :key="video.id"
          class="video-item"
          :class="{ active: video.id === videoId }"
          @click="switchVideo(video.id)"
        >
          <img :src="video.thumbnail" class="video-thumbnail" />
          <div class="video-item-info">
            <p class="video-title">{{ video.title }}</p>
            <p class="video-duration">{{ video.duration }}</p>
          </div>
        </div>
      </el-scrollbar>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  videoId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['ended', 'error'])

const videoRef = ref(null)

// 视频库
const videoLibrary = {
  'quick-start': {
    id: 'quick-start',
    title: '快速入门指南',
    description: '5分钟快速了解系统的核心功能和基本操作',
    url: '/videos/tutorials/quick-start.mp4',
    poster: '/videos/posters/quick-start.jpg',
    duration: '5:32',
    difficulty: '入门',
    views: 1234
  },
  'cookie-import': {
    id: 'cookie-import',
    title: 'Cookie获取与导入',
    description: '详细演示如何从浏览器获取KOOK的Cookie并导入到系统',
    url: '/videos/tutorials/cookie-import.mp4',
    poster: '/videos/posters/cookie-import.jpg',
    duration: '3:45',
    difficulty: '入门',
    views: 892
  },
  'discord-config': {
    id: 'discord-config',
    title: 'Discord Webhook配置',
    description: '手把手教你创建Discord Webhook并配置到系统',
    url: '/videos/tutorials/discord-config.mp4',
    poster: '/videos/posters/discord-config.jpg',
    duration: '2:18',
    difficulty: '入门',
    views: 756
  },
  'telegram-bot': {
    id: 'telegram-bot',
    title: 'Telegram Bot创建',
    description: '与BotFather对话创建Telegram Bot的完整流程',
    url: '/videos/tutorials/telegram-bot.mp4',
    poster: '/videos/posters/telegram-bot.jpg',
    duration: '4:12',
    difficulty: '入门',
    views: 645
  },
  'feishu-app': {
    id: 'feishu-app',
    title: '飞书自建应用配置',
    description: '在飞书开放平台创建自建应用并获取凭证',
    url: '/videos/tutorials/feishu-app.mp4',
    poster: '/videos/posters/feishu-app.jpg',
    duration: '6:28',
    difficulty: '中级',
    views: 432
  },
  'smart-mapping': {
    id: 'smart-mapping',
    title: '智能映射功能演示',
    description: '了解如何使用智能映射自动匹配同名频道',
    url: '/videos/tutorials/smart-mapping.mp4',
    poster: '/videos/posters/smart-mapping.jpg',
    duration: '3:56',
    difficulty: '中级',
    views: 521
  },
  'advanced-filter': {
    id: 'advanced-filter',
    title: '高级过滤规则设置',
    description: '掌握关键词过滤、用户黑白名单等高级功能',
    url: '/videos/tutorials/advanced-filter.mp4',
    poster: '/videos/posters/advanced-filter.jpg',
    duration: '5:18',
    difficulty: '高级',
    views: 298
  },
  'troubleshooting': {
    id: 'troubleshooting',
    title: '常见问题排查',
    description: '遇到问题时如何自己诊断和解决',
    url: '/videos/tutorials/troubleshooting.mp4',
    poster: '/videos/posters/troubleshooting.jpg',
    duration: '7:42',
    difficulty: '高级',
    views: 412
  }
}

// 当前视频
const currentVideo = computed(() => {
  return videoLibrary[props.videoId] || videoLibrary['quick-start']
})

const currentVideoUrl = computed(() => currentVideo.value.url)
const videoPoster = computed(() => currentVideo.value.poster)

// 相关视频
const relatedVideos = computed(() => {
  return Object.values(videoLibrary).filter(v => v.id !== props.videoId)
})

// 切换视频
function switchVideo(videoId) {
  emit('update:videoId', videoId)
}

// 视频加载错误
function handleVideoError(event) {
  ElMessage.error('视频加载失败，请检查网络连接')
  emit('error', event)
  
  // 如果是线上视频失败，尝试使用占位符
  if (videoRef.value) {
    videoRef.value.poster = '/placeholder-video.png'
  }
}

// 监听视频结束
watch(videoRef, (video) => {
  if (video) {
    video.addEventListener('ended', () => {
      emit('ended')
      
      // 自动播放下一个视频
      const currentIndex = Object.keys(videoLibrary).indexOf(props.videoId)
      const nextIndex = (currentIndex + 1) % Object.keys(videoLibrary).length
      const nextVideoId = Object.keys(videoLibrary)[nextIndex]
      
      ElMessage.info('3秒后将自动播放下一个视频')
      setTimeout(() => {
        switchVideo(nextVideoId)
      }, 3000)
    })
  }
})

onMounted(() => {
  // 记录观看次数
  // TODO: 调用API记录
})
</script>

<style scoped>
.video-tutorial {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.video-container {
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  max-height: 500px;
  display: block;
}

.video-info {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.video-info h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #303133;
}

.description {
  margin: 10px 0;
  color: #606266;
  line-height: 1.6;
}

.video-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
}

.views {
  color: #909399;
  font-size: 14px;
}

.related-videos {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.related-videos h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
}

.video-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  margin-bottom: 10px;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.video-item:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.video-item.active {
  border: 2px solid #409EFF;
  background: #ecf5ff;
}

.video-thumbnail {
  width: 120px;
  height: 68px;
  object-fit: cover;
  border-radius: 4px;
}

.video-item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.video-title {
  margin: 0 0 5px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.video-duration {
  margin: 0;
  font-size: 12px;
  color: #909399;
}
</style>
