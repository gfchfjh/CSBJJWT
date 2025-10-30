<template>
  <div class="mapping-visual">
    <div class="mapping-header">
      <h2>📊 可视化频道映射编辑器</h2>
      <div class="header-actions">
        <el-button @click="loadMappings" :icon="Refresh">刷新</el-button>
        <el-button type="primary" @click="saveMappings" :loading="isSaving">
          <el-icon><Check /></el-icon> 保存映射
        </el-button>
      </div>
    </div>

    <el-alert
      title="使用说明"
      type="info"
      :closable="false"
      style="margin-bottom: 20px;"
    >
      <template #default>
        点击KOOK频道，然后点击目标平台，即可创建映射关系。点击连线可以删除映射。
      </template>
    </el-alert>

    <!-- 主映射区域 -->
    <div class="mapping-canvas" ref="canvasRef">
      <!-- 左侧：KOOK频道 -->
      <div class="source-panel">
        <div class="panel-header">
          <h3>🏠 KOOK频道（源）</h3>
          <el-input
            v-model="sourceSearch"
            placeholder="搜索频道..."
            clearable
            size="small"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="channel-list">
          <div
            v-for="server in filteredSourceServers"
            :key="server.id"
            class="server-group"
          >
            <div class="server-title">
              <el-icon><OfficeBuilding /></el-icon>
              {{ server.name }}
            </div>
            <div
              v-for="channel in server.channels"
              :key="channel.id"
              class="channel-node"
              :class="{ selected: selectedSource?.id === channel.id }"
              @click="selectSource(channel, server)"
              :data-channel-id="channel.id"
            >
              <el-icon><ChatDotRound /></el-icon>
              <span>{{ channel.name }}</span>
              <el-tag v-if="getMappingCount(channel.id)" size="small" type="success">
                {{ getMappingCount(channel.id) }} 个映射
              </el-tag>
            </div>
          </div>

          <el-empty v-if="filteredSourceServers.length === 0" description="暂无频道" />
        </div>
      </div>

      <!-- 中间：连线区域 -->
      <svg class="connection-layer" ref="svgRef">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 10 3, 0 6" fill="#409EFF" />
          </marker>
        </defs>
        <g v-for="(mapping, index) in mappings" :key="`mapping-${index}`">
          <path
            :d="calculatePath(mapping)"
            class="connection-line"
            :class="{ highlighted: isHighlighted(mapping) }"
            stroke="#409EFF"
            stroke-width="2"
            fill="none"
            marker-end="url(#arrowhead)"
            @click="removeMappingLine(mapping, index)"
          />
          <!-- 删除按钮 -->
          <circle
            v-if="calculateMidpoint(mapping)"
            :cx="calculateMidpoint(mapping).x"
            :cy="calculateMidpoint(mapping).y"
            r="12"
            fill="#F56C6C"
            class="delete-button"
            @click="removeMappingLine(mapping, index)"
          />
          <text
            v-if="calculateMidpoint(mapping)"
            :x="calculateMidpoint(mapping).x"
            :y="calculateMidpoint(mapping).y + 4"
            text-anchor="middle"
            fill="white"
            font-size="14"
            font-weight="bold"
            class="delete-icon"
            @click="removeMappingLine(mapping, index)"
          >
            ×
          </text>
        </g>
      </svg>

      <!-- 右侧：目标平台 -->
      <div class="target-panel">
        <div class="panel-header">
          <h3>🎯 目标平台（接收）</h3>
          <el-input
            v-model="targetSearch"
            placeholder="搜索Bot..."
            clearable
            size="small"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="bot-list">
          <div
            v-for="bot in filteredTargetBots"
            :key="bot.id"
            class="bot-node"
            :class="{
              selected: selectedTarget?.id === bot.id,
              'discord': bot.platform === 'discord',
              'telegram': bot.platform === 'telegram',
              'feishu': bot.platform === 'feishu'
            }"
            @click="selectTarget(bot)"
            :data-bot-id="bot.id"
          >
            <div class="bot-icon">
              <el-icon v-if="bot.platform === 'discord'"><Connection /></el-icon>
              <el-icon v-else-if="bot.platform === 'telegram'"><Message /></el-icon>
              <el-icon v-else><ChatDotRound /></el-icon>
            </div>
            <div class="bot-info">
              <div class="bot-name">{{ bot.name }}</div>
              <div class="bot-platform">{{ getPlatformName(bot.platform) }}</div>
            </div>
            <el-tag size="small">{{ bot.target_channel || '默认' }}</el-tag>
          </div>

          <el-empty v-if="filteredTargetBots.length === 0" description="暂无Bot配置">
            <el-button type="primary" @click="goToBotsConfig">配置Bot</el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 映射列表 -->
    <div class="mapping-list">
      <h3>📋 当前映射关系（{{ mappings.length }}条）</h3>
      <el-table :data="mappings" stripe style="width: 100%">
        <el-table-column prop="source_name" label="KOOK频道" width="200">
          <template #default="{ row }">
            <el-icon><ChatDotRound /></el-icon>
            {{ row.source_name }}
          </template>
        </el-table-column>
        <el-table-column label="→" width="80" align="center">
          <template #default>
            <el-icon :size="20"><ArrowRight /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="target_name" label="目标Bot" width="200">
          <template #default="{ row }">
            {{ row.target_name }}
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-tag :type="getPlatformTagType(row.platform)">
              {{ getPlatformName(row.platform) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="启用" width="100">
          <template #default="{ row, $index }">
            <el-switch v-model="row.enabled" @change="toggleMapping($index)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ $index }">
            <el-button type="danger" size="small" @click="removeMapping($index)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Refresh, Check, Search, OfficeBuilding, ChatDotRound,
  Connection, Message, ArrowRight
} from '@element-plus/icons-vue';
import axios from 'axios';

const router = useRouter();

// 数据
const sourceServers = ref([]);
const targetBots = ref([]);
const mappings = ref([]);

// 选中状态
const selectedSource = ref(null);
const selectedTarget = ref(null);

// 搜索
const sourceSearch = ref('');
const targetSearch = ref('');

// UI状态
const isSaving = ref(false);
const canvasRef = ref(null);
const svgRef = ref(null);

// 计算属性
const filteredSourceServers = computed(() => {
  if (!sourceSearch.value) return sourceServers.value;
  
  const keyword = sourceSearch.value.toLowerCase();
  return sourceServers.value
    .map(server => ({
      ...server,
      channels: server.channels.filter(ch =>
        ch.name.toLowerCase().includes(keyword)
      )
    }))
    .filter(server => server.channels.length > 0);
});

const filteredTargetBots = computed(() => {
  if (!targetSearch.value) return targetBots.value;
  
  const keyword = targetSearch.value.toLowerCase();
  return targetBots.value.filter(bot =>
    bot.name.toLowerCase().includes(keyword) ||
    bot.platform.toLowerCase().includes(keyword)
  );
});

// 方法
const selectSource = (channel, server) => {
  selectedSource.value = {
    ...channel,
    server_id: server.id,
    server_name: server.name
  };
  
  // 如果已选择目标，自动创建映射
  if (selectedTarget.value) {
    createMapping();
  }
};

const selectTarget = (bot) => {
  selectedTarget.value = bot;
  
  // 如果已选择源，自动创建映射
  if (selectedSource.value) {
    createMapping();
  }
};

const createMapping = () => {
  if (!selectedSource.value || !selectedTarget.value) return;
  
  // 检查是否已存在相同映射
  const exists = mappings.value.some(m =>
    m.source_id === selectedSource.value.id &&
    m.target_id === selectedTarget.value.id
  );
  
  if (exists) {
    ElMessage.warning('该映射已存在');
    return;
  }
  
  mappings.value.push({
    source_id: selectedSource.value.id,
    source_name: `${selectedSource.value.server_name} / ${selectedSource.value.name}`,
    server_id: selectedSource.value.server_id,
    channel_id: selectedSource.value.id,
    target_id: selectedTarget.value.id,
    target_name: selectedTarget.value.name,
    platform: selectedTarget.value.platform,
    target_channel: selectedTarget.value.target_channel,
    enabled: true
  });
  
  ElMessage.success('映射创建成功');
  
  // 清空选择
  selectedSource.value = null;
  selectedTarget.value = null;
};

const removeMapping = (index) => {
  ElMessageBox.confirm('确定要删除这个映射吗？', '确认', {
    type: 'warning'
  }).then(() => {
    mappings.value.splice(index, 1);
    ElMessage.success('映射已删除');
  }).catch(() => {});
};

const removeMappingLine = (mapping, index) => {
  removeMapping(index);
};

const toggleMapping = (index) => {
  const mapping = mappings.value[index];
  ElMessage.info(mapping.enabled ? '映射已启用' : '映射已禁用');
};

const getMappingCount = (channelId) => {
  return mappings.value.filter(m => m.source_id === channelId).length;
};

const isHighlighted = (mapping) => {
  return (
    (selectedSource.value && mapping.source_id === selectedSource.value.id) ||
    (selectedTarget.value && mapping.target_id === selectedTarget.value.id)
  );
};

const calculatePath = (mapping) => {
  // 获取源和目标元素的位置
  const sourceEl = canvasRef.value?.querySelector(`[data-channel-id="${mapping.source_id}"]`);
  const targetEl = canvasRef.value?.querySelector(`[data-bot-id="${mapping.target_id}"]`);
  
  if (!sourceEl || !targetEl || !svgRef.value) return '';
  
  const canvasRect = canvasRef.value.getBoundingClientRect();
  const sourceRect = sourceEl.getBoundingClientRect();
  const targetRect = targetEl.getBoundingClientRect();
  
  const startX = sourceRect.right - canvasRect.left;
  const startY = sourceRect.top + sourceRect.height / 2 - canvasRect.top;
  const endX = targetRect.left - canvasRect.left;
  const endY = targetRect.top + targetRect.height / 2 - canvasRect.top;
  
  // 贝塞尔曲线
  const controlX1 = startX + (endX - startX) * 0.3;
  const controlX2 = endX - (endX - startX) * 0.3;
  
  return `M ${startX} ${startY} C ${controlX1} ${startY}, ${controlX2} ${endY}, ${endX} ${endY}`;
};

const calculateMidpoint = (mapping) => {
  const sourceEl = canvasRef.value?.querySelector(`[data-channel-id="${mapping.source_id}"]`);
  const targetEl = canvasRef.value?.querySelector(`[data-bot-id="${mapping.target_id}"]`);
  
  if (!sourceEl || !targetEl) return null;
  
  const canvasRect = canvasRef.value.getBoundingClientRect();
  const sourceRect = sourceEl.getBoundingClientRect();
  const targetRect = targetEl.getBoundingClientRect();
  
  const startX = sourceRect.right - canvasRect.left;
  const startY = sourceRect.top + sourceRect.height / 2 - canvasRect.top;
  const endX = targetRect.left - canvasRect.left;
  const endY = targetRect.top + targetRect.height / 2 - canvasRect.top;
  
  return {
    x: (startX + endX) / 2,
    y: (startY + endY) / 2
  };
};

const getPlatformName = (platform) => {
  const names = {
    discord: 'Discord',
    telegram: 'Telegram',
    feishu: '飞书'
  };
  return names[platform] || platform;
};

const getPlatformTagType = (platform) => {
  const types = {
    discord: 'primary',
    telegram: 'success',
    feishu: 'warning'
  };
  return types[platform] || 'info';
};

const loadMappings = async () => {
  try {
    // 加载服务器和频道
    const serversRes = await axios.get('http://localhost:9527/api/accounts');
    if (serversRes.data.length > 0) {
      const accountId = serversRes.data[0].id;
      const channelsRes = await axios.get(`http://localhost:9527/api/servers/discover/${accountId}`);
      sourceServers.value = channelsRes.data.servers || [];
    }
    
    // 加载Bots
    const botsRes = await axios.get('http://localhost:9527/api/bots');
    targetBots.value = botsRes.data || [];
    
    // 加载现有映射
    const mappingsRes = await axios.get('http://localhost:9527/api/mappings');
    mappings.value = mappingsRes.data || [];
    
    await nextTick();
    ElMessage.success('数据加载成功');
  } catch (error) {
    ElMessage.error(`加载失败：${error.message}`);
  }
};

const saveMappings = async () => {
  isSaving.value = true;
  
  try {
    await axios.post('http://localhost:9527/api/mappings/batch-save', {
      mappings: mappings.value
    });
    
    ElMessage.success('映射保存成功');
  } catch (error) {
    ElMessage.error(`保存失败：${error.message}`);
  } finally {
    isSaving.value = false;
  }
};

const goToBotsConfig = () => {
  router.push('/bots');
};

onMounted(() => {
  loadMappings();
  
  // 监听窗口大小变化，重新绘制连线
  window.addEventListener('resize', () => {
    nextTick(() => {
      // 触发重新渲染
      mappings.value = [...mappings.value];
    });
  });
});
</script>

<style scoped>
.mapping-visual {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.mapping-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.mapping-canvas {
  position: relative;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 20px;
  flex: 1;
  overflow: hidden;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
}

.source-panel,
.target-panel {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.panel-header {
  margin-bottom: 15px;
}

.panel-header h3 {
  margin-bottom: 10px;
  color: #333;
}

.channel-list,
.bot-list {
  flex: 1;
  overflow-y: auto;
}

.server-group {
  margin-bottom: 15px;
}

.server-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  padding: 8px;
  background: #f0f2f5;
  border-radius: 4px;
}

.channel-node,
.bot-node {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  margin: 5px 0;
  background: #f9fafc;
  border: 2px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.channel-node:hover,
.bot-node:hover {
  background: #ecf5ff;
  border-color: #409EFF;
  transform: translateX(5px);
}

.channel-node.selected,
.bot-node.selected {
  background: #409EFF;
  color: white;
  border-color: #409EFF;
}

.bot-node {
  flex-direction: row;
}

.bot-node.discord {
  border-left: 4px solid #5865F2;
}

.bot-node.telegram {
  border-left: 4px solid #0088cc;
}

.bot-node.feishu {
  border-left: 4px solid #00B96B;
}

.bot-icon {
  font-size: 24px;
}

.bot-info {
  flex: 1;
}

.bot-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.bot-platform {
  font-size: 12px;
  color: #909399;
}

.connection-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
}

.connection-line {
  pointer-events: all;
  cursor: pointer;
  transition: all 0.3s;
}

.connection-line:hover,
.connection-line.highlighted {
  stroke: #67C23A;
  stroke-width: 3;
}

.delete-button,
.delete-icon {
  cursor: pointer;
  pointer-events: all;
}

.delete-button:hover {
  r: 14;
  fill: #c0392b;
}

.mapping-list {
  margin-top: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.mapping-list h3 {
  margin-bottom: 15px;
  color: #333;
}
</style>
