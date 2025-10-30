<template>
  <div class="welcome-step">
    <div class="welcome-icon">
      <el-icon :size="100" color="#409EFF">
        <Promotion />
      </el-icon>
    </div>

    <h2>欢迎来到 KOOK消息转发系统！</h2>
    
    <div class="welcome-description">
      <p>本向导将帮助您快速完成以下配置：</p>
      
      <el-timeline>
        <el-timeline-item 
          timestamp="第1步" 
          placement="top"
          type="primary"
          hollow
        >
          <el-card>
            <h4>🔑 连接KOOK账号</h4>
            <p>通过Chrome扩展一键导入Cookie，或使用账号密码登录</p>
            <el-tag size="small" type="info">预计耗时: 1分钟</el-tag>
          </el-card>
        </el-timeline-item>

        <el-timeline-item 
          timestamp="第2步" 
          placement="top"
          type="success"
          hollow
        >
          <el-card>
            <h4>🤖 配置转发Bot</h4>
            <p>设置Discord Webhook / Telegram Bot / 飞书应用</p>
            <el-tag size="small" type="info">预计耗时: 2分钟</el-tag>
          </el-card>
        </el-timeline-item>

        <el-timeline-item 
          timestamp="第3步" 
          placement="top"
          type="warning"
          hollow
        >
          <el-card>
            <h4>🔀 设置频道映射</h4>
            <p>AI智能推荐映射关系，也可手动调整</p>
            <el-tag size="small" type="info">预计耗时: 1分钟</el-tag>
          </el-card>
        </el-timeline-item>

        <el-timeline-item 
          timestamp="完成" 
          placement="top"
          type="danger"
          :hollow="false"
        >
          <el-card>
            <h4>✅ 开始使用</h4>
            <p>立即开始自动转发KOOK消息！</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>

    <div class="welcome-actions">
      <el-button type="primary" size="large" @click="handleStart">
        <el-icon class="el-icon--left"><Right /></el-icon>
        开始配置
      </el-button>
      
      <el-button size="large" @click="handleSkip">
        跳过向导，稍后配置
      </el-button>
    </div>

    <div class="welcome-tips">
      <el-alert
        title="💡 小提示"
        type="info"
        :closable="false"
      >
        <p>• 所有配置都可以在稍后修改</p>
        <p>• 建议先准备好KOOK账号Cookie</p>
        <p>• 至少配置一个转发目标（Discord/Telegram/飞书）</p>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { Promotion, Right } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const emit = defineEmits(['next'])

const handleStart = () => {
  emit('next')
}

const handleSkip = async () => {
  const result = await ElMessageBox.confirm(
    '跳过配置向导后，您需要手动在各个页面分别配置。确定要跳过吗？',
    '确认跳过',
    {
      type: 'warning',
      confirmButtonText: '确定跳过',
      cancelButtonText: '继续配置'
    }
  ).catch(() => false)

  if (result) {
    // 跳转到主页
    window.location.href = '/'
  }
}
</script>

<style scoped>
.welcome-step {
  max-width: 700px;
  margin: 0 auto;
  text-align: center;
}

.welcome-icon {
  margin-bottom: 30px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 30px;
}

.welcome-description {
  text-align: left;
  margin-bottom: 40px;
}

.welcome-description > p {
  font-size: 16px;
  color: #606266;
  margin-bottom: 20px;
}

.welcome-description :deep(.el-card) {
  border: none;
  background: #f5f7fa;
  margin-bottom: 10px;
}

.welcome-description h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.welcome-description p {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
}

.welcome-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 30px;
}

.welcome-tips {
  text-align: left;
}

.welcome-tips :deep(.el-alert__content) {
  padding: 10px 0;
}

.welcome-tips p {
  margin: 5px 0;
  font-size: 13px;
}
</style>
