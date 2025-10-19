<template>
  <div class="step-welcome">
    <el-result
      icon="success"
      title="🎉 欢迎使用KOOK消息转发系统"
      sub-title="本向导将帮助您完成基础配置，预计耗时：3-5分钟"
    >
      <template #extra>
        <!-- 免责声明 -->
        <el-alert
          title="⚠️ 免责声明"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        >
          <div class="disclaimer-content">
            <p><strong>使用本软件前，请仔细阅读以下声明：</strong></p>
            <ol>
              <li>本软件通过浏览器自动化抓取KOOK消息，<strong>可能违反KOOK服务条款</strong></li>
              <li>使用本软件可能导致账号被封禁，<strong>请仅在已获授权的场景下使用</strong></li>
              <li>转发的消息内容可能涉及版权，<strong>请遵守相关法律法规</strong></li>
              <li>本软件仅供学习交流，<strong>开发者不承担任何法律责任</strong></li>
              <li>使用本软件即表示您已了解并接受上述风险</li>
            </ol>
          </div>
        </el-alert>

        <div class="welcome-tips">
          <el-alert
            title="配置前准备"
            type="info"
            :closable="false"
            show-icon
          >
            <ul>
              <li>您需要准备KOOK账号的Cookie或账号密码</li>
              <li>至少配置一个转发目标（Discord/Telegram/飞书）</li>
              <li>可以随时在设置中修改配置</li>
            </ul>
          </el-alert>
        </div>

        <div class="agreement-section">
          <el-checkbox v-model="agreed" size="large">
            <strong>我已阅读并同意以上免责声明</strong>
          </el-checkbox>
        </div>

        <div class="action-buttons">
          <el-button
            type="primary"
            size="large"
            :disabled="!agreed"
            @click="handleNext"
          >
            同意并继续
          </el-button>
          <el-button size="large" @click="handleReject">
            拒绝并退出
          </el-button>
        </div>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const agreed = ref(false)

const emit = defineEmits(['next', 'reject'])

const handleNext = () => {
  emit('next')
}

const handleReject = () => {
  emit('reject')
}
</script>

<style scoped>
.welcome-tips {
  margin: 30px 0;
}

.disclaimer-content {
  text-align: left;
}

.disclaimer-content p {
  margin-bottom: 10px;
}

.disclaimer-content ol {
  margin: 10px 0;
  padding-left: 25px;
}

.disclaimer-content li {
  margin: 8px 0;
  line-height: 1.6;
}

.agreement-section {
  margin: 25px 0;
  text-align: center;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 4px;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}
</style>
