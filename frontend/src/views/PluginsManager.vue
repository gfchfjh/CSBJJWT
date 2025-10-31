<template>
  <div class="plugins-manager">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔌 插件管理</span>
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            安装插件
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 已安装 -->
        <el-tab-pane label="已安装" name="installed">
          <el-table :data="installedPlugins" v-loading="loading">
            <el-table-column prop="name" label="插件名称" width="200" />
            <el-table-column prop="version" label="版本" width="100" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="author" label="作者" width="150" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-switch v-model="row.enabled" @change="togglePlugin(row)" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="configPlugin(row)">配置</el-button>
                <el-button type="danger" size="small" @click="uninstallPlugin(row)">卸载</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 插件市场 -->
        <el-tab-pane label="插件市场" name="market">
          <el-row :gutter="20">
            <el-col :span="6" v-for="plugin in marketPlugins" :key="plugin.id">
              <el-card class="plugin-card" shadow="hover">
                <div class="plugin-icon">{{ plugin.icon }}</div>
                <h3>{{ plugin.name }}</h3>
                <p class="plugin-desc">{{ plugin.description }}</p>
                <div class="plugin-meta">
                  <el-tag size="small">{{ plugin.category }}</el-tag>
                  <span>⭐ {{ plugin.rating }}</span>
                </div>
                <el-button type="primary" size="small" style="width: 100%;">安装</el-button>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="安装插件" width="500px">
      <el-upload
        drag
        :action="`${API_BASE}/api/plugins/upload`"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        accept=".zip"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽插件文件到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只支持.zip格式的插件包
          </div>
        </template>
      </el-upload>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = 'http://localhost:9527'

const activeTab = ref('installed')
const loading = ref(false)
const installedPlugins = ref([])
const marketPlugins = ref([])
const showUploadDialog = ref(false)

const loadPlugins = async () => {
  loading.value = true
  try {
    const [installedRes, marketRes] = await Promise.all([
      axios.get(`${API_BASE}/api/plugins/`),
      axios.get(`${API_BASE}/api/plugins/market`)
    ])
    
    installedPlugins.value = installedRes.data.data.map(p => ({
      ...p,
      enabled: Boolean(p.enabled)
    }))
    marketPlugins.value = marketRes.data.data
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const togglePlugin = async (plugin) => {
  try {
    await axios.post(`${API_BASE}/api/plugins/${plugin.id}/toggle`)
    ElMessage.success(plugin.enabled ? '插件已启用' : '插件已禁用')
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
    plugin.enabled = !plugin.enabled
  }
}

const uninstallPlugin = async (plugin) => {
  try {
    await ElMessageBox.confirm(`确定要卸载插件 ${plugin.name} 吗？`, '确认', {
      type: 'warning'
    })
    
    await axios.delete(`${API_BASE}/api/plugins/${plugin.id}`)
    ElMessage.success('插件已卸载')
    loadPlugins()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('卸载失败: ' + error.message)
    }
  }
}

const configPlugin = (plugin) => {
  ElMessage.info('插件配置功能开发中...')
}

const handleUploadSuccess = (response) => {
  if (response.success) {
    ElMessage.success('插件安装成功')
    showUploadDialog.value = false
    loadPlugins()
  }
}

const handleUploadError = (error) => {
  ElMessage.error('安装失败: ' + error.message)
}

onMounted(() => {
  loadPlugins()
})
</script>

<style scoped>
.plugins-manager {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plugin-card {
  margin-bottom: 20px;
  text-align: center;
}

.plugin-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.plugin-desc {
  color: #666;
  font-size: 14px;
  margin: 10px 0;
  min-height: 40px;
}

.plugin-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
}
</style>
