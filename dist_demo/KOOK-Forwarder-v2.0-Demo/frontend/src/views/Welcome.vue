<template>
  <div class="welcome-screen">
    <div class="welcome-overlay"></div>
    
    <div class="welcome-content">
      <div class="welcome-header">
        <div class="logo-container">
          <img src="@/assets/logo.png" alt="KOOK Forwarder" class="logo" />
        </div>
        <h1 class="welcome-title">🎉 欢迎使用</h1>
        <h2 class="app-name">KOOK消息转发系统</h2>
        <p class="version-badge">v11.0.0 Enhanced</p>
      </div>

      <div class="welcome-body">
        <div class="intro-text">
          <p>5分钟安装 · 3步配置 · 零代码基础 · AI智能推荐</p>
          <p class="highlight">真正人人可用的消息转发工具</p>
        </div>

        <div class="quick-start">
          <h3>🚀 快速开始</h3>
          <div class="steps-container">
            <div class="step-item">
              <div class="step-icon">
                <el-icon :size="32"><Connection /></el-icon>
              </div>
              <div class="step-content">
                <h4>步骤 1</h4>
                <p>登录KOOK账号</p>
                <span class="step-time">约1分钟</span>
              </div>
            </div>

            <div class="step-arrow">
              <el-icon :size="24"><ArrowRight /></el-icon>
            </div>

            <div class="step-item">
              <div class="step-icon">
                <el-icon :size="32"><Setting /></el-icon>
              </div>
              <div class="step-content">
                <h4>步骤 2</h4>
                <p>配置转发Bot</p>
                <span class="step-time">约2分钟</span>
              </div>
            </div>

            <div class="step-arrow">
              <el-icon :size="24"><ArrowRight /></el-icon>
            </div>

            <div class="step-item">
              <div class="step-icon">
                <el-icon :size="32"><Link /></el-icon>
              </div>
              <div class="step-content">
                <h4>步骤 3</h4>
                <p>智能映射</p>
                <span class="step-time">约1分钟</span>
              </div>
            </div>
          </div>
        </div>

        <div class="actions">
          <el-button
            type="primary"
            size="large"
            @click="startWizard"
            class="start-btn"
          >
            <el-icon class="el-icon--left"><MagicStick /></el-icon>
            开始配置向导
          </el-button>
          
          <el-button
            size="large"
            @click="skipWizard"
            class="skip-btn"
          >
            跳过，我已经会了
          </el-button>
        </div>

        <div class="help-links">
          <el-link
            type="primary"
            @click="openDocs"
            :underline="false"
          >
            <el-icon><Document /></el-icon>
            查看完整文档
          </el-link>
          
          <el-link
            type="primary"
            @click="openVideo"
            :underline="false"
          >
            <el-icon><VideoPlay /></el-icon>
            观看视频教程
          </el-link>
          
          <el-link
            type="primary"
            @click="openGithub"
            :underline="false"
          >
            <el-icon><Link /></el-icon>
            GitHub仓库
          </el-link>
        </div>
      </div>

      <div class="welcome-footer">
        <p class="copyright">
          Made with ❤️ by KOOK Community
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  Connection,
  Setting,
  Link,
  ArrowRight,
  MagicStick,
  Document,
  VideoPlay
} from '@element-plus/icons-vue'

const router = useRouter()

const startWizard = () => {
  router.push('/wizard')
}

const skipWizard = () => {
  ElMessageBox.confirm(
    '跳过向导后，您需要在主界面手动配置所有设置。确定要跳过吗？',
    '确认跳过',
    {
      confirmButtonText: '确定跳过',
      cancelButtonText: '继续配置',
      type: 'warning'
    }
  )
    .then(() => {
      router.push('/')
    })
    .catch(() => {
      // 用户取消
    })
}

const openDocs = () => {
  window.open('https://github.com/gfchfjh/CSBJJWT/blob/main/README.md', '_blank')
}

const openVideo = () => {
  ElMessageBox.alert(
    '视频教程正在制作中，敬请期待！',
    '提示',
    {
      confirmButtonText: '我知道了',
      type: 'info'
    }
  )
}

const openGithub = () => {
  window.open('https://github.com/gfchfjh/CSBJJWT', '_blank')
}
</script>

<style scoped lang="scss">
.welcome-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.welcome-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23ffffff" fill-opacity="0.1" d="M0,96L48,112C96,128,192,160,288,186.7C384,213,480,235,576,213.3C672,192,768,128,864,128C960,128,1056,192,1152,197.3C1248,203,1344,149,1392,122.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat bottom;
  background-size: cover;
  opacity: 0.3;
}

.welcome-content {
  position: relative;
  max-width: 900px;
  width: 90%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 60px 40px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-container {
  margin-bottom: 20px;
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

.logo {
  width: 80px;
  height: 80px;
}

.welcome-title {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 10px 0;
}

.app-name {
  font-size: 28px;
  font-weight: 600;
  color: #606266;
  margin: 0 0 10px 0;
}

.version-badge {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
}

.welcome-body {
  .intro-text {
    text-align: center;
    margin-bottom: 40px;
    
    p {
      font-size: 16px;
      color: #606266;
      margin: 8px 0;
    }
    
    .highlight {
      font-size: 18px;
      font-weight: 600;
      color: #667eea;
    }
  }
  
  .quick-start {
    margin-bottom: 40px;
    
    h3 {
      text-align: center;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 30px;
    }
    
    .steps-container {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 20px;
      flex-wrap: wrap;
    }
    
    .step-item {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 20px;
      background: #f5f7fa;
      border-radius: 12px;
      flex: 0 0 auto;
      
      .step-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
      }
      
      .step-content {
        h4 {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin: 0 0 5px 0;
        }
        
        p {
          font-size: 14px;
          color: #606266;
          margin: 0 0 5px 0;
        }
        
        .step-time {
          font-size: 12px;
          color: #909399;
        }
      }
    }
    
    .step-arrow {
      color: #909399;
    }
  }
  
  .actions {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 30px;
    flex-wrap: wrap;
    
    .start-btn {
      min-width: 200px;
      height: 50px;
      font-size: 16px;
      font-weight: 600;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
      }
    }
    
    .skip-btn {
      min-width: 180px;
      height: 50px;
      font-size: 16px;
    }
  }
  
  .help-links {
    display: flex;
    justify-content: center;
    gap: 30px;
    flex-wrap: wrap;
    
    .el-link {
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 5px;
    }
  }
}

.welcome-footer {
  text-align: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
  
  .copyright {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

@media (max-width: 768px) {
  .welcome-content {
    padding: 40px 20px;
  }
  
  .steps-container {
    flex-direction: column;
    
    .step-arrow {
      transform: rotate(90deg);
    }
  }
  
  .actions {
    flex-direction: column;
    
    .start-btn,
    .skip-btn {
      width: 100%;
    }
  }
}
</style>
