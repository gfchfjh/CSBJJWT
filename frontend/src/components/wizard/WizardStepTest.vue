<template>
  <div class="wizard-step-test">
    <h2>🧪 测试配置</h2>
    <p class="description">
      配置已完成！让我们发送一条测试消息来验证一切正常工作。
    </p>

    <!-- 测试状态 -->
    <div class="test-status">
      <el-result
        v-if="testResult === null"
        icon="info"
        title="准备就绪"
        sub-title="点击下方按钮开始测试"
      />

      <el-result
        v-else-if="testResult === 'testing'"
        icon="info"
        title="测试中..."
        sub-title="正在发送测试消息，请稍候"
      >
        <template #icon>
          <el-icon class="is-loading"><Loading /></el-icon>
        </template>
      </el-result>

      <el-result
        v-else-if="testResult === 'success'"
        icon="success"
        title="测试成功！"
        sub-title="恭喜！您的配置完全正确，可以开始使用了。"
      />

      <el-result
        v-else-if="testResult === 'failed'"
        icon="error"
        title="测试失败"
        :sub-title="testMessage"
      >
        <template #extra>
          <el-button type="primary" @click="openDiagnosis">
            🔍 查看诊断信息
          </el-button>
        </template>
      </el-result>
    </div>

    <!-- 测试详情 -->
    <el-collapse v-if="testDetails && testDetails.length > 0" v-model="activeNames">
      <el-collapse-item title="📋 测试详情" name="details">
        <el-timeline>
          <el-timeline-item
            v-for="(step, index) in testDetails"
            :key="index"
            :type="step.success ? 'success' : 'danger'"
            :timestamp="step.name"
          >
            {{ step.message }}
            <el-tag
              v-if="step.duration"
              size="small"
              type="info"
              style="margin-left: 10px"
            >
              {{ step.duration }}ms
            </el-tag>
          </el-timeline-item>
        </el-timeline>
      </el-collapse-item>
    </el-collapse>

    <!-- 测试选项 -->
    <el-card v-if="testResult === null" class="test-options">
      <template #header>
        <span>测试选项</span>
      </template>

      <el-form label-width="120px">
        <el-form-item label="测试消息内容">
          <el-input
            v-model="testMessage"
            type="textarea"
            :rows="3"
            placeholder="这是一条测试消息"
          />
        </el-form-item>

        <el-form-item label="测试目标">
          <el-checkbox-group v-model="testTargets">
            <el-checkbox label="discord">Discord</el-checkbox>
            <el-checkbox label="telegram">Telegram</el-checkbox>
            <el-checkbox label="feishu">飞书</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="$emit('prev')">
        上一步
      </el-button>

      <el-button
        v-if="testResult === null"
        type="primary"
        :loading="testResult === 'testing'"
        @click="handleTest"
      >
        🚀 开始测试
      </el-button>

      <el-button
        v-if="testResult === 'failed'"
        type="warning"
        @click="handleRetry"
      >
        🔄 重试
      </el-button>

      <el-button
        v-if="testResult === 'success'"
        type="success"
        @click="$emit('next')"
      >
        ✅ 完成向导
      </el-button>

      <el-button
        v-if="testResult !== null && testResult !== 'testing'"
        type="info"
        @click="handleSkip"
      >
        ⏭️ 跳过测试
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import api from '@/api'

const emit = defineEmits(['next', 'prev'])

// 状态
const testResult = ref(null)
const testMessage = ref('✅ KOOK 消息转发系统测试\n\n如果您看到这条消息，说明配置成功！')
const testTargets = ref(['discord', 'telegram', 'feishu'])
const testDetails = ref([])
const activeNames = ref(['details'])

// 方法
const handleTest = async () => {
  try {
    testResult.value = 'testing'
    testDetails.value = []

    // 调用测试 API
    const response = await api.post('/api/test/full-forwarding', {
      message: testMessage.value,
      targets: testTargets.value
    })

    if (response.success) {
      testResult.value = 'success'
      testDetails.value = response.steps || []
      ElMessage.success('🎉 测试成功！所有配置正常工作')
    } else {
      testResult.value = 'failed'
      testDetails.value = response.steps || []
      ElMessage.error('测试失败：' + response.message)
    }

  } catch (error) {
    testResult.value = 'failed'
    ElMessage.error('测试失败：' + (error.response?.data?.detail || error.message))
  }
}

const handleRetry = () => {
  testResult.value = null
  testDetails.value = []
}

const handleSkip = async () => {
  try {
    const confirmed = await ElMessageBox.confirm(
      '跳过测试将直接进入主界面，您可以稍后手动测试。确定要跳过吗？',
      '跳过测试',
      {
        confirmButtonText: '跳过',
        cancelButtonText: '继续测试',
        type: 'warning'
      }
    )

    if (confirmed) {
      emit('next')
    }
  } catch {
    // 用户取消
  }
}

const openDiagnosis = () => {
  // 打开诊断页面
  ElMessageBox.alert(
    '请查看测试详情，了解具体失败原因。如需帮助，请查看帮助文档或联系支持。',
    '诊断信息',
    {
      confirmButtonText: '我知道了'
    }
  )
}
</script>

<style scoped>
.wizard-step-test {
  padding: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 10px;
}

.description {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.test-status {
  margin: 30px 0;
}

.test-options {
  margin: 30px 0;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 30px;
}

.is-loading {
  font-size: 48px;
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
