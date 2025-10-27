<template>
  <div class="draggable-mapping-ultimate">
    <el-alert type="info" :closable="false" class="mapping-info">
      <template #title>
        拖拽创建映射关系
      </template>
      从左侧KOOK频道拖拽到右侧目标平台，即可创建映射。支持一对多映射。
    </el-alert>

    <div class="mapping-workspace">
      <!-- 左侧：KOOK频道列表 -->
      <el-card class="channel-panel kook-panel" shadow="hover">
        <template #header>
          <div class="panel-header">
            <span>
              <el-icon><Notification /></el-icon>
              KOOK频道（源）
            </span>
            <el-tag>{{ kookChannels.length }}个</el-tag>
          </div>
        </template>

        <el-scrollbar height="600px">
          <div class="server-group" v-for="server in kookServers" :key="server.id">
            <div class="server-name">
              <el-icon><Folder /></el-icon>
              {{ server.name }}
            </div>
            
            <draggable
              :list="getChannelsForServer(server.id)"
              :group="{ name: 'channels', pull: 'clone', put: false }"
              :clone="cloneChannel"
              item-key="id"
              class="channel-list"
            >
              <template #item="{ element }">
                <div class="channel-item kook-channel">
                  <el-icon><ChatDotRound /></el-icon>
                  <span># {{ element.name }}</span>
                  <el-tag size="small" type="info">{{ element.type }}</el-tag>
                </div>
              </template>
            </draggable>
          </div>
        </el-scrollbar>
      </el-card>

      <!-- 中间：映射可视化 -->
      <div class="mapping-visual">
        <svg width="100%" height="100%" ref="svgRef">
          <!-- 映射连接线 -->
          <line
            v-for="(mapping, index) in mappings"
            :key="`line-${index}`"
            :x1="50"
            :y1="getMappingY(index, 'source')"
            :x2="150"
            :y2="getMappingY(index, 'target')"
            stroke="#409EFF"
            stroke-width="2"
            stroke-dasharray="5,5"
          >
            <animate
              attributeName="stroke-dashoffset"
              from="0"
              to="10"
              dur="1s"
              repeatCount="indefinite"
            />
          </line>
          
          <!-- 箭头 -->
          <polygon
            v-for="(mapping, index) in mappings"
            :key="`arrow-${index}`"
            :points="getArrowPoints(index)"
            fill="#409EFF"
          />
        </svg>
        
        <div class="mapping-count">
          <el-statistic :value="mappings.length" title="已创建映射" />
        </div>
      </div>

      <!-- 右侧：目标平台 -->
      <el-card class="channel-panel target-panel" shadow="hover">
        <template #header>
          <div class="panel-header">
            <span>
              <el-icon><Position /></el-icon>
              目标平台（接收）
            </span>
          </div>
        </template>

        <el-scrollbar height="600px">
          <el-tabs v-model="activePlatform" class="platform-tabs">
            <!-- Discord -->
            <el-tab-pane label="Discord" name="discord">
              <draggable
                :list="discordChannels"
                :group="{ name: 'channels', pull: false, put: true }"
                item-key="id"
                @add="handleChannelDrop($event, 'discord')"
                class="channel-list drop-zone"
              >
                <template #item="{ element }">
                  <div class="channel-item target-channel">
                    <el-icon><ChatDotRound /></el-icon>
                    <span># {{ element.name }}</span>
                  </div>
                </template>
                
                <template #footer>
                  <div class="drop-hint">
                    拖拽KOOK频道到此创建映射
                  </div>
                </template>
              </draggable>
            </el-tab-pane>

            <!-- Telegram -->
            <el-tab-pane label="Telegram" name="telegram">
              <draggable
                :list="telegramChats"
                :group="{ name: 'channels', pull: false, put: true }"
                item-key="id"
                @add="handleChannelDrop($event, 'telegram')"
                class="channel-list drop-zone"
              >
                <template #item="{ element }">
                  <div class="channel-item target-channel">
                    <el-icon><ChatDotRound /></el-icon>
                    <span>{{ element.name }}</span>
                  </div>
                </template>
                
                <template #footer>
                  <div class="drop-hint">
                    拖拽KOOK频道到此创建映射
                  </div>
                </template>
              </draggable>
            </el-tab-pane>

            <!-- 飞书 -->
            <el-tab-pane label="飞书" name="feishu">
              <draggable
                :list="feishuGroups"
                :group="{ name: 'channels', pull: false, put: true }"
                item-key="id"
                @add="handleChannelDrop($event, 'feishu')"
                class="channel-list drop-zone"
              >
                <template #item="{ element }">
                  <div class="channel-item target-channel">
                    <el-icon><ChatDotRound /></el-icon>
                    <span>{{ element.name }}</span>
                  </div>
                </template>
                
                <template #footer>
                  <div class="drop-hint">
                    拖拽KOOK频道到此创建映射
                  </div>
                </template>
              </draggable>
            </el-tab-pane>
          </el-tabs>
        </el-scrollbar>
      </el-card>
    </div>

    <!-- 已创建的映射列表 -->
    <el-card v-if="mappings.length > 0" class="mappings-list" shadow="hover">
      <template #header>
        <div class="panel-header">
          <span>已创建的映射关系</span>
          <el-tag type="success">{{ mappings.length }}个</el-tag>
        </div>
      </template>

      <el-table :data="mappings">
        <el-table-column label="KOOK频道" width="250">
          <template #default="{ row }">
            <el-tag type="primary"># {{ row.kook_channel_name }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="→" width="60" align="center">
          <template #default>
            <el-icon><Right /></el-icon>
          </template>
        </el-table-column>

        <el-table-column label="目标平台" width="120">
          <template #default="{ row }">
            <el-tag :type="getPlatformColor(row.target_platform)">
              {{ getPlatformName(row.target_platform) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="目标频道" min-width="200">
          <template #default="{ row }">
            <span>{{ row.target_channel_name }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" align="center">
          <template #default="{ $index }">
            <el-button 
              type="danger" 
              size="small"
              @click="deleteMapping($index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="list-actions">
        <el-button @click="clearAllMappings" type="danger" plain>
          清空所有映射
        </el-button>
        <el-button @click="saveMappings" type="primary">
          保存映射配置
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import draggable from 'vuedraggable';
import {
  Notification,
  Position,
  Folder,
  ChatDotRound,
  Right
} from '@element-plus/icons-vue';
import api from '@/api';

// 数据
const kookServers = ref([]);
const kookChannels = ref([]);
const discordChannels = ref([]);
const telegramChats = ref([]);
const feishuGroups = ref([]);
const mappings = ref([]);
const activePlatform = ref('discord');
const svgRef = ref(null);

// 加载数据
onMounted(async () => {
  await loadKookChannels();
  await loadTargetChannels();
});

// 加载KOOK频道
const loadKookChannels = async () => {
  try {
    const response = await api.get('/api/accounts/servers');
    kookServers.value = response.servers;
    kookChannels.value = response.servers.flatMap(s => 
      s.channels.map(c => ({ ...c, server_id: s.id, server_name: s.name }))
    );
  } catch (error) {
    ElMessage.error('加载KOOK频道失败');
  }
};

// 加载目标平台频道
const loadTargetChannels = async () => {
  // TODO: 从后端API获取目标平台频道列表
  // 这里使用模拟数据
  discordChannels.value = [
    { id: 'disc-1', name: 'announcements' },
    { id: 'disc-2', name: 'general' },
    { id: 'disc-3', name: 'events' }
  ];
  
  telegramChats.value = [
    { id: 'tg-1', name: '公告群' },
    { id: 'tg-2', name: '讨论群' }
  ];
  
  feishuGroups.value = [
    { id: 'fs-1', name: '运营群' },
    { id: 'fs-2', name: '技术群' }
  ];
};

// 获取指定服务器的频道
const getChannelsForServer = (serverId) => {
  return kookChannels.value.filter(c => c.server_id === serverId);
};

// 克隆频道（拖拽时）
const cloneChannel = (channel) => {
  return { ...channel };
};

// 处理频道拖拽
const handleChannelDrop = (event, platform) => {
  const kookChannel = event.item._underlying_vm_;
  const targetIndex = event.newIndex;
  
  let targetChannelList, targetChannel;
  
  if (platform === 'discord') {
    targetChannelList = discordChannels.value;
  } else if (platform === 'telegram') {
    targetChannelList = telegramChats.value;
  } else {
    targetChannelList = feishuGroups.value;
  }
  
  targetChannel = targetChannelList[targetIndex];
  
  if (!targetChannel) {
    ElMessage.warning('请拖拽到目标频道上');
    return;
  }
  
  // 创建映射
  const mapping = {
    kook_server_id: kookChannel.server_id,
    kook_server_name: kookChannel.server_name,
    kook_channel_id: kookChannel.id,
    kook_channel_name: kookChannel.name,
    target_platform: platform,
    target_channel_id: targetChannel.id,
    target_channel_name: targetChannel.name
  };
  
  // 检查是否已存在
  const exists = mappings.value.some(m => 
    m.kook_channel_id === mapping.kook_channel_id &&
    m.target_platform === mapping.target_platform &&
    m.target_channel_id === mapping.target_channel_id
  );
  
  if (exists) {
    ElMessage.warning('此映射已存在');
    return;
  }
  
  mappings.value.push(mapping);
  ElMessage.success(`已创建映射：${kookChannel.name} → ${platform} ${targetChannel.name}`);
};

// 删除映射
const deleteMapping = (index) => {
  const mapping = mappings.value[index];
  mappings.value.splice(index, 1);
  ElMessage.success(`已删除映射：${mapping.kook_channel_name}`);
};

// 清空所有映射
const clearAllMappings = () => {
  mappings.value = [];
  ElMessage.success('已清空所有映射');
};

// 保存映射
const saveMappings = async () => {
  try {
    await api.post('/api/mappings/batch', { mappings: mappings.value });
    ElMessage.success('映射配置已保存');
  } catch (error) {
    ElMessage.error('保存失败，请重试');
  }
};

// 获取平台名称
const getPlatformName = (platform) => {
  const names = { discord: 'Discord', telegram: 'Telegram', feishu: '飞书' };
  return names[platform] || platform;
};

// 获取平台颜色
const getPlatformColor = (platform) => {
  const colors = { discord: 'primary', telegram: 'success', feishu: 'warning' };
  return colors[platform] || '';
};

// 计算映射线的Y坐标
const getMappingY = (index, type) => {
  const baseY = 50;
  const spacing = 60;
  return baseY + index * spacing;
};

// 获取箭头点坐标
const getArrowPoints = (index) => {
  const y = getMappingY(index, 'target');
  return `150,${y} 140,${y-5} 140,${y+5}`;
};
</script>

<style scoped>
.draggable-mapping-ultimate {
  padding: 20px;
}

.mapping-info {
  margin-bottom: 24px;
}

.mapping-workspace {
  display: grid;
  grid-template-columns: 1fr 200px 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.channel-panel {
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.server-group {
  margin-bottom: 20px;
}

.server-name {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #F5F7FA;
  border-radius: 4px;
  font-weight: 600;
  margin-bottom: 8px;
}

.channel-list {
  min-height: 100px;
  padding: 8px;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  cursor: move;
  transition: all 0.3s;
}

.channel-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.kook-channel {
  background: #ECF5FF;
  border-color: #B3D8FF;
}

.target-channel {
  background: #F0F9FF;
  border-color: #BAE6FD;
}

.drop-zone {
  min-height: 300px;
  border: 2px dashed #DCDFE6;
  border-radius: 4px;
  padding: 16px;
}

.drop-zone.dragging {
  border-color: #409EFF;
  background: #ECF5FF;
}

.drop-hint {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
  font-size: 14px;
}

.mapping-visual {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #FAFAFA;
  border-radius: 8px;
  position: relative;
}

.mapping-count {
  position: absolute;
  bottom: 20px;
}

.mappings-list {
  margin-top: 24px;
}

.list-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #EBEEF5;
}

.platform-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}
</style>
