<template>
  <div class="help-center">
    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索教程、FAQ..."
        size="large"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <div v-if="searchResults.length > 0" class="search-results">
        <h3>搜索结果 ({{ searchResults.length }})</h3>
        <div class="tutorial-grid">
          <TutorialCard
            v-for="tutorial in searchResults"
            :key="tutorial.id"
            :tutorial="tutorial"
            @click="openTutorial(tutorial)"
          />
        </div>
      </div>
    </div>

    <!-- 分类导航 -->
    <div v-if="!searchKeyword" class="categories">
      <el-tabs v-model="activeCategory" @tab-change="handleCategoryChange">
        <el-tab-pane label="🚀 快速入门" name="getting-started">
          <div class="tutorial-grid">
            <TutorialCard
              v-for="tutorial in getCategoryTutorials('getting-started')"
              :key="tutorial.id"
              :tutorial="tutorial"
              @click="openTutorial(tutorial)"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="⚙️ 配置指南" name="configuration">
          <div class="tutorial-grid">
            <TutorialCard
              v-for="tutorial in getCategoryTutorials('configuration')"
              :key="tutorial.id"
              :tutorial="tutorial"
              @click="openTutorial(tutorial)"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="❓ 常见问题" name="faq">
          <FAQSection :faq="tutorials.faq" />
        </el-tab-pane>

        <el-tab-pane label="📺 视频教程" name="videos">
          <VideoSection />
        </el-tab-pane>

        <el-tab-pane label="💬 社区支持" name="community">
          <CommunitySection />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 教程详情对话框 -->
    <el-dialog
      v-model="tutorialDialogVisible"
      :title="currentTutorial?.title"
      width="900px"
      top="5vh"
      class="tutorial-dialog"
    >
      <TutorialViewer
        v-if="currentTutorial"
        :tutorial="currentTutorial"
        @close="tutorialDialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { tutorials, searchTutorials, getTutorialsByCategory } from '@/data/tutorials'
import TutorialCard from '@/components/help/TutorialCard.vue'
import TutorialViewer from '@/components/help/TutorialViewer.vue'
import FAQSection from '@/components/help/FAQSection.vue'
import VideoSection from '@/components/help/VideoSection.vue'
import CommunitySection from '@/components/help/CommunitySection.vue'

const activeCategory = ref('getting-started')
const searchKeyword = ref('')
const searchResults = ref([])
const tutorialDialogVisible = ref(false)
const currentTutorial = ref(null)

const getCategoryTutorials = (category) => {
  return getTutorialsByCategory(category)
}

const handleCategoryChange = (category) => {
  console.log('切换分类:', category)
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    searchResults.value = searchTutorials(searchKeyword.value)
  } else {
    searchResults.value = []
  }
}

const openTutorial = (tutorial) => {
  currentTutorial.value = tutorial
  tutorialDialogVisible.value = true
}
</script>

<style scoped>
.help-center {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.search-section {
  margin-bottom: 30px;
}

.search-section :deep(.el-input__wrapper) {
  border-radius: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.search-results {
  margin-top: 30px;
}

.search-results h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
}

.tutorial-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.categories :deep(.el-tabs__header) {
  background: white;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.tutorial-dialog :deep(.el-dialog__body) {
  padding: 30px;
  max-height: 70vh;
  overflow-y: auto;
}
</style>
