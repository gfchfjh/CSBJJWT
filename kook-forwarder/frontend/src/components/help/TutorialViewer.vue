<template>
  <div class="tutorial-viewer">
    <el-tabs v-model="activeTutorial" type="border-card">
      <!-- Cookie获取教程 -->
      <el-tab-pane label="📖 Cookie获取教程" name="cookie">
        <div class="tutorial-content">
          <h2>如何获取KOOK Cookie</h2>
          <p class="intro">Cookie是自动登录的凭证。以下提供3种获取方式，推荐使用方法一。</p>

          <el-divider />

          <!-- 方法一：Chrome扩展 -->
          <div class="method">
            <h3>
              <el-tag type="success">推荐</el-tag>
              方法一：使用Chrome扩展（最简单）
            </h3>

            <el-steps direction="vertical" :space="200">
              <el-step status="process">
                <template #title>
                  <h4>步骤1：安装Chrome扩展</h4>
                </template>
                <template #description>
                  <div class="step-content">
                    <el-image
                      v-if="tutorialImages.chromeExtensionInstall"
                      :src="tutorialImages.chromeExtensionInstall"
                      fit="contain"
                      style="width: 100%; max-width: 600px"
                    />
                    <ol>
                      <li>在Chrome浏览器中访问扩展商店</li>
                      <li>搜索 "KOOK Cookie Exporter"</li>
                      <li>点击"添加到Chrome"按钮</li>
                      <li>等待安装完成（几秒钟）</li>
                    </ol>
                    <el-alert type="info" :closable="false">
                      💡 <strong>提示：</strong>扩展完全免费且开源，代码可在GitHub查看，保证安全。
                    </el-alert>
                  </div>
                </template>
              </el-step>

              <el-step status="process">
                <template #title>
                  <h4>步骤2：登录KOOK并导出Cookie</h4>
                </template>
                <template #description>
                  <div class="step-content">
                    <el-image
                      v-if="tutorialImages.exportCookie"
                      :src="tutorialImages.exportCookie"
                      fit="contain"
                      style="width: 100%; max-width: 600px"
                    />
                    <ol>
                      <li>访问并登录KOOK网页版（<el-link type="primary" href="https://www.kookapp.cn" target="_blank">www.kookapp.cn</el-link>）</li>
                      <li>确保已成功登录，能看到频道列表</li>
                      <li>点击浏览器右上角的扩展图标</li>
                      <li>点击"导出Cookie"按钮</li>
                      <li>Cookie会自动复制到剪贴板！</li>
                    </ol>
                    <el-alert type="success" :closable="false">
                      ✅ <strong>成功标志：</strong>看到"Cookie已复制"的提示
                    </el-alert>
                  </div>
                </template>
              </el-step>

              <el-step status="process">
                <template #title>
                  <h4>步骤3：粘贴到本应用</h4>
                </template>
                <template #description>
                  <div class="step-content">
                    <ol>
                      <li>返回KOOK消息转发系统</li>
                      <li>进入"账号管理"页面</li>
                      <li>点击"添加账号"按钮</li>
                      <li>选择"Cookie导入"标签</li>
                      <li>在文本框中按 <kbd>Ctrl+V</kbd>（Mac用<kbd>⌘+V</kbd>）粘贴</li>
                      <li>点击"验证并添加"按钮</li>
                    </ol>
                    <el-alert type="success" :closable="false">
                      🎉 <strong>完成！</strong>现在可以开始监听KOOK消息了
                    </el-alert>
                  </div>
                </template>
              </el-step>
            </el-steps>

            <div class="video-section">
              <h4>📺 视频教程</h4>
              <el-button type="primary" @click="openVideo('cookie-chrome-ext')">
                <el-icon><VideoPlay /></el-icon>
                观看完整视频演示（3分钟）
              </el-button>
            </div>
          </div>

          <el-divider />

          <!-- 方法二：开发者工具 -->
          <div class="method">
            <h3>
              <el-tag>备选</el-tag>
              方法二：使用浏览器开发者工具
            </h3>

            <el-collapse>
              <el-collapse-item title="展开查看详细步骤" name="devtools">
                <el-steps direction="vertical">
                  <el-step>
                    <template #title>打开开发者工具</template>
                    <template #description>
                      <p>在KOOK网页版（已登录状态）按<kbd>F12</kbd>键，或右键选择"检查"</p>
                    </template>
                  </el-step>
                  <el-step>
                    <template #title>切换到Application标签</template>
                    <template #description>
                      <p>在开发者工具中找到并点击"Application"（应用）标签页</p>
                    </template>
                  </el-step>
                  <el-step>
                    <template #title>查找Cookie</template>
                    <template #description>
                      <p>左侧找到"Cookies" → "https://www.kookapp.cn"</p>
                    </template>
                  </el-step>
                  <el-step>
                    <template #title>导出Cookie</template>
                    <template #description>
                      <p>选中所有Cookie（Ctrl+A），右键选择"Copy"</p>
                    </template>
                  </el-step>
                </el-steps>
              </el-collapse-item>
            </el-collapse>
          </div>

          <el-divider />

          <!-- 常见问题 -->
          <div class="troubleshooting">
            <h3>❓ 遇到问题？</h3>
            <el-collapse accordion>
              <el-collapse-item title="Q: 提示'Cookie无效'怎么办？" name="invalid">
                <p><strong>可能原因：</strong></p>
                <ul>
                  <li>未登录KOOK就导出了Cookie</li>
                  <li>Cookie格式不正确</li>
                  <li>Cookie已过期</li>
                </ul>
                <p><strong>解决方案：</strong></p>
                <ol>
                  <li>确保已登录KOOK网页版</li>
                  <li>重新导出Cookie</li>
                  <li>使用Chrome扩展（推荐，不易出错）</li>
                </ol>
                <el-button size="small" type="primary" @click="runDiagnostic('cookie')">
                  <el-icon><Tools /></el-icon>
                  运行Cookie诊断工具
                </el-button>
              </el-collapse-item>

              <el-collapse-item title="Q: 提示'Cookie已过期'怎么办？" name="expired">
                <p>Cookie有效期一般为7-30天。过期后需要重新导出。</p>
                <p><strong>解决方案：</strong></p>
                <ol>
                  <li>重新登录KOOK网页版</li>
                  <li>导出新的Cookie</li>
                  <li>在本应用中更新Cookie</li>
                </ol>
              </el-collapse-item>

              <el-collapse-item title="Q: Chrome扩展在哪里下载？" name="extension">
                <p>扩展在Chrome Web Store中搜索"KOOK Cookie Exporter"，或使用以下链接：</p>
                <el-link type="primary" :underline="false">
                  https://chrome.google.com/webstore/detail/kook-cookie-exporter
                </el-link>
                <p style="margin-top: 10px">如果无法访问Chrome商店，可以下载本地版本：</p>
                <el-button size="small" @click="downloadExtension">
                  <el-icon><Download /></el-icon>
                  下载本地扩展包
                </el-button>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </el-tab-pane>

      <!-- Discord Webhook教程 -->
      <el-tab-pane label="📘 Discord配置" name="discord">
        <div class="tutorial-content">
          <h2>如何创建Discord Webhook</h2>
          
          <el-steps direction="vertical" :space="200">
            <el-step>
              <template #title>
                <h4>步骤1：打开服务器设置</h4>
              </template>
              <template #description>
                <p>在Discord中，右键点击您的服务器图标，选择"服务器设置"</p>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤2：创建Webhook</h4>
              </template>
              <template #description>
                <p>左侧菜单中找到"整合" → "Webhook" → 点击"新建Webhook"</p>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤3：配置Webhook</h4>
              </template>
              <template #description>
                <ol>
                  <li>设置Webhook名称（如：KOOK消息转发）</li>
                  <li>选择要接收消息的频道</li>
                  <li>可选：上传头像</li>
                  <li>点击"复制Webhook URL"</li>
                </ol>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤4：粘贴到本应用</h4>
              </template>
              <template #description>
                <p>在本应用的"机器人配置"页面，粘贴Webhook URL并测试连接</p>
              </template>
            </el-step>
          </el-steps>

          <div class="video-section">
            <el-button type="primary" @click="openVideo('discord-webhook')">
              <el-icon><VideoPlay /></el-icon>
              观看视频教程（2分钟）
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- Telegram Bot教程 -->
      <el-tab-pane label="📗 Telegram配置" name="telegram">
        <div class="tutorial-content">
          <h2>如何创建Telegram Bot</h2>
          
          <el-steps direction="vertical" :space="200">
            <el-step>
              <template #title>
                <h4>步骤1：找到BotFather</h4>
              </template>
              <template #description>
                <p>在Telegram中搜索 <el-tag type="primary">@BotFather</el-tag> 并打开对话</p>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤2：创建Bot</h4>
              </template>
              <template #description>
                <ol>
                  <li>发送命令：<el-tag>/newbot</el-tag></li>
                  <li>按提示输入Bot名称（如：KOOK消息转发Bot）</li>
                  <li>输入Bot用户名（必须以bot结尾，如：kook_forwarder_bot）</li>
                  <li>创建成功后，BotFather会发送Bot Token</li>
                </ol>
                <el-alert type="warning" :closable="false">
                  ⚠️ <strong>重要：</strong>请妥善保管Token，不要泄露给他人
                </el-alert>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤3：将Bot添加到群组</h4>
              </template>
              <template #description>
                <ol>
                  <li>打开目标Telegram群组</li>
                  <li>点击群组信息 → 添加成员</li>
                  <li>搜索您刚创建的Bot并添加</li>
                  <li>（可选）将Bot设置为管理员</li>
                </ol>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤4：获取Chat ID</h4>
              </template>
              <template #description>
                <p>在本应用的Bot配置页面：</p>
                <ol>
                  <li>填写Bot Token</li>
                  <li>在群组中发送任意消息</li>
                  <li>点击"自动获取"按钮</li>
                  <li>Chat ID会自动填充</li>
                </ol>
                <el-alert type="success" :closable="false">
                  ✅ 或手动获取：发送消息后访问 <el-text type="primary">https://api.telegram.org/bot{TOKEN}/getUpdates</el-text>
                </el-alert>
              </template>
            </el-step>
          </el-steps>

          <div class="video-section">
            <el-button type="primary" @click="openVideo('telegram-bot')">
              <el-icon><VideoPlay /></el-icon>
              观看视频教程（4分钟）
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- 飞书应用教程 -->
      <el-tab-pane label="📕 飞书配置" name="feishu">
        <div class="tutorial-content">
          <h2>如何创建飞书自建应用</h2>
          
          <el-alert type="info" :closable="false" style="margin-bottom: 20px">
            飞书配置相对复杂，建议观看完整视频教程
          </el-alert>

          <el-steps direction="vertical" :space="200">
            <el-step>
              <template #title>
                <h4>步骤1：访问飞书开放平台</h4>
              </template>
              <template #description>
                <p>访问 <el-link type="primary" href="https://open.feishu.cn" target="_blank">https://open.feishu.cn</el-link></p>
                <p>使用飞书账号登录</p>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤2：创建自建应用</h4>
              </template>
              <template #description>
                <ol>
                  <li>点击"创建企业自建应用"</li>
                  <li>填写应用名称和描述</li>
                  <li>上传应用图标</li>
                  <li>点击"创建"</li>
                </ol>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤3：获取App ID和Secret</h4>
              </template>
              <template #description>
                <ol>
                  <li>进入应用详情页</li>
                  <li>在"凭证与基础信息"中找到App ID</li>
                  <li>点击"查看"获取App Secret</li>
                  <li>复制这两个信息</li>
                </ol>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤4：开启机器人能力</h4>
              </template>
              <template #description>
                <ol>
                  <li>在应用管理页面，点击"添加应用能力"</li>
                  <li>选择"机器人"</li>
                  <li>配置机器人信息和权限</li>
                  <li>发布应用版本</li>
                </ol>
              </template>
            </el-step>

            <el-step>
              <template #title>
                <h4>步骤5：将机器人添加到群组</h4>
              </template>
              <template #description>
                <ol>
                  <li>在飞书群组中，点击设置</li>
                  <li>选择"群机器人" → "添加机器人"</li>
                  <li>搜索并添加您创建的机器人</li>
                </ol>
              </template>
            </el-step>
          </el-steps>

          <div class="video-section">
            <el-button type="primary" @click="openVideo('feishu-app')">
              <el-icon><VideoPlay /></el-icon>
              观看视频教程（5分钟）
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- 频道映射教程 -->
      <el-tab-pane label="🔀 频道映射" name="mapping">
        <div class="tutorial-content">
          <h2>频道映射配置详解</h2>

          <el-alert type="info" :closable="false" style="margin-bottom: 20px">
            频道映射定义了消息的转发规则：哪个KOOK频道的消息转发到哪个目标平台频道
          </el-alert>

          <h3>配置方式</h3>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon><MagicStick /></el-icon>
                    <span>智能映射（推荐）</span>
                  </div>
                </template>
                <p>系统自动分析频道名称，智能推荐映射关系</p>
                <p><strong>优点：</strong>快速、准确率高</p>
                <p><strong>适用：</strong>频道名称相似的情况</p>
                <el-button type="primary" size="small" @click="gotoMapping">
                  立即体验
                </el-button>
              </el-card>
            </el-col>

            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon><Edit /></el-icon>
                    <span>手动映射</span>
                  </div>
                </template>
                <p>手动选择每个映射关系</p>
                <p><strong>优点：</strong>完全可控</p>
                <p><strong>适用：</strong>复杂的映射需求</p>
                <el-button type="primary" size="small" @click="gotoMapping">
                  开始配置
                </el-button>
              </el-card>
            </el-col>
          </el-row>

          <h3 style="margin-top: 30px">💡 使用技巧</h3>
          <ul class="tips-list">
            <li>
              <el-icon color="#67C23A"><Check /></el-icon>
              一个KOOK频道可以同时转发到多个目标平台
            </li>
            <li>
              <el-icon color="#67C23A"><Check /></el-icon>
              可以为不同映射设置不同的过滤规则
            </li>
            <li>
              <el-icon color="#67C23A"><Check /></el-icon>
              使用拖拽功能快速创建映射关系
            </li>
            <li>
              <el-icon color="#67C23A"><Check /></el-icon>
              测试功能可以验证映射是否正常工作
            </li>
          </ul>
        </div>
      </el-tab-pane>

      <!-- 过滤规则教程 -->
      <el-tab-pane label="🔧 过滤规则" name="filter">
        <div class="tutorial-content">
          <h2>消息过滤规则使用指南</h2>

          <p class="intro">过滤规则可以控制哪些消息被转发，哪些被忽略。</p>

          <h3>过滤类型</h3>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="关键词黑名单">
              包含指定关键词的消息<strong>不转发</strong>
              <br>
              <el-tag size="small">示例：广告、代练、外挂</el-tag>
            </el-descriptions-item>

            <el-descriptions-item label="关键词白名单">
              <strong>仅转发</strong>包含指定关键词的消息
              <br>
              <el-tag size="small">示例：官方公告、版本更新</el-tag>
            </el-descriptions-item>

            <el-descriptions-item label="用户黑名单">
              指定用户的消息<strong>不转发</strong>
            </el-descriptions-item>

            <el-descriptions-item label="用户白名单">
              <strong>仅转发</strong>指定用户的消息
            </el-descriptions-item>

            <el-descriptions-item label="正则表达式">
              使用正则表达式进行高级过滤
              <br>
              <el-tag size="small">示例：^\[公告\].*</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <h3 style="margin-top: 30px">⚙️ 配置建议</h3>

          <el-alert type="warning" :closable="false" style="margin-bottom: 15px">
            <strong>注意：</strong>黑名单和白名单不能同时启用！
          </el-alert>

          <el-timeline>
            <el-timeline-item color="#67C23A">
              <strong>场景1：过滤垃圾信息</strong>
              <p>使用关键词黑名单，添加：广告、代练、外挂、刷屏</p>
            </el-timeline-item>

            <el-timeline-item color="#409EFF">
              <strong>场景2：只转发官方消息</strong>
              <p>使用用户白名单，只添加官方管理员账号</p>
            </el-timeline-item>

            <el-timeline-item color="#E6A23C">
              <strong>场景3：只转发公告类消息</strong>
              <p>使用关键词白名单，添加：公告、通知、更新</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-tab-pane>

      <!-- 常见问题FAQ -->
      <el-tab-pane label="❓ 常见问题" name="faq">
        <div class="tutorial-content">
          <h2>常见问题FAQ</h2>

          <el-collapse accordion>
            <el-collapse-item name="q1">
              <template #title>
                <strong>Q: KOOK账号一直显示"离线"？</strong>
              </template>
              <div class="faq-answer">
                <p><strong>可能原因：</strong></p>
                <ol>
                  <li>Cookie已过期 → <strong>解决：</strong>重新导出并更新Cookie</li>
                  <li>IP被KOOK限制 → <strong>解决：</strong>更换网络或等待一段时间</li>
                  <li>账号被封禁 → <strong>解决：</strong>联系KOOK客服</li>
                  <li>浏览器崩溃 → <strong>解决：</strong>查看日志，重启应用</li>
                </ol>
                <el-button size="small" type="primary" @click="runDiagnostic('account-offline')">
                  运行诊断工具
                </el-button>
              </div>
            </el-collapse-item>

            <el-collapse-item name="q2">
              <template #title>
                <strong>Q: 消息转发延迟很大（超过10秒）？</strong>
              </template>
              <div class="faq-answer">
                <p><strong>可能原因：</strong></p>
                <ol>
                  <li>消息队列积压 → <strong>解决：</strong>查看队列状态，等待消化或重启服务</li>
                  <li>目标平台限流 → <strong>解决：</strong>降低频道映射数量</li>
                  <li>网络不稳定 → <strong>解决：</strong>检查网络连接</li>
                  <li>图片下载慢 → <strong>解决：</strong>在设置中调整图片策略</li>
                </ol>
              </div>
            </el-collapse-item>

            <el-collapse-item name="q3">
              <template #title>
                <strong>Q: 图片转发失败？</strong>
              </template>
              <div class="faq-answer">
                <p><strong>可能原因：</strong></p>
                <ol>
                  <li>图片被防盗链 → <strong>解决：</strong>程序会自动处理，重试即可</li>
                  <li>图片过大 → <strong>解决：</strong>程序会自动压缩，或手动设置压缩参数</li>
                  <li>目标平台限制 → <strong>解决：</strong>使用图床模式</li>
                  <li>网络超时 → <strong>解决：</strong>增加超时时间或检查网络</li>
                </ol>
                <p style="margin-top: 10px">
                  <strong>推荐设置：</strong>在系统设置中选择"智能模式"，可自动处理大部分问题
                </p>
              </div>
            </el-collapse-item>

            <el-collapse-item name="q4">
              <template #title>
                <strong>Q: 如何卸载软件？</strong>
              </template>
              <div class="faq-answer">
                <p><strong>Windows：</strong></p>
                <p>控制面板 → 程序和功能 → 找到"KOOK消息转发系统" → 卸载</p>
                
                <p style="margin-top: 15px"><strong>macOS：</strong></p>
                <p>在应用程序文件夹中，将应用拖到废纸篓</p>
                
                <p style="margin-top: 15px"><strong>Linux：</strong></p>
                <p>直接删除AppImage文件</p>
                
                <el-alert type="info" :closable="false" style="margin-top: 15px">
                  📝 <strong>数据清理：</strong>卸载后，数据会保留在用户文档目录中（<el-text type="primary">~/Documents/KookForwarder</el-text>），如需彻底清理请手动删除此文件夹
                </el-alert>
              </div>
            </el-collapse-item>

            <el-collapse-item name="q5">
              <template #title>
                <strong>Q: 转发的消息格式乱了？</strong>
              </template>
              <div class="faq-answer">
                <p>不同平台支持的格式不同：</p>
                <ul>
                  <li><strong>Discord：</strong>支持Markdown格式（粗体、斜体、代码块等）</li>
                  <li><strong>Telegram：</strong>支持HTML格式，Markdown需要转换</li>
                  <li><strong>飞书：</strong>支持富文本，但部分格式可能不兼容</li>
                </ul>
                <p style="margin-top: 10px">
                  系统会自动转换格式，如果转换效果不理想，可在设置中调整格式化选项。
                </p>
              </div>
            </el-collapse-item>

            <el-collapse-item name="q6">
              <template #title>
                <strong>Q: 如何备份配置？</strong>
              </template>
              <div class="faq-answer">
                <p>系统提供自动和手动两种备份方式：</p>
                <p><strong>自动备份：</strong></p>
                <p>在设置 → 备份与恢复中，开启"每天自动备份"</p>
                
                <p style="margin-top: 15px"><strong>手动备份：</strong></p>
                <ol>
                  <li>进入设置 → 备份与恢复</li>
                  <li>点击"立即备份配置"</li>
                  <li>备份文件会保存到：<el-text type="primary">~/Documents/KookForwarder/backup/</el-text></li>
                </ol>
                
                <el-button size="small" type="primary" @click="gotoBackup">
                  前往备份页面
                </el-button>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-tab-pane>

      <!-- 故障排查 -->
      <el-tab-pane label="🔍 故障排查" name="troubleshooting">
        <div class="tutorial-content">
          <h2>智能故障排查工具</h2>

          <el-alert type="info" :closable="false" style="margin-bottom: 20px">
            选择您遇到的问题，系统会自动诊断并提供解决方案
          </el-alert>

          <el-space direction="vertical" style="width: 100%" :size="15">
            <el-card
              v-for="issue in commonIssues"
              :key="issue.id"
              shadow="hover"
              class="issue-card"
            >
              <div class="issue-header">
                <div>
                  <h4>{{ issue.title }}</h4>
                  <p class="issue-desc">{{ issue.description }}</p>
                </div>
                <el-button type="primary" @click="diagnose(issue.id)">
                  <el-icon><Tools /></el-icon>
                  诊断
                </el-button>
              </div>
            </el-card>
          </el-space>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  VideoPlay,
  Download,
  Tools,
  MagicStick,
  Edit,
  Check
} from '@element-plus/icons-vue'

const router = useRouter()

// 数据
const activeTutorial = ref('cookie')

const tutorialImages = reactive({
  chromeExtensionInstall: null,  // TODO: 添加实际图片
  exportCookie: null
})

const commonIssues = ref([
  {
    id: 'account-offline',
    title: '账号显示离线',
    description: 'KOOK账号连接状态异常'
  },
  {
    id: 'cookie-invalid',
    title: 'Cookie验证失败',
    description: '导入的Cookie无法使用'
  },
  {
    id: 'message-delay',
    title: '消息转发延迟大',
    description: '转发延迟超过10秒'
  },
  {
    id: 'image-failed',
    title: '图片转发失败',
    description: '图片无法正常转发'
  },
  {
    id: 'bot-error',
    title: 'Bot连接错误',
    description: 'Discord/Telegram/飞书Bot无法连接'
  }
])

// 方法
const openVideo = (videoId) => {
  // TODO: 实现视频播放
  ElMessage.info('视频教程功能开发中，敬请期待')
  
  // 示例：打开外部链接
  // const videoUrl = `https://tutorials.kook-forwarder.com/${videoId}`
  // window.open(videoUrl, '_blank')
}

const downloadExtension = () => {
  ElMessage.info('本地扩展包下载功能开发中')
  // TODO: 提供扩展包下载
}

const runDiagnostic = (type) => {
  ElMessage.info(`启动诊断工具: ${type}`)
  // TODO: 实现诊断工具
}

const gotoMapping = () => {
  router.push('/mapping')
}

const gotoBackup = () => {
  router.push('/settings?tab=backup')
}

const diagnose = (issueId) => {
  ElMessage.info(`诊断问题: ${issueId}`)
  // TODO: 实现智能诊断
}
</script>

<style scoped>
.tutorial-viewer {
  padding: 20px;
}

.tutorial-content {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.tutorial-content h2 {
  font-size: 24px;
  margin-bottom: 15px;
  color: #303133;
}

.tutorial-content h3 {
  font-size: 18px;
  margin: 25px 0 15px 0;
  color: #606266;
}

.intro {
  font-size: 14px;
  color: #909399;
  margin-bottom: 20px;
  line-height: 1.6;
}

.method {
  margin: 30px 0;
}

.step-content {
  padding: 15px;
  background: #F5F7FA;
  border-radius: 8px;
  margin-top: 10px;
}

.step-content ol,
.step-content ul {
  margin: 10px 0;
  padding-left: 25px;
}

.step-content li {
  margin: 8px 0;
  line-height: 1.6;
}

kbd {
  display: inline-block;
  padding: 2px 6px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #303133;
  background-color: #EBEEF5;
  border: 1px solid #DCDFE6;
  border-radius: 3px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.2);
}

.video-section {
  margin: 30px 0;
  padding: 20px;
  background: #F5F7FA;
  border-radius: 8px;
  text-align: center;
}

.video-section h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
}

.troubleshooting {
  margin-top: 30px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.tips-list {
  list-style: none;
  padding: 0;
}

.tips-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  margin: 8px 0;
  background: #F5F7FA;
  border-radius: 6px;
}

.issue-card {
  cursor: pointer;
  transition: all 0.3s;
}

.issue-card:hover {
  transform: translateY(-2px);
}

.issue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.issue-header h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #303133;
}

.issue-desc {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.faq-answer {
  padding: 15px;
  line-height: 1.8;
}

.faq-answer ol,
.faq-answer ul {
  padding-left: 25px;
}

.faq-answer li {
  margin: 8px 0;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .tutorial-content h2,
  .tutorial-content h3 {
    color: #E4E7ED;
  }

  .step-content,
  .video-section,
  .tips-list li {
    background: #1F1F1F;
  }

  kbd {
    background-color: #2C2C2C;
    border-color: #3C3C3C;
    color: #E4E7ED;
  }
}
</style>
