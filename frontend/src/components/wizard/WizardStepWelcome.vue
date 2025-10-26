<template>
  <div class="step-welcome">
    <div class="welcome-header">
      <h1 class="welcome-title">🎉 欢迎使用KOOK消息转发系统</h1>
      <p class="welcome-subtitle">v6.3.0 傻瓜式一键安装版</p>
      <p class="welcome-description">本向导将引导您完成基础配置，预计耗时：3-5分钟</p>
    </div>

    <!-- ✅ P0-1优化完成：强制滚动阅读的免责声明 -->
    <div class="disclaimer-wrapper">
      <div class="disclaimer-header">
        <el-icon :size="32" color="#E6A23C"><WarningFilled /></el-icon>
        <h2>免责声明与使用协议</h2>
        <el-tag type="danger" size="large">必读</el-tag>
      </div>

      <div 
        ref="disclaimerScrollRef"
        class="disclaimer-scroll-area"
        :class="{ 'force-read': !hasScrolledToBottom }"
        @scroll="handleScroll"
      >
        <div class="disclaimer-content">
          <p class="disclaimer-intro">
            <strong>在使用本软件之前，请您务必仔细阅读并充分理解以下全部条款。</strong>
            本声明具有法律效力，一旦您开始使用本软件，即视为您已完全理解并同意遵守本声明的所有内容。
          </p>

          <div class="disclaimer-section">
            <h3>一、软件性质与用途</h3>
            <ol>
              <li>本软件是一款<strong>消息转发工具</strong>，通过浏览器自动化技术抓取KOOK平台的消息，并转发至其他平台（Discord、Telegram、飞书等）。</li>
              <li>本软件<strong>仅供个人学习、研究和技术交流使用</strong>，不得用于任何商业用途。</li>
              <li>本软件为<strong>开源软件</strong>，采用MIT许可证发布，源代码完全公开。</li>
            </ol>
          </div>

          <div class="disclaimer-section disclaimer-warning">
            <h3>二、重要风险提示 ⚠️</h3>
            <ol>
              <li>
                <strong class="risk-high">【账号风险】</strong>
                本软件通过浏览器自动化技术抓取KOOK消息，该行为<strong>可能违反KOOK平台的服务条款</strong>。
                使用本软件可能导致您的KOOK账号被<strong>警告、限制或永久封禁</strong>。
              </li>
              <li>
                <strong class="risk-high">【法律风险】</strong>
                转发他人发布的消息内容，可能涉及<strong>侵犯著作权、隐私权、肖像权</strong>等法律问题。
                请确保您有权转发相关内容，否则可能承担法律责任。
              </li>
              <li>
                <strong class="risk-medium">【隐私风险】</strong>
                本软件需要您的KOOK登录凭证（Cookie或账号密码），请<strong>妥善保管</strong>，不要与他人分享。
                开发者<strong>不会收集</strong>您的任何个人信息，所有数据均存储在本地。
              </li>
              <li>
                <strong class="risk-medium">【稳定性风险】</strong>
                KOOK平台可能随时更新其网页结构或API，导致本软件无法正常工作。
                开发者会尽力维护，但<strong>不保证100%可用</strong>。
              </li>
              <li>
                <strong class="risk-low">【兼容性风险】</strong>
                本软件在不同操作系统、不同网络环境下的表现可能存在差异。
              </li>
            </ol>
          </div>

          <div class="disclaimer-section">
            <h3>三、授权与限制</h3>
            <ol>
              <li><strong>授权场景</strong>：您应当仅在以下场景使用本软件：
                <ul>
                  <li>您是KOOK服务器的<strong>所有者或管理员</strong>，且已获得成员的同意</li>
                  <li>用于<strong>个人学习和研究</strong>目的，不传播或公开转发内容</li>
                  <li>用于<strong>备份自己发布的内容</strong></li>
                </ul>
              </li>
              <li><strong>禁止行为</strong>：严禁使用本软件进行以下行为：
                <ul>
                  <li>未经授权抓取他人的私密对话或敏感信息</li>
                  <li>用于商业盈利、广告推广或其他商业目的</li>
                  <li>传播违法违规、淫秽色情、暴力血腥等有害信息</li>
                  <li>恶意骚扰、诽谤、侵犯他人合法权益</li>
                  <li>破坏、干扰KOOK或其他平台的正常运营</li>
                </ul>
              </li>
            </ol>
          </div>

          <div class="disclaimer-section">
            <h3>四、免责条款</h3>
            <ol>
              <li><strong>开发者不承担责任</strong>：
                <ul>
                  <li>因使用本软件导致的<strong>任何直接或间接损失</strong>，包括但不限于账号封禁、数据丢失、法律纠纷等</li>
                  <li>因软件缺陷、错误、中断导致的任何损失</li>
                  <li>因第三方平台（KOOK、Discord、Telegram等）政策变化导致的不可用</li>
                  <li>因您违反法律法规或平台规则导致的任何后果</li>
                </ul>
              </li>
              <li><strong>无保证声明</strong>：
                本软件按"原样"提供，开发者<strong>不提供任何明示或暗示的保证</strong>，包括但不限于适销性、适用性、准确性、可靠性、安全性等。
              </li>
              <li><strong>第三方服务</strong>：
                本软件依赖第三方服务（Redis、Playwright、Chromium等），这些服务的问题不在开发者控制范围内。
              </li>
            </ol>
          </div>

          <div class="disclaimer-section">
            <h3>五、用户义务与责任</h3>
            <ol>
              <li>您应当<strong>年满18周岁</strong>，具有完全民事行为能力。</li>
              <li>您应当<strong>遵守所在国家/地区的法律法规</strong>，以及KOOK等平台的服务条款。</li>
              <li>您应当<strong>自行承担</strong>因使用本软件而产生的所有风险和责任。</li>
              <li>您应当<strong>尊重他人的合法权益</strong>，不得侵犯他人的隐私、著作权等。</li>
              <li>如果发现本软件存在安全漏洞或违法违规内容，应及时向开发者报告。</li>
            </ol>
          </div>

          <div class="disclaimer-section">
            <h3>六、知识产权</h3>
            <ol>
              <li>本软件的著作权归开发者所有，受著作权法和国际条约保护。</li>
              <li>本软件采用<strong>MIT开源许可证</strong>，您可以自由使用、修改、分发，但需保留原作者版权声明。</li>
              <li>本软件中使用的第三方库和组件，其著作权归各自作者所有。</li>
            </ol>
          </div>

          <div class="disclaimer-section">
            <h3>七、协议变更与终止</h3>
            <ol>
              <li>开发者保留<strong>随时修改本声明</strong>的权利，修改后的声明将在软件更新时生效。</li>
              <li>如您不同意修改后的声明，应立即<strong>停止使用本软件</strong>。</li>
              <li>开发者可随时<strong>停止维护或关闭本软件</strong>，无需事先通知。</li>
            </ol>
          </div>

          <div class="disclaimer-section disclaimer-final">
            <h3>八、最终声明</h3>
            <p>
              本声明的解释权归开发者所有。如本声明的任何条款被认定为无效或不可执行，
              该条款应在最小必要范围内被修改或删除，本声明的其余条款仍然有效。
            </p>
            <p class="disclaimer-emphasis">
              <strong>再次提醒：使用本软件即表示您已完全理解并同意本声明的所有内容，
              并自愿承担使用本软件的所有风险。如果您不同意本声明的任何内容，
              请立即点击"拒绝并退出"按钮，卸载本软件。</strong>
            </p>
          </div>

          <div class="scroll-hint" v-show="!hasScrolledToBottom">
            <el-icon :size="24" class="scroll-icon"><ArrowDown /></el-icon>
            <p>请向下滚动阅读完整声明</p>
          </div>
        </div>
      </div>

      <!-- 只有滚动到底部才显示 -->
      <div class="agreement-section" v-show="hasScrolledToBottom">
        <el-alert
          type="warning"
          :closable="false"
          show-icon
        >
          <p><strong>请确认您已完整阅读并理解上述免责声明</strong></p>
        </el-alert>

        <el-checkbox 
          v-model="agreed" 
          size="large"
          class="agreement-checkbox"
        >
          <strong>
            ☑️ 我已年满18周岁，已仔细阅读、充分理解并完全同意上述免责声明与使用协议的全部内容，
            自愿承担使用本软件的所有风险和责任
          </strong>
        </el-checkbox>

        <el-alert
          type="info"
          :closable="false"
          style="margin-top: 15px"
        >
          <p>
            💡 <strong>温馨提示</strong>：勾选上述复选框即表示您已做出法律承诺，
            请务必确保您真正理解并接受所有条款。
          </p>
        </el-alert>
      </div>

      <!-- 提示：未滚动到底部时显示 -->
      <el-alert
        v-show="!hasScrolledToBottom"
        type="warning"
        title="请先阅读完整的免责声明"
        :closable="false"
        show-icon
        style="margin-top: 20px"
      >
        您需要滚动到免责声明底部，完整阅读所有内容后才能继续。
      </el-alert>
    </div>

    <!-- 配置前准备 -->
    <div class="welcome-tips" v-show="hasScrolledToBottom && agreed">
      <el-alert
        title="📋 配置前准备"
        type="info"
        :closable="false"
        show-icon
      >
        <ul>
          <li>您需要准备<strong>KOOK账号的Cookie</strong>或账号密码</li>
          <li>至少配置<strong>一个转发目标</strong>（Discord/Telegram/飞书）</li>
          <li>确保您有权转发相关频道的消息内容</li>
          <li>配置完成后可以随时在设置中修改</li>
        </ul>
      </el-alert>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button
        type="primary"
        size="large"
        :disabled="!agreed || !hasScrolledToBottom"
        @click="handleNext"
      >
        <el-icon><CircleCheck /></el-icon>
        同意并继续配置
      </el-button>
      
      <el-button 
        type="danger"
        size="large" 
        @click="handleReject"
      >
        <el-icon><CircleClose /></el-icon>
        拒绝并退出应用
      </el-button>
    </div>

    <!-- 阅读进度提示 -->
    <div class="progress-hint" v-show="!hasScrolledToBottom">
      <el-progress 
        :percentage="scrollProgress" 
        :color="scrollProgress === 100 ? '#67C23A' : '#E6A23C'"
      >
        <template #default="{ percentage }">
          <span class="percentage-value">{{ percentage }}%</span>
        </template>
      </el-progress>
      <p class="progress-text">
        已阅读 {{ scrollProgress }}%，请继续向下滚动
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { 
  WarningFilled, 
  CircleCheck, 
  CircleClose, 
  ArrowDown 
} from '@element-plus/icons-vue'

const agreed = ref(false)
const hasScrolledToBottom = ref(false)
const disclaimerScrollRef = ref(null)
const scrollProgress = ref(0)

const emit = defineEmits(['next', 'reject'])

// ✅ P0-1完成：监听滚动事件
const handleScroll = (event) => {
  const element = event.target
  const scrollTop = element.scrollTop
  const scrollHeight = element.scrollHeight
  const clientHeight = element.clientHeight
  
  // 计算滚动进度
  const progress = Math.round((scrollTop / (scrollHeight - clientHeight)) * 100)
  scrollProgress.value = Math.min(progress, 100)
  
  // 判断是否滚动到底部（允许5px误差）
  if (scrollHeight - scrollTop - clientHeight < 5) {
    hasScrolledToBottom.value = true
  }
}

const handleNext = () => {
  if (!hasScrolledToBottom.value) {
    ElMessage.warning('请先滚动到免责声明底部，完整阅读所有内容')
    return
  }
  
  if (!agreed.value) {
    ElMessage.warning('请勾选同意协议后继续')
    return
  }
  
  // 二次确认
  ElMessageBox.confirm(
    '请再次确认：您已完整阅读并理解免责声明的所有内容，自愿承担使用本软件的所有风险？',
    '最终确认',
    {
      confirmButtonText: '确认同意',
      cancelButtonText: '我再看看',
      type: 'warning',
      distinguishCancelAndClose: true
    }
  ).then(() => {
    // 记录用户同意时间
    const agreementTime = new Date().toISOString()
    localStorage.setItem('disclaimer_agreed', 'true')
    localStorage.setItem('disclaimer_agreed_time', agreementTime)
    localStorage.setItem('disclaimer_version', '6.3.0')
    
    ElMessage.success('✅ 已确认，开始配置向导')
    emit('next')
  }).catch((action) => {
    if (action === 'cancel') {
      ElMessage.info('请仔细阅读免责声明')
    }
  })
}

// ✅ P0-1完成：拒绝时真正退出应用
const handleReject = () => {
  ElMessageBox.confirm(
    '您拒绝了免责声明，应用将立即关闭。\n\n如需使用本软件，请重新启动并同意免责声明。',
    '退出应用',
    {
      confirmButtonText: '确定退出',
      cancelButtonText: '我再想想',
      type: 'error',
      distinguishCancelAndClose: true
    }
  ).then(() => {
    // 记录拒绝
    localStorage.setItem('disclaimer_rejected', 'true')
    localStorage.setItem('disclaimer_rejected_time', new Date().toISOString())
    
    // 尝试关闭Electron窗口
    if (window.electron && window.electron.quit) {
      window.electron.quit()
    } else if (window.electron && window.electron.closeWindow) {
      window.electron.closeWindow()
    } else {
      // 如果不是Electron环境，关闭窗口
      window.close()
      
      // 如果无法关闭，显示提示
      setTimeout(() => {
        ElMessage.error('无法自动关闭窗口，请手动关闭浏览器标签页')
      }, 100)
    }
  }).catch(() => {
    // 用户取消
  })
}
</script>

<style scoped>
/* ✅ P0-1完成：全新样式系统 */

.step-welcome {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.welcome-title {
  font-size: 32px;
  margin: 0 0 10px 0;
  font-weight: bold;
}

.welcome-subtitle {
  font-size: 16px;
  margin: 0 0 10px 0;
  opacity: 0.9;
}

.welcome-description {
  font-size: 14px;
  margin: 0;
  opacity: 0.8;
}

.disclaimer-wrapper {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.disclaimer-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #E6A23C;
}

.disclaimer-header h2 {
  margin: 0;
  font-size: 24px;
  color: #E6A23C;
}

.disclaimer-scroll-area {
  max-height: 500px;
  overflow-y: auto;
  border: 2px solid #DCDFE6;
  border-radius: 8px;
  padding: 25px;
  background: #FAFAFA;
  position: relative;
  scroll-behavior: smooth;
}

/* 强制阅读样式 */
.disclaimer-scroll-area.force-read {
  border-color: #E6A23C;
  background: linear-gradient(to bottom, 
    rgba(230, 162, 60, 0.05) 0%, 
    transparent 100%);
}

/* 滚动条样式 */
.disclaimer-scroll-area::-webkit-scrollbar {
  width: 10px;
}

.disclaimer-scroll-area::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 5px;
}

.disclaimer-scroll-area::-webkit-scrollbar-thumb {
  background: #E6A23C;
  border-radius: 5px;
}

.disclaimer-scroll-area::-webkit-scrollbar-thumb:hover {
  background: #D89E36;
}

.disclaimer-content {
  text-align: left;
  line-height: 1.8;
  color: #303133;
}

.disclaimer-intro {
  font-size: 15px;
  padding: 15px;
  background: #FFF7E6;
  border-left: 4px solid #E6A23C;
  margin-bottom: 25px;
  border-radius: 4px;
}

.disclaimer-section {
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #EBEEF5;
}

.disclaimer-section h3 {
  color: #409EFF;
  font-size: 18px;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #409EFF;
}

.disclaimer-warning h3 {
  color: #F56C6C;
  border-bottom-color: #F56C6C;
}

.disclaimer-section ol {
  margin: 0;
  padding-left: 25px;
}

.disclaimer-section li {
  margin: 12px 0;
  line-height: 1.8;
}

.disclaimer-section ul {
  margin: 8px 0;
  padding-left: 25px;
  list-style-type: disc;
}

.disclaimer-section ul li {
  margin: 6px 0;
}

.risk-high {
  color: #F56C6C;
  background: #FEF0F0;
  padding: 2px 8px;
  border-radius: 4px;
}

.risk-medium {
  color: #E6A23C;
  background: #FDF6EC;
  padding: 2px 8px;
  border-radius: 4px;
}

.risk-low {
  color: #909399;
  background: #F4F4F5;
  padding: 2px 8px;
  border-radius: 4px;
}

.disclaimer-final {
  background: #FFF7E6;
  border: 2px solid #E6A23C;
}

.disclaimer-emphasis {
  font-size: 15px;
  color: #F56C6C;
  font-weight: bold;
  padding: 15px;
  background: #FEF0F0;
  border-radius: 4px;
  margin-top: 15px;
  text-align: center;
}

.scroll-hint {
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  padding: 15px;
  background: linear-gradient(to bottom, transparent, rgba(250, 250, 250, 0.95));
  animation: bounce 2s infinite;
}

.scroll-icon {
  color: #E6A23C;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.scroll-hint p {
  margin: 5px 0 0 0;
  color: #E6A23C;
  font-weight: bold;
}

.agreement-section {
  margin: 25px 0;
  padding: 20px;
  background: #F0F9FF;
  border-radius: 8px;
  border: 2px solid #409EFF;
}

.agreement-checkbox {
  display: block;
  margin: 20px 0;
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 2px solid #67C23A;
}

.agreement-checkbox :deep(.el-checkbox__label) {
  line-height: 1.8;
  white-space: normal;
  word-break: break-word;
}

.welcome-tips {
  margin: 30px 0;
}

.welcome-tips ul {
  margin: 10px 0;
  padding-left: 25px;
}

.welcome-tips li {
  margin: 8px 0;
  line-height: 1.6;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.action-buttons .el-button {
  min-width: 200px;
  height: 50px;
  font-size: 16px;
}

.progress-hint {
  margin-top: 20px;
  padding: 15px;
  background: #F4F4F5;
  border-radius: 8px;
  text-align: center;
}

.progress-text {
  margin: 10px 0 0 0;
  color: #606266;
  font-size: 14px;
}

.percentage-value {
  font-weight: bold;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .step-welcome {
    padding: 10px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .disclaimer-scroll-area {
    max-height: 400px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
}
</style>
