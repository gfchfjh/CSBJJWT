<template>
  <div class="help-center">
    <el-page-header @back="$router.push('/')">
      <template #content>
        <span class="page-title">📚 帮助中心</span>
      </template>
    </el-page-header>

    <el-container class="help-container">
      <!-- 侧边栏 -->
      <el-aside width="250px">
        <el-menu
          :default-active="activeSection"
          @select="handleSelect"
        >
          <el-menu-item index="quick-start">
            <el-icon><Sunrise /></el-icon>
            <span>快速入门</span>
          </el-menu-item>

          <el-sub-menu index="tutorials">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>图文教程</span>
            </template>
            <el-menu-item index="tutorial-cookie">获取 KOOK Cookie</el-menu-item>
            <el-menu-item index="tutorial-discord">配置 Discord Webhook</el-menu-item>
            <el-menu-item index="tutorial-telegram">配置 Telegram Bot</el-menu-item>
            <el-menu-item index="tutorial-feishu">配置飞书应用</el-menu-item>
            <el-menu-item index="tutorial-mapping">设置频道映射</el-menu-item>
            <el-menu-item index="tutorial-filter">使用过滤规则</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="videos">
            <template #title>
              <el-icon><VideoCamera /></el-icon>
              <span>视频教程</span>
            </template>
            <el-menu-item index="video-overview">完整配置演示</el-menu-item>
            <el-menu-item index="video-cookie">Cookie 获取</el-menu-item>
            <el-menu-item index="video-bots">Bot 配置</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="faq">
            <el-icon><QuestionFilled /></el-icon>
            <span>常见问题</span>
          </el-menu-item>

          <el-menu-item index="troubleshooting">
            <el-icon><Tools /></el-icon>
            <span>故障排查</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 内容区 -->
      <el-main>
        <!-- 快速入门 -->
        <section v-if="activeSection === 'quick-start'" class="help-section">
          <h1>⚡ 快速入门</h1>
          <el-alert type="info" :closable="false">
            <p>欢迎使用 KOOK 消息转发系统！跟随以下步骤，5 分钟即可完成配置。</p>
          </el-alert>

          <el-timeline>
            <el-timeline-item timestamp="步骤 1" type="primary">
              <h3>添加 KOOK 账号</h3>
              <p>前往"账号管理"页面，使用 Cookie 或账号密码添加您的 KOOK 账号。</p>
              <el-button size="small" type="primary" @click="$router.push('/accounts')">
                去添加账号
              </el-button>
            </el-timeline-item>

            <el-timeline-item timestamp="步骤 2" type="success">
              <h3>配置目标 Bot</h3>
              <p>前往"机器人配置"页面，添加 Discord Webhook 或 Telegram Bot。</p>
              <el-button size="small" type="success" @click="$router.push('/bots')">
                去配置 Bot
              </el-button>
            </el-timeline-item>

            <el-timeline-item timestamp="步骤 3" type="warning">
              <h3>设置频道映射</h3>
              <p>前往"频道映射"页面，将 KOOK 频道映射到目标平台。</p>
              <el-button size="small" type="warning" @click="$router.push('/mapping')">
                去设置映射
              </el-button>
            </el-timeline-item>

            <el-timeline-item timestamp="步骤 4" type="info">
              <h3>开始使用</h3>
              <p>配置完成后，新消息将自动转发到目标平台！</p>
            </el-timeline-item>
          </el-timeline>
        </section>

        <!-- Cookie 获取教程 -->
        <section v-if="activeSection === 'tutorial-cookie'" class="help-section">
          <h1>🍪 如何获取 KOOK Cookie</h1>
          
          <el-alert type="warning" :closable="false">
            <p><strong>重要提示：</strong>Cookie 相当于您的账号密码，请勿分享给他人！</p>
          </el-alert>

          <h2>方法一：使用浏览器扩展（推荐）</h2>
          <el-steps direction="vertical">
            <el-step title="安装扩展" description="Chrome: 安装 EditThisCookie 扩展" />
            <el-step title="登录 KOOK" description="在浏览器中登录 KOOK 网页版" />
            <el-step title="导出 Cookie" description="点击扩展图标 → 导出 → JSON 格式" />
            <el-step title="导入系统" description="在本系统中粘贴 JSON 内容" />
          </el-steps>

          <h3>详细步骤（附截图）</h3>
          <el-carousel height="400px">
            <el-carousel-item>
              <div class="tutorial-image">
                <img src="/help-images/cookie-step1.png" alt="步骤 1">
                <p>步骤 1：安装 EditThisCookie 扩展</p>
              </div>
            </el-carousel-item>
            <el-carousel-item>
              <div class="tutorial-image">
                <img src="/help-images/cookie-step2.png" alt="步骤 2">
                <p>步骤 2：登录 KOOK 网页版</p>
              </div>
            </el-carousel-item>
            <el-carousel-item>
              <div class="tutorial-image">
                <img src="/help-images/cookie-step3.png" alt="步骤 3">
                <p>步骤 3：导出 Cookie</p>
              </div>
            </el-carousel-item>
          </el-carousel>

          <h2>方法二：手动提取（开发者工具）</h2>
          <el-collapse>
            <el-collapse-item title="展开详细步骤" name="manual">
              <ol>
                <li>在浏览器中打开 KOOK 网页版并登录</li>
                <li>按 F12 打开开发者工具</li>
                <li>切换到"应用程序"（Application）标签</li>
                <li>左侧选择"存储" → "Cookie" → "https://www.kookapp.cn"</li>
                <li>复制所有 Cookie 的名称和值</li>
                <li>按本系统格式粘贴</li>
              </ol>
            </el-collapse-item>
          </el-collapse>
        </section>

        <!-- FAQ -->
        <section v-if="activeSection === 'faq'" class="help-section">
          <h1>❓ 常见问题</h1>

          <el-collapse accordion>
            <el-collapse-item title="Q: KOOK 账号一直显示"离线"？" name="1">
              <p><strong>可能原因：</strong></p>
              <ol>
                <li>Cookie 已过期 → 解决：重新登录</li>
                <li>IP 被限制 → 解决：更换网络或使用代理</li>
                <li>账号被封禁 → 解决：联系 KOOK 客服</li>
              </ol>
            </el-collapse-item>

            <el-collapse-item title="Q: 消息转发延迟很大（超过 10 秒）？" name="2">
              <p><strong>可能原因：</strong></p>
              <ol>
                <li>消息队列积压 → 解决：查看队列状态，等待消化</li>
                <li>目标平台限流 → 解决：降低频道映射数量</li>
                <li>网络不稳定 → 解决：检查网络连接</li>
              </ol>
            </el-collapse-item>

            <el-collapse-item title="Q: 图片转发失败？" name="3">
              <p><strong>可能原因：</strong></p>
              <ol>
                <li>图片被防盗链 → 解决：已自动处理，重试即可</li>
                <li>图片过大 → 解决：程序会自动压缩</li>
                <li>目标平台限制 → 解决：使用图床模式</li>
              </ol>
            </el-collapse-item>

            <el-collapse-item title="Q: 如何卸载软件？" name="4">
              <p><strong>卸载步骤：</strong></p>
              <ul>
                <li>Windows：控制面板 → 程序 → 卸载</li>
                <li>macOS：直接删除应用</li>
                <li>数据会保留在用户文档目录，可手动删除</li>
              </ul>
            </el-collapse-item>

            <el-collapse-item title="Q: 支持哪些平台？" name="5">
              <p><strong>当前支持：</strong></p>
              <ul>
                <li>✅ Discord（通过 Webhook）</li>
                <li>✅ Telegram（通过 Bot）</li>
                <li>✅ 飞书（通过自建应用）</li>
                <li>🔜 企业微信（开发中）</li>
                <li>🔜 钉钉（开发中）</li>
              </ul>
            </el-collapse-item>

            <!-- 更多 FAQ -->
            <el-collapse-item title="Q: 如何设置开机自启？" name="6">
              <p><strong>设置方法：</strong></p>
              <p>前往"系统设置"页面，勾选"开机自动启动"选项。</p>
            </el-collapse-item>

            <el-collapse-item title="Q: Cookie 多久需要更新一次？" name="7">
              <p><strong>答：</strong></p>
              <p>KOOK 的 Cookie 通常 7-30 天过期。如果账号显示"离线"，请重新登录更新 Cookie。</p>
            </el-collapse-item>

            <el-collapse-item title="Q: 能同时监听多个 KOOK 账号吗？" name="8">
              <p><strong>答：</strong></p>
              <p>可以！在"账号管理"页面添加多个账号即可。</p>
            </el-collapse-item>

            <el-collapse-item title="Q: 转发的消息能保留原格式吗？" name="9">
              <p><strong>答：</strong></p>
              <p>可以！系统会自动转换 KMarkdown 格式为目标平台格式，保留粗体、斜体、代码块等。</p>
            </el-collapse-item>

            <el-collapse-item title="Q: 如何仅转发特定用户的消息？" name="10">
              <p><strong>答：</strong></p>
              <p>前往"过滤规则"页面，添加用户白名单即可。</p>
            </el-collapse-item>
          </el-collapse>
        </section>

        <!-- 故障排查 -->
        <section v-if="activeSection === 'troubleshooting'" class="help-section">
          <h1>🔧 故障排查指南</h1>

          <el-card class="diagnostic-tool">
            <template #header>
              <span>🔍 自动诊断工具</span>
            </template>
            <p>系统会自动检测常见问题并给出解决方案。</p>
            <el-button type="primary" @click="runDiagnostics">
              开始诊断
            </el-button>
          </el-card>

          <h2>常见问题自查清单</h2>
          <el-checkbox-group v-model="checklist">
            <el-checkbox label="check1">检查网络连接是否正常</el-checkbox>
            <el-checkbox label="check2">检查 KOOK 账号是否在线</el-checkbox>
            <el-checkbox label="check3">检查 Bot 配置是否正确</el-checkbox>
            <el-checkbox label="check4">检查频道映射是否已启用</el-checkbox>
            <el-checkbox label="check5">检查日志中是否有错误信息</el-checkbox>
          </el-checkbox-group>

          <h2>高级故障排查</h2>
          <el-collapse>
            <el-collapse-item title="如何查看详细日志？" name="logs">
              <p>日志文件位置：<code>用户文档/KookForwarder/data/logs/</code></p>
              <p>您可以在"日志"页面查看实时日志，或直接打开日志文件。</p>
            </el-collapse-item>

            <el-collapse-item title="如何重置配置？" name="reset">
              <p>如果遇到无法解决的问题，可以重置配置：</p>
              <ol>
                <li>备份重要数据（如 Bot Token、频道映射）</li>
                <li>删除配置文件：<code>用户文档/KookForwarder/data/config.db</code></li>
                <li>重新启动应用</li>
              </ol>
            </el-collapse-item>

            <el-collapse-item title="如何联系技术支持？" name="support">
              <p>如果以上方法都无法解决问题，请：</p>
              <ul>
                <li>📧 发送邮件至：support@example.com</li>
                <li>💬 在 GitHub 提交 Issue</li>
                <li>📱 加入官方 Discord 社群</li>
              </ul>
            </el-collapse-item>
          </el-collapse>
        </section>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Sunrise,
  Document,
  VideoCamera,
  QuestionFilled,
  Tools
} from '@element-plus/icons-vue'

const router = useRouter()

const activeSection = ref('quick-start')
const checklist = ref([])

const handleSelect = (key) => {
  activeSection.value = key
}

const runDiagnostics = () => {
  router.push('/wizard?step=environment')
  ElMessage.info('正在启动诊断工具...')
}
</script>

<style scoped>
.help-center {
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
}

.help-container {
  margin-top: 20px;
  min-height: 600px;
}

.help-section {
  max-width: 900px;
}

.help-section h1 {
  margin-bottom: 20px;
}

.help-section h2 {
  margin-top: 30px;
  margin-bottom: 15px;
}

.help-section h3 {
  margin-top: 20px;
  margin-bottom: 10px;
}

.tutorial-image {
  text-align: center;
  padding: 20px;
}

.tutorial-image img {
  max-width: 100%;
  max-height: 300px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.tutorial-image p {
  margin-top: 10px;
  color: #666;
}

.diagnostic-tool {
  margin: 20px 0;
}

.el-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 20px 0;
}

code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}
</style>
