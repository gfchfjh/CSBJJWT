<template>
  <div class="step-complete">
    <el-result
      icon="success"
      title="✅ 配置完成！"
      sub-title="您已成功完成基础配置"
    >
      <template #extra>
        <div class="complete-summary">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="KOOK账号">
              {{ accountAdded ? '✅ 已添加' : '❌ 未添加' }}
            </el-descriptions-item>
            <el-descriptions-item label="监听频道">
              ✅ {{ selectedChannelsCount }}个频道
            </el-descriptions-item>
            <el-descriptions-item label="机器人配置">
              ✅ {{ botsCount }}个平台
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            title="接下来您可以："
            type="success"
            :closable="false"
            style="margin-top: 20px"
          >
            <ul>
              <li>在"频道映射"中设置转发规则</li>
              <li>启动服务开始转发消息</li>
              <li>在"日志"中查看转发状态</li>
            </ul>
          </el-alert>
        </div>

        <div class="action-buttons">
          <el-button type="primary" size="large" @click="emit('finish')">
            进入主界面
          </el-button>
        </div>
      </template>
    </el-result>
  </div>
</template>

<script setup>
const props = defineProps({
  accountAdded: {
    type: Boolean,
    default: false
  },
  selectedChannelsCount: {
    type: Number,
    default: 0
  },
  botsCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['finish'])
</script>

<style scoped>
.complete-summary {
  margin: 30px 0;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}
</style>
