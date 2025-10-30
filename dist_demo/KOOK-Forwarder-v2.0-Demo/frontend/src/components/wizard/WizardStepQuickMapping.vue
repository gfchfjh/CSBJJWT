<template>
  <div class="wizard-quick-mapping">
    <el-alert type="info" :closable="false" class="step-info">
      <template #title>
        <div class="alert-title">
          <el-icon><Connection /></el-icon>
          <span>快速频道映射</span>
        </div>
      </template>
      智能推荐映射关系，也可手动调整。设置完成后将开始自动转发消息。
    </el-alert>

    <!-- 智能映射按钮 -->
    <el-card shadow="hover" class="smart-mapping-card">
      <div class="smart-mapping-header">
        <div>
          <h3>🤖 智能推荐映射</h3>
          <p>根据频道名称相似度自动推荐映射关系</p>
        </div>
        <el-button 
          type="primary" 
          size="large"
          @click="runSmartMapping"
          :loading="smartMapping"
        >
          <el-icon><MagicStick /></el-icon>
          一键智能映射
        </el-button>
      </div>
    </el-card>

    <!-- 映射列表 -->
    <el-card v-if="mappings.length > 0" shadow="hover" class="mappings-card">
      <template #header>
        <div class="card-header">
          <span>频道映射列表</span>
          <el-tag type="success">{{ mappings.length }}个映射</el-tag>
        </div>
      </template>

      <el-table :data="mappings" style="width: 100%">
        <el-table-column label="KOOK频道" min-width="200">
          <template #default="{ row }">
            <div class="channel-info">
              <el-tag type="primary" size="small">{{ row.kook_server_name }}</el-tag>
              <span># {{ row.kook_channel_name }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="" width="60" align="center">
          <template #default>
            <el-icon color="#409EFF" size="20"><Right /></el-icon>
          </template>
        </el-table-column>

        <el-table-column label="目标频道" min-width="200">
          <template #default="{ row }">
            <div class="channel-info">
              <el-tag 
                :type="getPlatformTagType(row.target_platform)" 
                size="small"
              >
                {{ getPlatformName(row.target_platform) }}
              </el-tag>
              <span>{{ row.target_channel_name }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="置信度" width="120">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.confidence || 80" 
              :color="getConfidenceColor(row.confidence)"
            />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row, $index }">
            <el-button-group>
              <el-button size="small" @click="editMapping($index)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="deleteMapping($index)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <div class="add-mapping-btn">
        <el-button @click="showAddMappingDialog">
          <el-icon><Plus /></el-icon>
          手动添加映射
        </el-button>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-empty 
      v-else
      description="还没有配置任何映射，点击上方按钮开始智能映射"
      :image-size="200"
    />

    <!-- 添加/编辑映射对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingIndex === null ? '添加映射' : '编辑映射'"
      width="600px"
    >
      <el-form :model="currentMapping" label-width="120px">
        <el-form-item label="KOOK频道" required>
          <el-cascader
            v-model="currentMapping.kook_channel"
            :options="kookChannelOptions"
            placeholder="选择服务器和频道"
            style="width: 100%"
            :props="{ expandTrigger: 'hover' }"
          />
        </el-form-item>

        <el-form-item label="目标平台" required>
          <el-select v-model="currentMapping.target_platform" placeholder="选择平台">
            <el-option label="Discord" value="discord" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="飞书" value="feishu" />
          </el-select>
        </el-form-item>

        <el-form-item label="目标Bot" required>
          <el-select v-model="currentMapping.target_bot_id" placeholder="选择Bot">
            <el-option 
              v-for="bot in getBotsForPlatform(currentMapping.target_platform)"
              :key="bot.id"
              :label="bot.name"
              :value="bot.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="目标频道" required>
          <el-input 
            v-model="currentMapping.target_channel_id" 
            placeholder="目标频道ID或名称"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMappingDialog">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导航按钮 -->
    <div class="wizard-actions">
      <el-button @click="$emit('prev')">
        <el-icon><ArrowLeft /></el-icon>
        上一步
      </el-button>
      <el-button 
        type="success" 
        size="large"
        @click="completeWizard"
        :disabled="mappings.length === 0"
      >
        <el-icon><CircleCheckFilled /></el-icon>
        完成配置，开始使用
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Connection,
  MagicStick,
  Right,
  Edit,
  Delete,
  Plus,
  CircleCheckFilled,
  ArrowLeft
} from '@element-plus/icons-vue';
import api from '@/api';

const emit = defineEmits(['next', 'prev', 'complete']);

// 数据
const smartMapping = ref(false);
const mappings = ref([]);
const dialogVisible = ref(false);
const editingIndex = ref(null);
const kookChannelOptions = ref([]);
const bots = ref([]);

const currentMapping = ref({
  kook_channel: null,
  target_platform: '',
  target_bot_id: null,
  target_channel_id: ''
});

// 加载数据
onMounted(async () => {
  await loadKookChannels();
  await loadBots();
});

// 加载KOOK频道
const loadKookChannels = async () => {
  try {
    const response = await api.get('/api/accounts/servers');
    
    kookChannelOptions.value = response.servers.map(server => ({
      value: server.id,
      label: server.name,
      children: server.channels.map(channel => ({
        value: channel.id,
        label: channel.name
      }))
    }));
  } catch (error) {
    ElMessage.error('加载KOOK频道失败');
  }
};

// 加载Bot列表
const loadBots = async () => {
  try {
    const response = await api.get('/api/bots');
    bots.value = response.bots;
  } catch (error) {
    ElMessage.error('加载Bot列表失败');
  }
};

// 智能映射
const runSmartMapping = async () => {
  smartMapping.value = true;
  
  try {
    const response = await api.post('/api/smart-mapping/auto');
    
    if (response.mappings && response.mappings.length > 0) {
      mappings.value = response.mappings;
      ElMessage.success(`智能推荐了${response.mappings.length}个映射关系`);
    } else {
      ElMessage.warning('未找到匹配的映射关系，请手动添加');
    }
  } catch (error) {
    ElMessage.error('智能映射失败，请手动添加');
  } finally {
    smartMapping.value = false;
  }
};

// 获取平台名称
const getPlatformName = (platform) => {
  const names = {
    discord: 'Discord',
    telegram: 'Telegram',
    feishu: '飞书'
  };
  return names[platform] || platform;
};

// 获取平台标签类型
const getPlatformTagType = (platform) => {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  };
  return types[platform] || '';
};

// 获取置信度颜色
const getConfidenceColor = (confidence) => {
  if (confidence >= 80) return '#67C23A';
  if (confidence >= 60) return '#E6A23C';
  return '#F56C6C';
};

// 获取指定平台的Bot
const getBotsForPlatform = (platform) => {
  return bots.value.filter(bot => bot.platform === platform);
};

// 显示添加映射对话框
const showAddMappingDialog = () => {
  editingIndex.value = null;
  currentMapping.value = {
    kook_channel: null,
    target_platform: '',
    target_bot_id: null,
    target_channel_id: ''
  };
  dialogVisible.value = true;
};

// 编辑映射
const editMapping = (index) => {
  editingIndex.value = index;
  currentMapping.value = { ...mappings.value[index] };
  dialogVisible.value = true;
};

// 删除映射
const deleteMapping = (index) => {
  mappings.value.splice(index, 1);
  ElMessage.success('已删除映射');
};

// 保存映射对话框
const saveMappingDialog = () => {
  if (editingIndex.value === null) {
    mappings.value.push({ ...currentMapping.value, confidence: 100 });
  } else {
    mappings.value[editingIndex.value] = { ...currentMapping.value };
  }
  
  dialogVisible.value = false;
  ElMessage.success('映射已保存');
};

// 完成向导
const completeWizard = async () => {
  try {
    // 保存所有映射
    await api.post('/api/mappings/batch', { mappings: mappings.value });
    
    ElMessage.success('配置完成！开始享受自动转发服务吧 🎉');
    emit('complete');
  } catch (error) {
    ElMessage.error('保存映射失败，请重试');
  }
};
</script>

<style scoped>
.wizard-quick-mapping {
  max-width: 1000px;
  margin: 0 auto;
}

.step-info {
  margin-bottom: 24px;
}

.alert-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.smart-mapping-card {
  margin-bottom: 24px;
}

.smart-mapping-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.smart-mapping-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.smart-mapping-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.mappings-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-mapping-btn {
  margin-top: 16px;
  text-align: center;
}

.wizard-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #EBEEF5;
}
</style>
