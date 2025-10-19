<template>
  <div class="step-login">
    <h2>📧 登录KOOK账号</h2>
    
    <el-radio-group v-model="loginType" class="login-type-selector">
      <el-radio label="cookie">Cookie导入（推荐）</el-radio>
      <el-radio label="password">账号密码登录</el-radio>
    </el-radio-group>

    <!-- Cookie登录 -->
    <div v-if="loginType === 'cookie'" class="cookie-login">
      <el-alert
        title="如何获取Cookie？"
        type="info"
        :closable="false"
        class="help-alert"
      >
        <ol>
          <li>在浏览器打开 <a href="https://www.kookapp.cn" target="_blank">KOOK网页版</a> 并登录</li>
          <li>按F12打开开发者工具</li>
          <li>切换到 Application/存储 → Cookies</li>
          <li>复制所有Cookie（或使用浏览器扩展导出）</li>
        </ol>
        <el-link type="primary" :underline="false" @click="emit('openVideo', 'cookie')">
          <el-icon><VideoPlay /></el-icon>
          观看视频教程 (3分钟)
        </el-link>
      </el-alert>

      <el-form :model="form" label-width="100px" class="form-content">
        <el-form-item label="Cookie">
          <el-input
            v-model="form.cookie"
            type="textarea"
            :rows="6"
            placeholder="粘贴Cookie内容（JSON格式或文本格式）"
          />
        </el-form-item>

        <el-form-item label="账号备注">
          <el-input
            v-model="form.name"
            placeholder="例如：主账号"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 密码登录 -->
    <div v-else class="password-login">
      <el-alert
        title="首次登录可能需要验证码"
        type="warning"
        :closable="false"
        class="help-alert"
      />

      <el-form :model="form" label-width="100px" class="form-content">
        <el-form-item label="邮箱">
          <el-input
            v-model="form.email"
            placeholder="KOOK注册邮箱"
          />
        </el-form-item>

        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="账号密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="账号备注">
          <el-input
            v-model="form.name"
            placeholder="例如：主账号"
          />
        </el-form-item>
      </el-form>
    </div>

    <div class="action-buttons">
      <el-button @click="emit('prev')">上一步</el-button>
      <el-button
        type="primary"
        :loading="loading"
        @click="handleLogin"
      >
        登录并继续
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'
import api from '@/api'

const loginType = ref('cookie')
const loading = ref(false)

const form = ref({
  name: '',
  email: '',
  password: '',
  cookie: ''
})

const emit = defineEmits(['next', 'prev', 'openVideo'])

const handleLogin = async () => {
  try {
    loading.value = true

    const data = {
      name: form.value.name || '默认账号'
    }

    if (loginType.value === 'cookie') {
      if (!form.value.cookie) {
        ElMessage.error('请输入Cookie')
        return
      }
      data.cookie = form.value.cookie
    } else {
      if (!form.value.email || !form.value.password) {
        ElMessage.error('请输入邮箱和密码')
        return
      }
      data.email = form.value.email
      data.password = form.value.password
    }

    await api.addAccount(data)
    ElMessage.success('账号添加成功')
    emit('next')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.login-type-selector {
  margin: 20px 0;
}

.form-content {
  margin-top: 20px;
}

.help-alert {
  margin-bottom: 20px;
}

.help-alert ol {
  margin: 10px 0;
  padding-left: 25px;
}

.help-alert li {
  margin: 5px 0;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}
</style>
