<template>
  <div class="settings-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>⚙️ 系统设置</span>
          <el-button type="primary" @click="saveAllSettings" :loading="saving">
            <el-icon><Check /></el-icon>
            保存所有设置
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <!-- 🚀 服务控制 -->
        <el-tab-pane label="🚀 服务控制" name="service">
          <div class="settings-section">
            <h3>服务状态</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="当前状态">
                <el-tag :type="serviceStatus.running ? 'success' : 'danger'">
                  {{ serviceStatus.running ? '运行中' : '已停止' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="运行时长">
                {{ formatUptime(serviceStatus.uptime) }}
              </el-descriptions-item>
              <el-descriptions-item label="启动时间">
                {{ serviceStatus.startTime ? new Date(serviceStatus.startTime).toLocaleString() : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="进程PID">
                {{ serviceStatus.pid || '-' }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="control-buttons" style="margin-top: 20px;">
              <el-button 
                v-if="!serviceStatus.running"
                type="success" 
                size="large"
                @click="startService"
              >
                <el-icon><VideoPlay /></el-icon>
                启动服务
              </el-button>
              <el-button 
                v-else
                type="danger" 
                size="large"
                @click="stopService"
              >
                <el-icon><VideoPause /></el-icon>
                停止服务
              </el-button>
              <el-button size="large" @click="restartService">
                <el-icon><RefreshRight /></el-icon>
                重启服务
              </el-button>
            </div>

            <el-divider />

            <h3>自动启动</h3>
            <el-form label-width="150px">
              <el-form-item label="开机自启">
                <el-switch 
                  v-model="settings.autoLaunch" 
                  @change="handleAutoLaunchChange"
                />
                <span class="form-item-tip">启用后，系统启动时自动运行应用</span>
              </el-form-item>

              <el-form-item label="最小化到托盘">
                <el-switch v-model="settings.minimizeToTray" />
                <span class="form-item-tip">关闭窗口时最小化到系统托盘（而非退出）</span>
              </el-form-item>

              <el-form-item label="启动时最小化">
                <el-switch v-model="settings.startMinimized" />
                <span class="form-item-tip">启动时直接最小化到托盘</span>
              </el-form-item>
            </el-form>

            <el-divider />

            <h3>💬 历史消息同步</h3>
            <el-alert
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 20px;"
            >
              <template #title>
                启用后，程序启动时会同步最近N分钟的历史消息
              </template>
              默认仅转发新消息。启用此功能可以在重启后补发历史消息，但会增加启动时间。
            </el-alert>
            <el-form label-width="200px">
              <el-form-item label="启动时同步历史消息">
                <el-switch v-model="settings.syncHistoryOnStartup" />
                <span class="form-item-tip">启动时同步最近的历史消息到转发队列</span>
              </el-form-item>

              <el-form-item label="同步时间范围（分钟）" v-if="settings.syncHistoryOnStartup">
                <el-input-number 
                  v-model="settings.syncHistoryMinutes" 
                  :min="5" 
                  :max="120"
                  :step="5"
                />
                <span class="form-item-tip">同步最近多少分钟内的历史消息（5-120分钟）</span>
              </el-form-item>

              <el-form-item label="最多同步消息数" v-if="settings.syncHistoryOnStartup">
                <el-input-number 
                  v-model="settings.syncHistoryMaxMessages" 
                  :min="10" 
                  :max="500"
                  :step="10"
                />
                <span class="form-item-tip">每个频道最多同步多少条消息（10-500条）</span>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 🖼️ 图片处理 -->
        <el-tab-pane label="🖼️ 图片处理" name="image">
          <div class="settings-section">
            <h3>图片处理策略</h3>
            
            <!-- 策略选择 -->
            <el-form label-width="150px">
              <el-form-item label="图片策略">
                <el-radio-group v-model="settings.imageStrategy" size="large">
                  <el-radio value="smart">
                    <div class="radio-option">
                      <strong>● 智能模式（优先直传，失败用图床）← 推荐</strong>
                    </div>
                  </el-radio>
                  <el-radio value="direct">
                    <div class="radio-option">
                      <strong>○ 仅直传到目标平台</strong>
                    </div>
                  </el-radio>
                  <el-radio value="imgbed">
                    <div class="radio-option">
                      <strong>○ 仅使用内置图床</strong>
                    </div>
                  </el-radio>
                </el-radio-group>
              </el-form-item>
            </el-form>

            <!-- 策略对比表 -->
            <el-card shadow="hover" style="margin: 20px 0; background: #f9fafb;">
              <template #header>
                <div style="display: flex; align-items: center; gap: 10px;">
                  <el-icon color="#409EFF"><InfoFilled /></el-icon>
                  <strong>策略对比与推荐</strong>
                </div>
              </template>
              
              <el-table
                :data="strategyComparison"
                stripe
                border
                style="width: 100%"
                :header-cell-style="{ background: '#f5f7fa', fontWeight: 'bold' }"
              >
                <el-table-column prop="strategy" label="策略" width="150" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.isRecommended ? 'success' : 'info'" size="large">
                      {{ row.strategy }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="pros" label="✅ 优点" min-width="200">
                  <template #default="{ row }">
                    <ul style="margin: 5px 0; padding-left: 20px;">
                      <li v-for="(pro, index) in row.pros" :key="index" style="margin: 5px 0;">
                        {{ pro }}
                      </li>
                    </ul>
                  </template>
                </el-table-column>
                <el-table-column prop="cons" label="⚠️ 缺点" min-width="200">
                  <template #default="{ row }">
                    <ul style="margin: 5px 0; padding-left: 20px;">
                      <li v-for="(con, index) in row.cons" :key="index" style="margin: 5px 0;">
                        {{ con }}
                      </li>
                    </ul>
                  </template>
                </el-table-column>
                <el-table-column prop="recommend" label="💡 推荐场景" min-width="200">
                  <template #default="{ row }">
                    <div style="color: #606266;">{{ row.recommend }}</div>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>

            <el-divider />

            <h3>图床配置</h3>
            
            <el-form label-width="150px">
              <el-form-item label="存储路径">
                <el-input v-model="settings.imageStoragePath" readonly>
                  <template #append>
                    <el-button @click="openImageFolder">
                      <el-icon><FolderOpened /></el-icon>
                      打开
                    </el-button>
                    <el-button @click="changeImagePath">更改</el-button>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="最大占用空间">
                <el-input-number 
                  v-model="settings.imageMaxSizeGB" 
                  :min="1" 
                  :max="100"
                  :step="1"
                />
                <span style="margin-left: 10px;">GB</span>
                <div class="form-item-tip">
                  当前已用：{{ imageStats.usedSize }} / {{ settings.imageMaxSizeGB }}GB
                  ({{ imageStats.usedPercent }}%)
                </div>
                <el-progress 
                  :percentage="imageStats.usedPercent" 
                  :color="imageStats.usedPercent > 80 ? '#F56C6C' : '#67C23A'"
                />
              </el-form-item>

              <el-form-item label="自动清理">
                <el-input-number 
                  v-model="settings.imageCleanupDays" 
                  :min="1" 
                  :max="365"
                />
                <span style="margin-left: 10px;">天前的图片</span>
                <el-button 
                  style="margin-left: 20px;" 
                  type="warning"
                  @click="cleanupOldImages"
                >
                  <el-icon><Delete /></el-icon>
                  立即清理
                </el-button>
              </el-form-item>

              <el-form-item label="压缩质量">
                <el-slider 
                  v-model="settings.imageCompressionQuality" 
                  :min="60" 
                  :max="100"
                  :marks="{ 60: '最小', 80: '平衡', 100: '原始' }"
                />
                <div class="form-item-tip">
                  当前：{{ settings.imageCompressionQuality }}%
                  （质量越高，文件越大）
                </div>
              </el-form-item>

              <el-form-item label="最大尺寸">
                <el-input-number 
                  v-model="settings.imageMaxSizeMB" 
                  :min="1" 
                  :max="50"
                  :step="1"
                />
                <span style="margin-left: 10px;">MB</span>
                <div class="form-item-tip">超过此大小的图片将自动压缩</div>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 📝 日志设置 -->
        <el-tab-pane label="📝 日志设置" name="log">
          <div class="settings-section">
            <h3>日志配置</h3>
            <el-form label-width="150px">
              <el-form-item label="日志级别">
                <el-select v-model="settings.logLevel">
                  <el-option label="调试（DEBUG）" value="DEBUG">
                    <div>
                      <strong>调试</strong>
                      <p class="option-desc">记录所有信息，包括调试细节</p>
                    </div>
                  </el-option>
                  <el-option label="普通（INFO）" value="INFO">
                    <div>
                      <strong>普通</strong>
                      <p class="option-desc">记录正常运行信息（推荐）</p>
                    </div>
                  </el-option>
                  <el-option label="警告（WARNING）" value="WARNING">
                    <div>
                      <strong>警告</strong>
                      <p class="option-desc">仅记录警告和错误</p>
                    </div>
                  </el-option>
                  <el-option label="错误（ERROR）" value="ERROR">
                    <div>
                      <strong>错误</strong>
                      <p class="option-desc">仅记录错误信息</p>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="保留时长">
                <el-input-number 
                  v-model="settings.logRetentionDays" 
                  :min="1" 
                  :max="365"
                />
                <span style="margin-left: 10px;">天</span>
              </el-form-item>

              <el-form-item label="日志存储">
                <div>
                  <div>当前大小：{{ logStats.totalSize }}</div>
                  <div>文件数量：{{ logStats.fileCount }} 个</div>
                  <div style="margin-top: 10px;">
                    <el-button @click="openLogFolder">
                      <el-icon><FolderOpened /></el-icon>
                      打开日志文件夹
                    </el-button>
                    <el-button type="danger" @click="clearAllLogs">
                      <el-icon><Delete /></el-icon>
                      清空所有日志
                    </el-button>
                  </div>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 🔔 通知设置 -->
        <el-tab-pane label="🔔 通知设置" name="notification">
          <div class="settings-section">
            <h3>桌面通知</h3>
            <el-form label-width="180px">
              <el-form-item label="服务异常通知">
                <el-switch v-model="settings.notifyOnServiceError" />
                <span class="form-item-tip">服务异常时弹出桌面通知</span>
              </el-form-item>

              <el-form-item label="账号掉线通知">
                <el-switch v-model="settings.notifyOnAccountOffline" />
                <span class="form-item-tip">KOOK账号掉线时通知</span>
              </el-form-item>

              <el-form-item label="消息转发失败通知">
                <el-switch v-model="settings.notifyOnMessageFailed" />
                <span class="form-item-tip">消息转发失败时通知（可能较频繁）</span>
              </el-form-item>

              <el-form-item label="通知声音">
                <el-switch v-model="settings.notificationSound" />
              </el-form-item>
            </el-form>

            <el-divider />

            <h3>邮件告警（可选）</h3>
            <el-form label-width="180px">
              <el-form-item label="启用邮件告警">
                <el-switch v-model="settings.emailAlertEnabled" />
              </el-form-item>

              <template v-if="settings.emailAlertEnabled">
                <el-form-item label="SMTP服务器">
                  <el-input v-model="settings.smtpHost" placeholder="smtp.gmail.com" />
                </el-form-item>

                <el-form-item label="SMTP端口">
                  <el-input-number v-model="settings.smtpPort" :min="1" :max="65535" />
                </el-form-item>

                <el-form-item label="发件邮箱">
                  <el-input v-model="settings.smtpFromEmail" placeholder="your@email.com" />
                </el-form-item>

                <el-form-item label="邮箱密码">
                  <el-input 
                    v-model="settings.smtpPassword" 
                    type="password" 
                    show-password
                    placeholder="邮箱密码或应用专用密码"
                  />
                </el-form-item>

                <el-form-item label="收件邮箱">
                  <el-input v-model="settings.smtpToEmail" placeholder="notify@email.com" />
                </el-form-item>

                <el-form-item label="使用TLS">
                  <el-switch v-model="settings.smtpUseTLS" />
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" @click="testEmailConfig">
                    <el-icon><Promotion /></el-icon>
                    发送测试邮件
                  </el-button>
                </el-form-item>
              </template>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 🔒 安全设置 -->
        <el-tab-pane label="🔒 安全设置" name="security">
          <div class="settings-section">
            <h3>访问控制</h3>
            <el-form label-width="150px">
              <el-form-item label="启动时需要密码">
                <el-switch v-model="settings.requirePassword" />
                <span class="form-item-tip">启用后，每次启动应用需要输入主密码</span>
              </el-form-item>

              <el-form-item v-if="settings.requirePassword" label="当前密码">
                <div>
                  <div>密码状态：<el-tag type="success">已设置</el-tag></div>
                  <el-button style="margin-top: 10px;" @click="showChangePasswordDialog = true">
                    更改密码
                  </el-button>
                </div>
              </el-form-item>

              <el-form-item v-else>
                <el-button type="primary" @click="showSetPasswordDialog = true">
                  设置主密码
                </el-button>
              </el-form-item>
            </el-form>

            <el-divider />

            <h3>数据加密</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="敏感信息加密">
                <el-tag type="success">✓ 已启用</el-tag>
                <div class="desc-tip">所有Token、密码等敏感信息均采用AES-256加密存储</div>
              </el-descriptions-item>
              <el-descriptions-item label="加密密钥">
                <div>
                  <div>基于设备唯一ID生成</div>
                  <el-button 
                    type="danger" 
                    size="small" 
                    style="margin-top: 10px;"
                    @click="regenerateEncryptionKey"
                  >
                    重新生成密钥
                  </el-button>
                  <div class="desc-warning">
                    ⚠️ 重新生成密钥后，需要重新输入所有密码和Token
                  </div>
                </div>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-tab-pane>

        <!-- 💾 备份与恢复 -->
        <el-tab-pane label="💾 备份与恢复" name="backup">
          <div class="settings-section">
            <h3>配置备份</h3>
            
            <el-descriptions :column="2" border style="margin-bottom: 20px;">
              <el-descriptions-item label="最后备份时间">
                {{ backupInfo.lastBackupTime || '从未备份' }}
              </el-descriptions-item>
              <el-descriptions-item label="备份文件大小">
                {{ backupInfo.lastBackupSize || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="自动备份">
                <el-tag :type="settings.autoBackup ? 'success' : 'info'">
                  {{ settings.autoBackup ? '已启用' : '未启用' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="备份文件数">
                {{ backupInfo.totalBackups || 0 }} 个
              </el-descriptions-item>
            </el-descriptions>

            <div class="backup-actions">
              <el-button type="primary" size="large" @click="backupNow">
                <el-icon><Download /></el-icon>
                立即备份配置
              </el-button>
              <el-button type="success" size="large" @click="showRestoreDialog = true">
                <el-icon><Upload /></el-icon>
                恢复配置
              </el-button>
              <el-button size="large" @click="openBackupFolder">
                <el-icon><FolderOpened /></el-icon>
                打开备份文件夹
              </el-button>
            </div>

            <el-divider />

            <h3>自动备份设置</h3>
            <el-form label-width="150px">
              <el-form-item label="启用自动备份">
                <el-switch v-model="settings.autoBackup" />
                <span class="form-item-tip">每天自动备份一次配置</span>
              </el-form-item>

              <el-form-item v-if="settings.autoBackup" label="备份时间">
                <el-time-picker 
                  v-model="settings.autoBackupTime" 
                  format="HH:mm"
                  placeholder="选择备份时间"
                />
              </el-form-item>

              <el-form-item label="保留备份数">
                <el-input-number 
                  v-model="settings.backupRetentionCount" 
                  :min="1" 
                  :max="30"
                />
                <span style="margin-left: 10px;">个</span>
                <div class="form-item-tip">超过此数量的旧备份将被自动删除</div>
              </el-form-item>
            </el-form>

            <el-divider />

            <h3>备份内容</h3>
            <el-checkbox-group v-model="settings.backupItems">
              <el-checkbox label="accounts">账号配置</el-checkbox>
              <el-checkbox label="bots">Bot配置</el-checkbox>
              <el-checkbox label="mappings">频道映射</el-checkbox>
              <el-checkbox label="filters">过滤规则</el-checkbox>
              <el-checkbox label="settings">系统设置</el-checkbox>
            </el-checkbox-group>
          </div>
        </el-tab-pane>

        <!-- 🌍 其他设置 -->
        <el-tab-pane label="🌍 其他设置" name="other">
          <div class="settings-section">
            <h3>界面设置</h3>
            <el-form label-width="150px">
              <el-form-item label="语言">
                <el-select v-model="settings.language">
                  <el-option label="简体中文" value="zh-CN" />
                  <el-option label="English" value="en-US" />
                </el-select>
              </el-form-item>

              <el-form-item label="主题">
                <el-radio-group v-model="settings.theme">
                  <el-radio label="light">浅色</el-radio>
                  <el-radio label="dark">深色</el-radio>
                  <el-radio label="auto">跟随系统</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-form>

            <el-divider />

            <h3>更新设置</h3>
            <el-form label-width="150px">
              <el-form-item label="自动检查更新">
                <el-switch v-model="settings.autoCheckUpdate" />
              </el-form-item>

              <el-form-item label="当前版本">
                <div>
                  <el-tag type="info">v6.1.0</el-tag>
                  <el-button style="margin-left: 10px;" @click="checkUpdate">
                    检查更新
                  </el-button>
                </div>
              </el-form-item>
            </el-form>

            <el-divider />

            <h3>高级选项</h3>
            <el-form label-width="150px">
              <el-form-item label="开发者模式">
                <el-switch v-model="settings.developerMode" />
                <div class="form-item-tip">启用后可查看更详细的调试信息</div>
              </el-form-item>

              <el-form-item label="性能监控">
                <el-switch v-model="settings.performanceMonitor" />
                <div class="form-item-tip">显示CPU和内存使用情况</div>
              </el-form-item>
            </el-form>

            <el-divider />

            <h3>数据管理</h3>
            <div class="danger-zone">
              <el-alert
                title="危险操作"
                type="error"
                :closable="false"
              >
                <div>以下操作不可恢复，请谨慎操作！</div>
              </el-alert>

              <div style="margin-top: 20px;">
                <el-button type="danger" @click="clearAllData">
                  <el-icon><Delete /></el-icon>
                  清空所有数据
                </el-button>
                <el-button type="danger" plain @click="resetSettings">
                  <el-icon><RefreshLeft /></el-icon>
                  恢复默认设置
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 更改密码对话框 -->
    <el-dialog v-model="showChangePasswordDialog" title="更改主密码" width="500px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChangePasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="changePassword">确定</el-button>
      </template>
    </el-dialog>

    <!-- 恢复配置对话框 -->
    <el-dialog v-model="showRestoreDialog" title="恢复配置" width="600px">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleBackupFileSelect"
        accept=".json,.zip"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将备份文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .json 和 .zip 格式的备份文件
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showRestoreDialog = false">取消</el-button>
        <el-button type="primary" @click="restoreFromBackup">恢复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Check,
  VideoPlay,
  VideoPause,
  RefreshRight,
  FolderOpened,
  Delete,
  Promotion,
  Download,
  Upload,
  RefreshLeft,
  UploadFilled
} from '@element-plus/icons-vue'
import api from '@/api'

const activeTab = ref('service')
const saving = ref(false)

// ✅ P0-4优化: 图片策略对比数据
const strategyComparison = ref([
  {
    strategy: '智能模式',
    isRecommended: true,
    pros: [
      '最佳平衡：结合直传和图床的优点',
      '自动降级：直传失败时自动使用图床',
      '稳定性高：双重保障确保消息不丢失',
      '无需维护：用户无感知自动切换'
    ],
    cons: [
      '无明显缺点'
    ],
    recommend: '所有用户（强烈推荐）'
  },
  {
    strategy: '仅直传',
    isRecommended: false,
    pros: [
      '速度最快：直接上传到目标平台',
      '无需图床：不占用本地磁盘空间',
      '链接永久：图片随平台账号永久保存'
    ],
    cons: [
      '稳定性差：上传失败则无法转发',
      '平台限制：受目标平台上传限制影响',
      '大图失败：超大图片可能上传失败'
    ],
    recommend: '网络稳定、目标平台可靠、对磁盘空间敏感的用户'
  },
  {
    strategy: '仅图床',
    isRecommended: false,
    pros: [
      '稳定性极高：图片先保存本地再转发',
      '可追溯：所有图片本地存档',
      '多次转发：同一图片可多次使用',
      '自主可控：不依赖目标平台'
    ],
    cons: [
      '占用磁盘：需要较大本地存储空间',
      '维护成本：需定期清理旧图片',
      '链接时效：Token过期后链接失效'
    ],
    recommend: '对稳定性要求极高、磁盘空间充足的用户'
  }
])

// 服务状态
const serviceStatus = reactive({
  running: false,
  uptime: 0,
  startTime: null,
  pid: null
})

// 设置数据
const settings = reactive({
  // 服务控制
  autoLaunch: false,
  minimizeToTray: true,
  startMinimized: false,
  
  // ✅ 新增: 历史消息同步
  syncHistoryOnStartup: false,
  syncHistoryMinutes: 30,
  syncHistoryMaxMessages: 100,
  
  // 图片处理
  imageStrategy: 'smart',
  imageStoragePath: '',
  imageMaxSizeGB: 10,
  imageCleanupDays: 7,
  imageCompressionQuality: 85,
  imageMaxSizeMB: 10,
  
  // 日志
  logLevel: 'INFO',
  logRetentionDays: 3,
  
  // 通知
  notifyOnServiceError: true,
  notifyOnAccountOffline: true,
  notifyOnMessageFailed: false,
  notificationSound: true,
  
  // 邮件
  emailAlertEnabled: false,
  smtpHost: 'smtp.gmail.com',
  smtpPort: 587,
  smtpFromEmail: '',
  smtpPassword: '',
  smtpToEmail: '',
  smtpUseTLS: true,
  
  // 安全
  requirePassword: false,
  
  // 备份
  autoBackup: true,
  autoBackupTime: new Date(),
  backupRetentionCount: 10,
  backupItems: ['accounts', 'bots', 'mappings', 'filters', 'settings'],
  
  // 其他
  language: 'zh-CN',
  theme: 'light',
  autoCheckUpdate: true,
  developerMode: false,
  performanceMonitor: false,
})

// 统计信息
const imageStats = reactive({
  usedSize: '0 MB',
  usedPercent: 0
})

const logStats = reactive({
  totalSize: '0 MB',
  fileCount: 0
})

const backupInfo = reactive({
  lastBackupTime: null,
  lastBackupSize: null,
  totalBackups: 0
})

// 对话框
const showChangePasswordDialog = ref(false)
const showSetPasswordDialog = ref(false)
const showRestoreDialog = ref(false)

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

let selectedBackupFile = null

/**
 * 加载设置
 */
const loadSettings = async () => {
  try {
    const response = await api.get('/api/settings')
    Object.assign(settings, response.data)
    
    // 加载服务状态
    const statusRes = await api.get('/api/system/status')
    Object.assign(serviceStatus, statusRes.data)
    
    // 加载统计信息
    loadStats()
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败')
  }
}

/**
 * 加载统计信息
 */
const loadStats = async () => {
  try {
    const [imageRes, logRes, backupRes] = await Promise.all([
      api.get('/api/settings/image-stats'),
      api.get('/api/settings/log-stats'),
      api.get('/api/settings/backup-info')
    ])
    
    Object.assign(imageStats, imageRes.data)
    Object.assign(logStats, logRes.data)
    Object.assign(backupInfo, backupRes.data)
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

/**
 * 保存所有设置
 */
const saveAllSettings = async () => {
  try {
    saving.value = true
    await api.post('/api/settings', settings)
    ElMessage.success('设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

/**
 * 格式化运行时长
 */
const formatUptime = (seconds) => {
  if (!seconds) return '0秒'
  
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  const parts = []
  if (days > 0) parts.push(`${days}天`)
  if (hours > 0) parts.push(`${hours}小时`)
  if (minutes > 0) parts.push(`${minutes}分`)
  if (secs > 0 || parts.length === 0) parts.push(`${secs}秒`)
  
  return parts.join(' ')
}

/**
 * 启动服务
 */
const startService = async () => {
  try {
    await api.post('/api/system/start')
    ElMessage.success('服务已启动')
    await loadSettings()
  } catch (error) {
    ElMessage.error('启动失败: ' + error.message)
  }
}

/**
 * 停止服务
 */
const stopService = async () => {
  try {
    await ElMessageBox.confirm('确定要停止服务吗？', '确认')
    await api.post('/api/system/stop')
    ElMessage.success('服务已停止')
    await loadSettings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停止失败: ' + error.message)
    }
  }
}

/**
 * 重启服务
 */
const restartService = async () => {
  try {
    await ElMessageBox.confirm('确定要重启服务吗？', '确认')
    await api.post('/api/system/restart')
    ElMessage.success('服务已重启')
    await loadSettings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重启失败: ' + error.message)
    }
  }
}

/**
 * 自动启动设置
 */
const handleAutoLaunchChange = async (enabled) => {
  try {
    if (window.electronAPI) {
      if (enabled) {
        await window.electronAPI.autoLaunch.enable()
      } else {
        await window.electronAPI.autoLaunch.disable()
      }
      ElMessage.success(enabled ? '已启用开机自启' : '已禁用开机自启')
    } else {
      ElMessage.warning('仅Electron环境支持此功能')
    }
  } catch (error) {
    ElMessage.error('设置失败: ' + error.message)
  }
}

/**
 * 打开图片文件夹
 */
const openImageFolder = async () => {
  if (window.electronAPI) {
    await window.electronAPI.system.openPath(settings.imageStoragePath)
  }
}

/**
 * 更改图片路径
 */
const changeImagePath = async () => {
  if (window.electronAPI) {
    const result = await window.electronAPI.dialog.openFile({
      properties: ['openDirectory']
    })
    if (!result.canceled && result.filePaths.length > 0) {
      settings.imageStoragePath = result.filePaths[0]
      ElMessage.success('路径已更改')
    }
  }
}

/**
 * 清理旧图片
 */
const cleanupOldImages = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清理 ${settings.imageCleanupDays} 天前的图片吗？`,
      '确认清理'
    )
    const response = await api.post('/api/settings/cleanup-images', {
      days: settings.imageCleanupDays
    })
    ElMessage.success(`已清理 ${response.data.deletedCount} 个文件，释放 ${response.data.freedSpace}`)
    await loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清理失败: ' + error.message)
    }
  }
}

/**
 * 打开日志文件夹
 */
const openLogFolder = async () => {
  if (window.electronAPI) {
    await window.electronAPI.system.openPath(await window.electronAPI.app.getPath('logs'))
  }
}

/**
 * 清空所有日志
 */
const clearAllLogs = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有日志吗？此操作不可恢复！', '危险操作', {
      type: 'error'
    })
    await api.post('/api/settings/clear-logs')
    ElMessage.success('日志已清空')
    await loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败: ' + error.message)
    }
  }
}

/**
 * 测试邮件配置
 */
const testEmailConfig = async () => {
  try {
    await api.post('/api/settings/test-email', {
      smtpHost: settings.smtpHost,
      smtpPort: settings.smtpPort,
      smtpFromEmail: settings.smtpFromEmail,
      smtpPassword: settings.smtpPassword,
      smtpToEmail: settings.smtpToEmail,
      smtpUseTLS: settings.smtpUseTLS
    })
    ElMessage.success('测试邮件已发送，请检查收件箱')
  } catch (error) {
    ElMessage.error('发送失败: ' + error.message)
  }
}

/**
 * 立即备份
 */
const backupNow = async () => {
  try {
    const response = await api.post('/api/backup/create', {
      items: settings.backupItems
    })
    ElMessage.success('备份成功：' + response.data.filename)
    await loadStats()
  } catch (error) {
    ElMessage.error('备份失败: ' + error.message)
  }
}

/**
 * 打开备份文件夹
 */
const openBackupFolder = async () => {
  if (window.electronAPI) {
    const backupPath = await window.electronAPI.app.getPath('userData') + '/backups'
    await window.electronAPI.system.openPath(backupPath)
  }
}

/**
 * 选择备份文件
 */
const handleBackupFileSelect = (file) => {
  selectedBackupFile = file
}

/**
 * 从备份恢复
 */
const restoreFromBackup = async () => {
  if (!selectedBackupFile) {
    ElMessage.warning('请先选择备份文件')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '恢复配置将覆盖当前所有设置，确定继续吗？',
      '确认恢复',
      { type: 'warning' }
    )
    
    const formData = new FormData()
    formData.append('file', selectedBackupFile.raw)
    
    await api.post('/api/backup/restore', formData)
    ElMessage.success('恢复成功，即将重启应用...')
    
    setTimeout(() => {
      if (window.electronAPI) {
        window.electronAPI.app.relaunch()
      } else {
        window.location.reload()
      }
    }, 2000)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('恢复失败: ' + error.message)
    }
  }
}

/**
 * 更改密码
 */
const changePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword) {
    ElMessage.warning('请填写所有字段')
    return
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  
  try {
    await api.post('/api/auth/change-password', {
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    })
    ElMessage.success('密码已更改')
    showChangePasswordDialog.value = false
    Object.assign(passwordForm, { oldPassword: '', newPassword: '', confirmPassword: '' })
  } catch (error) {
    ElMessage.error('更改失败: ' + error.message)
  }
}

/**
 * 重新生成加密密钥
 */
const regenerateEncryptionKey = async () => {
  try {
    await ElMessageBox.confirm(
      '重新生成加密密钥后，所有已加密的数据将无法解密，需要重新输入所有敏感信息。确定继续吗？',
      '危险操作',
      { type: 'error' }
    )
    
    await api.post('/api/settings/regenerate-key')
    ElMessage.success('密钥已重新生成')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败: ' + error.message)
    }
  }
}

/**
 * 检查更新
 */
const checkUpdate = async () => {
  try {
    const response = await api.get('/api/updates/check')
    if (response.data.hasUpdate) {
      ElMessageBox.confirm(
        `发现新版本 ${response.data.latestVersion}，是否立即下载？`,
        '发现更新',
        { type: 'success' }
      ).then(() => {
        if (window.electronAPI) {
          window.electronAPI.app.openExternal(response.data.downloadUrl)
        }
      })
    } else {
      ElMessage.info('当前已是最新版本')
    }
  } catch (error) {
    ElMessage.error('检查更新失败: ' + error.message)
  }
}

/**
 * 清空所有数据
 */
const clearAllData = async () => {
  try {
    await ElMessageBox.prompt(
      '此操作将删除所有数据（账号、Bot、映射、日志等），请输入"确认删除"以继续',
      '危险操作',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'error',
        inputPattern: /^确认删除$/,
        inputErrorMessage: '请输入"确认删除"'
      }
    )
    
    await api.post('/api/settings/clear-all-data')
    ElMessage.success('数据已清空，即将重启应用...')
    
    setTimeout(() => {
      if (window.electronAPI) {
        window.electronAPI.app.relaunch()
      } else {
        window.location.reload()
      }
    }, 2000)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败: ' + error.message)
    }
  }
}

/**
 * 恢复默认设置
 */
const resetSettings = async () => {
  try {
    await ElMessageBox.confirm('确定要恢复所有默认设置吗？', '确认', {
      type: 'warning'
    })
    
    await api.post('/api/settings/reset')
    ElMessage.success('设置已重置')
    await loadSettings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置失败: ' + error.message)
    }
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-section {
  padding: 20px;
}

.settings-section h3 {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

.control-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.form-item-tip {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-top: 5px;
}

.radio-desc {
  font-size: 13px;
  color: #909399;
  margin: 5px 0 0 0;
}

.option-desc {
  font-size: 12px;
  color: #909399;
  margin: 3px 0 0 0;
}

.desc-tip {
  font-size: 13px;
  color: #909399;
  margin-top: 5px;
}

.desc-warning {
  font-size: 13px;
  color: #E6A23C;
  margin-top: 5px;
}

.backup-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.danger-zone {
  padding: 20px;
  border: 2px solid #F56C6C;
  border-radius: 8px;
}

/* 暗色主题 */
.dark .settings-section h3 {
  color: #E5EAF3;
}
</style>
