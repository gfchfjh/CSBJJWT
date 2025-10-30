<template>
  <div class="step-servers">
    <h2>🏠 选择要监听的KOOK服务器</h2>
    
    <el-alert
      v-if="!accountAdded"
      title="请先在上一步添加KOOK账号"
      type="warning"
      :closable="false"
      class="help-alert"
    />

    <el-alert
      v-else-if="loading"
      title="正在加载服务器列表，请稍候..."
      type="info"
      :closable="false"
      class="help-alert"
    />

    <div v-else-if="servers.length === 0 && !loading" class="empty-servers">
      <el-empty description="未获取到服务器列表">
        <el-button type="primary" @click="emit('loadServers')">
          重新加载
        </el-button>
      </el-empty>
    </div>

    <div v-else class="servers-list">
      <el-alert
        title="请选择需要监听的服务器和频道"
        type="info"
        :closable="false"
        class="help-alert"
      >
        <p>提示：</p>
        <ul>
          <li>只有选中的频道才会被监听</li>
          <li>可以在后续的"频道映射"页面中设置转发规则</li>
          <li>支持全选或按需选择</li>
        </ul>
      </el-alert>

      <div class="server-selection">
        <div class="toolbar">
          <el-button size="small" @click="emit('selectAll')">全选</el-button>
          <el-button size="small" @click="emit('unselectAll')">全不选</el-button>
          <span class="selection-count">
            已选择：{{ selectedCount }} 个频道
          </span>
        </div>

        <el-collapse v-model="activeServers" accordion>
          <el-collapse-item
            v-for="server in servers"
            :key="server.id"
            :name="server.id"
            :title="`${server.name} (${server.channels?.length || 0}个频道)`"
          >
            <template #title>
              <div class="server-header">
                <el-checkbox
                  v-model="server.selected"
                  @change="emit('toggleServer', server)"
                  @click.stop
                />
                <img
                  v-if="server.icon"
                  :src="server.icon"
                  class="server-icon"
                  alt="server icon"
                />
                <span class="server-name">{{ server.name }}</span>
                <el-tag size="small" type="info">
                  {{ server.channels?.length || 0 }}个频道
                </el-tag>
              </div>
            </template>

            <div v-if="!server.channels" class="loading-channels">
              <el-button
                type="primary"
                size="small"
                :loading="loadingChannels[server.id]"
                @click="emit('loadChannels', server.id)"
              >
                加载频道列表
              </el-button>
            </div>

            <el-checkbox-group
              v-else
              v-model="server.selectedChannels"
              class="channels-list"
            >
              <el-checkbox
                v-for="channel in server.channels"
                :key="channel.id"
                :label="channel.id"
                class="channel-item"
              >
                <span class="channel-icon">
                  {{ channel.type === 'voice' ? '🔊' : '#' }}
                </span>
                {{ channel.name }}
                <el-tag v-if="channel.type === 'voice'" size="small" type="warning">
                  语音
                </el-tag>
              </el-checkbox>
            </el-checkbox-group>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <div class="action-buttons">
      <el-button @click="emit('prev')">上一步</el-button>
      <el-button
        type="primary"
        :disabled="selectedCount === 0"
        @click="emit('next')"
      >
        继续（已选 {{ selectedCount }} 个频道）
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  servers: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingChannels: {
    type: Object,
    default: () => ({})
  },
  accountAdded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['next', 'prev', 'loadServers', 'loadChannels', 'toggleServer', 'selectAll', 'unselectAll'])

const activeServers = ref([])

const selectedCount = computed(() => {
  return props.servers.reduce((count, server) => {
    return count + (server.selectedChannels?.length || 0)
  }, 0)
})
</script>

<style scoped>
h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.step-servers {
  padding: 20px;
}

.empty-servers {
  padding: 60px 20px;
  text-align: center;
}

.servers-list {
  margin-top: 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.selection-count {
  margin-left: auto;
  color: #409eff;
  font-weight: bold;
}

.server-header {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.server-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

.server-name {
  flex: 1;
  font-weight: 500;
}

.loading-channels {
  padding: 20px;
  text-align: center;
}

.channels-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 15px;
}

.channel-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.channel-item:hover {
  background-color: #f5f7fa;
}

.channel-icon {
  font-size: 16px;
  margin-right: 5px;
}

.server-selection {
  max-height: 500px;
  overflow-y: auto;
}

.help-alert {
  margin-bottom: 20px;
}

.help-alert ol, .help-alert ul {
  margin: 10px 0;
  padding-left: 25px;
}

.help-alert li {
  margin: 5px 0;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}
</style>
