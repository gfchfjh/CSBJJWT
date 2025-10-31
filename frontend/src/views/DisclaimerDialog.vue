<template>
  <el-dialog
    v-model="dialogVisible"
    title="⚠️ 免责声明"
    width="700px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    center
    class="disclaimer-dialog"
  >
    <div class="disclaimer-content">
      <el-alert
        type="warning"
        :closable="false"
        show-icon
        class="warning-alert"
      >
        <template #title>
          <strong>请仔细阅读以下重要声明</strong>
        </template>
      </el-alert>

      <div class="disclaimer-sections">
        <!-- 第1条：浏览器自动化风险 -->
        <div class="disclaimer-section">
          <div class="section-icon">
            <el-icon :size="24" color="#E6A23C"><Warning /></el-icon>
          </div>
          <div class="section-content">
            <h3>1. 浏览器自动化抓取风险</h3>
            <p>
              本软件通过浏览器自动化技术（Playwright）抓取KOOK消息，
              <strong>可能违反KOOK平台服务条款</strong>。
            </p>
            <ul>
              <li>KOOK官方未授权任何第三方工具进行消息抓取</li>
              <li>使用本软件可能导致您的KOOK账号被<strong>警告</strong>、<strong>限制</strong>或<strong>永久封禁</strong></li>
              <li>建议仅在测试环境或已获得平台明确授权的情况下使用</li>
            </ul>
          </div>
        </div>

        <!-- 第2条：账号安全风险 -->
        <div class="disclaimer-section">
          <div class="section-icon">
            <el-icon :size="24" color="#F56C6C"><Lock /></el-icon>
          </div>
          <div class="section-content">
            <h3>2. 账号安全与隐私风险</h3>
            <p>
              使用本软件需要提供KOOK账号凭证（密码或Cookie），存在以下风险：
            </p>
            <ul>
              <li>虽然软件采用AES-256加密存储，但无法100%保证凭证安全</li>
              <li>本地数据库文件如被他人获取，可能导致账号信息泄露</li>
              <li>建议使用独立的测试账号，避免使用主要账号</li>
              <li>定期更换密码，启用KOOK的两步验证功能</li>
            </ul>
          </div>
        </div>

        <!-- 第3条：版权与内容责任 -->
        <div class="disclaimer-section">
          <div class="section-icon">
            <el-icon :size="24" color="#409EFF"><Document /></el-icon>
          </div>
          <div class="section-content">
            <h3>3. 版权与内容责任</h3>
            <p>
              转发的消息内容可能涉及版权、隐私及其他法律问题：
            </p>
            <ul>
              <li>请确保您有权转发相关消息内容</li>
              <li>未经授权转发他人原创内容可能侵犯著作权</li>
              <li>转发涉密、敏感、违法信息需自行承担法律责任</li>
              <li>请遵守目标平台（Discord/Telegram/飞书）的服务条款</li>
            </ul>
          </div>
        </div>

        <!-- 第4条：法律责任 -->
        <div class="disclaimer-section">
          <div class="section-icon">
            <el-icon :size="24" color="#909399"><Document /></el-icon>
          </div>
          <div class="section-content">
            <h3>4. 法律责任与免责条款</h3>
            <p>
              使用本软件即表示您理解并同意：
            </p>
            <ul>
              <li>本软件<strong>仅供学习、研究和技术交流使用</strong></li>
              <li>开发者不对因使用本软件造成的任何损失承担责任，包括但不限于：
                <ul>
                  <li>账号被封禁、限制或损失</li>
                  <li>数据丢失、泄露或被篡改</li>
                  <li>因违反法律法规导致的法律纠纷</li>
                  <li>因软件缺陷导致的任何直接或间接损失</li>
                </ul>
              </li>
              <li>使用者需<strong>自行承担所有使用风险和法律责任</strong></li>
              <li>如因使用本软件涉及法律诉讼，使用者需自行应对，开发者不承担任何责任</li>
            </ul>
          </div>
        </div>

        <!-- 第5条：适用场景建议 -->
        <div class="disclaimer-section">
          <div class="section-icon">
            <el-icon :size="24" color="#67C23A"><Check /></el-icon>
          </div>
          <div class="section-content">
            <h3>5. 建议的合规使用场景</h3>
            <p>
              为降低风险，我们建议仅在以下场景使用：
            </p>
            <ul>
              <li>✅ <strong>自有社区/服务器</strong>：您是KOOK服务器的所有者或管理员</li>
              <li>✅ <strong>已获授权</strong>：已获得服务器所有者和相关用户的明确授权</li>
              <li>✅ <strong>测试环境</strong>：使用测试账号在私有环境中测试</li>
              <li>✅ <strong>个人备份</strong>：仅用于备份自己发送的消息</li>
              <li>❌ <strong>请勿用于</strong>：商业用途、批量营销、爬取他人隐私信息</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 同意确认 -->
      <div class="agreement-section">
        <el-checkbox v-model="agreed" size="large" class="agreement-checkbox">
          <span class="agreement-text">
            我已<strong>仔细阅读</strong>并<strong>完全理解</strong>以上所有条款，
            <strong>自愿承担所有使用风险和法律责任</strong>，
            并承诺在<strong>合法合规</strong>的前提下使用本软件
          </span>
        </el-checkbox>

        <el-alert
          v-if="showAgreementWarning"
          type="error"
          :closable="false"
          show-icon
          class="agreement-warning"
        >
          请仔细阅读免责声明并勾选同意选项后再继续
        </el-alert>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleDecline" size="large">
          拒绝并退出
        </el-button>
        <el-button
          type="primary"
          @click="handleAccept"
          :disabled="!agreed"
          size="large"
        >
          我已阅读并同意
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  Warning,
  Lock,
  Document,
  Check
} from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'accepted', 'declined'])

const dialogVisible = ref(props.modelValue)
const agreed = ref(false)
const showAgreementWarning = ref(false)

const handleAccept = async () => {
  if (!agreed.value) {
    showAgreementWarning.value = true
    setTimeout(() => {
      showAgreementWarning.value = false
    }, 3000)
    return
  }

  // 记录用户同意
  try {
    const response = await fetch('/api/disclaimer/accept', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        accepted_at: new Date().toISOString(),
        version: '1.0.0'
      })
    })

    if (response.ok) {
      dialogVisible.value = false
      emit('update:modelValue', false)
      emit('accepted')
    }
  } catch (error) {
    console.error('记录免责声明同意失败:', error)
    // 即使API失败，也允许继续（本地记录）
    dialogVisible.value = false
    emit('update:modelValue', false)
    emit('accepted')
  }
}

const handleDecline = async () => {
  const confirmed = await ElMessageBox.confirm(
    '拒绝免责声明将退出应用。您确定要退出吗？',
    '确认退出',
    {
      confirmButtonText: '确定退出',
      cancelButtonText: '返回继续',
      type: 'warning'
    }
  ).catch(() => false)

  if (confirmed) {
    emit('declined')
    // 关闭应用（如果在Electron中）
    if (window.electronAPI && window.electronAPI.closeApp) {
      window.electronAPI.closeApp()
    } else {
      // 在浏览器中，关闭当前标签页
      window.close()
    }
  }
}
</script>

<style scoped lang="scss">
.disclaimer-dialog {
  :deep(.el-dialog__body) {
    max-height: 70vh;
    overflow-y: auto;
    padding: 20px 30px;
  }

  :deep(.el-dialog__header) {
    padding: 20px 30px;
    background: linear-gradient(135deg, #FFA726 0%, #FB8C00 100%);
    color: white;
    
    .el-dialog__title {
      color: white;
      font-size: 20px;
      font-weight: bold;
    }
  }

  :deep(.el-dialog__footer) {
    padding: 20px 30px;
    border-top: 1px solid #e4e7ed;
  }
}

.disclaimer-content {
  .warning-alert {
    margin-bottom: 20px;
  }

  .disclaimer-sections {
    .disclaimer-section {
      display: flex;
      gap: 15px;
      margin-bottom: 25px;
      padding: 20px;
      background: #f9f9f9;
      border-radius: 8px;
      border-left: 4px solid #409EFF;

      &:nth-child(1) {
        border-left-color: #E6A23C;
      }
      &:nth-child(2) {
        border-left-color: #F56C6C;
      }
      &:nth-child(3) {
        border-left-color: #409EFF;
      }
      &:nth-child(4) {
        border-left-color: #909399;
      }
      &:nth-child(5) {
        border-left-color: #67C23A;
      }

      .section-icon {
        flex-shrink: 0;
        display: flex;
        align-items: flex-start;
        padding-top: 5px;
      }

      .section-content {
        flex: 1;

        h3 {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin: 0 0 12px 0;
        }

        p {
          font-size: 14px;
          line-height: 1.6;
          color: #606266;
          margin: 0 0 12px 0;

          strong {
            color: #E6A23C;
            font-weight: 600;
          }
        }

        ul {
          margin: 8px 0;
          padding-left: 20px;

          li {
            font-size: 14px;
            line-height: 1.8;
            color: #606266;
            margin-bottom: 6px;

            strong {
              color: #F56C6C;
              font-weight: 600;
            }

            ul {
              margin-top: 6px;

              li {
                list-style-type: circle;
                font-size: 13px;
              }
            }
          }
        }
      }
    }
  }

  .agreement-section {
    margin-top: 30px;
    padding: 25px;
    background: #FFF9E6;
    border: 2px solid #FFA726;
    border-radius: 8px;

    .agreement-checkbox {
      display: block;
      
      :deep(.el-checkbox__label) {
        white-space: normal;
        line-height: 1.8;
      }

      .agreement-text {
        font-size: 15px;
        color: #303133;
        font-weight: 500;

        strong {
          color: #E6A23C;
          font-weight: 700;
        }
      }
    }

    .agreement-warning {
      margin-top: 15px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

// 滚动条样式
:deep(.el-dialog__body) {
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;

    &:hover {
      background: #a8a8a8;
    }
  }
}
</style>
