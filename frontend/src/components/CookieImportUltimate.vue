<template>
  <div class="cookie-import-ultimate">
    <el-alert 
      type="info" 
      :closable="false"
      class="import-tips"
    >
      <template #title>
        <div style="display: flex; align-items: center; gap: 10px;">
          <el-icon><InfoFilled /></el-icon>
          <span>Cookie导入方式（3种）</span>
        </div>
      </template>
      <ol style="margin: 10px 0 0 20px; padding: 0;">
        <li><strong>拖拽文件</strong>：将Cookie JSON文件拖拽到下方区域</li>
        <li><strong>粘贴文本</strong>：直接粘贴Cookie内容（支持JSON/Netscape格式）</li>
        <li><strong>浏览器扩展</strong>：使用Chrome扩展一键导出 
          <el-link type="primary" @click="downloadExtension">下载扩展</el-link>
        </li>
      </ol>
    </el-alert>

    <!-- 拖拽上传区域 -->
    <el-upload
      ref="uploadRef"
      class="cookie-upload"
      drag
      accept=".json,.txt"
      :auto-upload="false"
      :on-change="handleFileChange"
      :show-file-list="false"
      :limit="1"
    >
      <el-icon class="upload-icon"><upload-filled /></el-icon>
      <div class="upload-text">
        <p class="primary-text">拖拽Cookie文件到此，或点击上传</p>
        <p class="secondary-text">支持格式：JSON, TXT（最大5MB）</p>
      </div>
    </el-upload>

    <!-- 或分隔线 -->
    <el-divider>或</el-divider>

    <!-- 文本粘贴区域 -->
    <div class="paste-area">
      <el-input
        v-model="cookieText"
        type="textarea"
        :rows="8"
        placeholder="直接粘贴Cookie内容到此（支持JSON或Netscape格式）&#10;&#10;JSON格式示例：&#10;[&#10;  {&quot;name&quot;: &quot;token&quot;, &quot;value&quot;: &quot;xxx&quot;, &quot;domain&quot;: &quot;.kookapp.cn&quot;},&#10;  ...&#10;]&#10;&#10;Netscape格式示例：&#10;.kookapp.cn    TRUE    /    FALSE    0    token    xxx"
        @input="handleTextInput"
      />
      
      <div class="paste-actions">
        <el-button @click="clearText" :disabled="!cookieText">清空</el-button>
        <el-button type="primary" @click="parseCookie" :disabled="!cookieText" :loading="parsing">
          <el-icon><Check /></el-icon>
          解析Cookie
        </el-button>
      </div>
    </div>

    <!-- 解析结果预览 -->
    <transition name="el-fade-in">
      <el-card v-if="parsedCookies" class="result-card" shadow="hover">
        <template #header>
          <div class="result-header">
            <span>
              <el-icon color="#67C23A"><SuccessFilled /></el-icon>
              Cookie解析成功
            </span>
            <el-tag type="success">共 {{ parsedCookies.length }} 条</el-tag>
          </div>
        </template>
        
        <div class="cookie-list">
          <el-scrollbar max-height="300px">
            <div v-for="(cookie, index) in parsedCookies" :key="index" class="cookie-item">
              <div class="cookie-name">
                <el-tag size="small">{{ cookie.name }}</el-tag>
              </div>
              <div class="cookie-value">
                <code>{{ truncate(cookie.value, 50) }}</code>
              </div>
              <div class="cookie-domain">
                <el-text type="info" size="small">{{ cookie.domain }}</el-text>
              </div>
            </div>
          </el-scrollbar>
        </div>
        
        <div class="result-actions">
          <el-button @click="clearParsed">重新导入</el-button>
          <el-button type="success" @click="confirmImport" :loading="importing">
            <el-icon><Check /></el-icon>
            确认导入
          </el-button>
        </div>
      </el-card>
    </transition>

    <!-- 错误提示 -->
    <transition name="el-fade-in">
      <el-alert
        v-if="error"
        type="error"
        :title="error"
        show-icon
        closable
        @close="error = ''"
        class="error-alert"
      >
        <template v-if="errorDetails">
          <el-collapse style="margin-top: 10px;">
            <el-collapse-item title="查看详细错误信息" name="1">
              <pre style="font-size: 12px; overflow-x: auto;">{{ errorDetails }}</pre>
            </el-collapse-item>
          </el-collapse>
        </template>
      </el-alert>
    </transition>

    <!-- 帮助链接 -->
    <div class="help-links">
      <el-link :underline="false" @click="showTutorial">
        <el-icon><QuestionFilled /></el-icon>
        如何获取Cookie？
      </el-link>
      <el-link :underline="false" @click="showVideoTutorial">
        <el-icon><VideoPlay /></el-icon>
        观看视频教程
      </el-link>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  InfoFilled,
  UploadFilled,
  Check,
  SuccessFilled,
  QuestionFilled,
  VideoPlay
} from '@element-plus/icons-vue';

const emit = defineEmits(['import-success']);

// 数据
const uploadRef = ref();
const cookieText = ref('');
const parsedCookies = ref(null);
const parsing = ref(false);
const importing = ref(false);
const error = ref('');
const errorDetails = ref('');

/**
 * 处理文件拖拽上传
 */
const handleFileChange = (file) => {
  const reader = new FileReader();
  
  reader.onload = (e) => {
    try {
      cookieText.value = e.target.result;
      parseCookie();
    } catch (err) {
      error.value = '文件读取失败';
      errorDetails.value = err.message;
    }
  };
  
  reader.onerror = () => {
    error.value = '文件读取失败';
  };
  
  reader.readAsText(file.raw);
};

/**
 * 处理文本输入（实时验证）
 */
const handleTextInput = () => {
  error.value = '';
  errorDetails.value = '';
  parsedCookies.value = null;
};

/**
 * 解析Cookie
 */
const parseCookie = async () => {
  if (!cookieText.value.trim()) {
    error.value = 'Cookie内容不能为空';
    return;
  }
  
  parsing.value = true;
  error.value = '';
  errorDetails.value = '';
  parsedCookies.value = null;
  
  try {
    const text = cookieText.value.trim();
    
    // 尝试JSON格式
    if (text.startsWith('[') || text.startsWith('{')) {
      const cookies = JSON.parse(text);
      parsedCookies.value = Array.isArray(cookies) ? cookies : [cookies];
    }
    // 尝试Netscape格式
    else {
      parsedCookies.value = parseNetscapeFormat(text);
    }
    
    // 验证Cookie有效性
    if (!parsedCookies.value || parsedCookies.value.length === 0) {
      throw new Error('未解析到任何Cookie');
    }
    
    // 检查必需字段
    for (const cookie of parsedCookies.value) {
      if (!cookie.name || !cookie.value) {
        throw new Error(`Cookie缺少必需字段: ${JSON.stringify(cookie)}`);
      }
    }
    
    // 检查是否包含KOOK的Cookie
    const hasKookCookie = parsedCookies.value.some(c => 
      c.domain && (c.domain.includes('kookapp.cn') || c.domain.includes('kaiheila.cn'))
    );
    
    if (!hasKookCookie) {
      ElMessageBox.confirm(
        '未检测到KOOK相关的Cookie（域名应为kookapp.cn），是否继续？',
        '警告',
        {
          confirmButtonText: '继续',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).catch(() => {
        parsedCookies.value = null;
      });
    }
    
  } catch (err) {
    error.value = 'Cookie解析失败';
    errorDetails.value = err.message;
    parsedCookies.value = null;
  } finally {
    parsing.value = false;
  }
};

/**
 * 解析Netscape格式Cookie
 */
const parseNetscapeFormat = (text) => {
  const lines = text.split('\n').filter(line => 
    line.trim() && !line.trim().startsWith('#')
  );
  
  const cookies = [];
  
  for (const line of lines) {
    const parts = line.split('\t');
    if (parts.length >= 7) {
      cookies.push({
        domain: parts[0],
        path: parts[2],
        secure: parts[3] === 'TRUE',
        expiry: parseInt(parts[4]),
        name: parts[5],
        value: parts[6]
      });
    }
  }
  
  return cookies;
};

/**
 * 截断字符串
 */
const truncate = (str, length) => {
  if (str.length <= length) return str;
  return str.substring(0, length) + '...';
};

/**
 * 清空文本
 */
const clearText = () => {
  cookieText.value = '';
  parsedCookies.value = null;
  error.value = '';
  errorDetails.value = '';
};

/**
 * 清除解析结果
 */
const clearParsed = () => {
  parsedCookies.value = null;
  error.value = '';
  errorDetails.value = '';
};

/**
 * 确认导入
 */
const confirmImport = () => {
  importing.value = true;
  
  // 模拟API调用（实际应调用后端API）
  setTimeout(() => {
    importing.value = false;
    ElMessage.success('Cookie导入成功！');
    emit('import-success', parsedCookies.value);
  }, 1000);
};

/**
 * 下载Chrome扩展
 */
const downloadExtension = () => {
  window.open('/downloads/kook-cookie-exporter.zip', '_blank');
  ElMessage.info('Chrome扩展下载中...');
};

/**
 * 显示教程
 */
const showTutorial = () => {
  ElMessageBox.alert(
    '<ol><li>打开KOOK网页版（www.kookapp.cn）</li><li>登录您的账号</li><li>按F12打开开发者工具</li><li>切换到"Application"标签</li><li>左侧选择"Cookies" → "https://www.kookapp.cn"</li><li>复制所有Cookie内容</li></ol>',
    '如何获取Cookie',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '我知道了'
    }
  );
};

/**
 * 显示视频教程
 */
const showVideoTutorial = () => {
  ElMessage.info('视频教程开发中...');
};
</script>

<style scoped>
.cookie-import-ultimate {
  max-width: 800px;
  margin: 0 auto;
}

.import-tips {
  margin-bottom: 20px;
}

.cookie-upload {
  margin: 20px 0;
}

.cookie-upload :deep(.el-upload-dragger) {
  padding: 40px 20px;
}

.upload-icon {
  font-size: 60px;
  color: #409EFF;
  margin-bottom: 16px;
}

.upload-text .primary-text {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 8px 0;
}

.upload-text .secondary-text {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.paste-area {
  margin: 20px 0;
}

.paste-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.result-card {
  margin: 20px 0;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cookie-list {
  margin: 10px 0;
}

.cookie-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  border-bottom: 1px solid #EBEEF5;
}

.cookie-item:last-child {
  border-bottom: none;
}

.cookie-name {
  flex-shrink: 0;
  min-width: 120px;
}

.cookie-value {
  flex: 1;
  overflow: hidden;
}

.cookie-value code {
  display: block;
  background: #F5F7FA;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cookie-domain {
  flex-shrink: 0;
  min-width: 150px;
  text-align: right;
}

.result-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.error-alert {
  margin: 20px 0;
}

.help-links {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px dashed #DCDFE6;
}
</style>
