<template>
  <transition name="fade">
    <div v-if="visible" class="loading-overlay">
      <div class="loading-content">
        <el-icon class="loading-icon" :size="60">
          <Loading />
        </el-icon>
        <div class="loading-text">{{ message }}</div>
        <div v-if="subMessage" class="loading-sub-text">{{ subMessage }}</div>
        <el-progress
          v-if="progress !== null"
          :percentage="progress"
          :status="progressStatus"
          style="margin-top: 20px; width: 300px"
        />
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: '加载中...'
  },
  subMessage: {
    type: String,
    default: ''
  },
  progress: {
    type: Number,
    default: null
  },
  progressStatus: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.loading-content {
  background: white;
  padding: 40px 60px;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  text-align: center;
  min-width: 300px;
}

.loading-icon {
  animation: spin 1s linear infinite;
  color: #409EFF;
  margin-bottom: 20px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 18px;
  color: #303133;
  margin-bottom: 10px;
  font-weight: 500;
}

.loading-sub-text {
  font-size: 14px;
  color: #909399;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
