<template>
  <div class="result-display">
    <!-- 进度条 -->
    <div class="progress-section" v-if="isLoading || (steps.length > 0 && !planJson)">
      <div class="progress-bar-wrap">
        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
      </div>
      <div class="progress-text">
        <span v-if="!planJson">🤔 AI正在规划中...</span>
        <span v-else>✅ 规划完成</span>
        <span class="progress-steps">{{ completedSteps }}/{{ totalSteps }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  steps: Array,
  planJson: Object,
  isLoading: Boolean,
})

const completedSteps = computed(() => {
  return props.steps?.filter(s => s.status === 'done').length || 0
})

const totalSteps = computed(() => {
  // 动态计算：排除 system 步骤
  return props.steps?.filter(s => s.agent !== 'system').length || 1
})

const progress = computed(() => {
  if (totalSteps.value === 0) return 0
  return Math.min(Math.round((completedSteps.value / totalSteps.value) * 100), 100)
})
</script>

<style scoped>
.result-display {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.progress-section { margin-bottom: 0; }
.progress-bar-wrap {
  width: 100%; height: 8px;
  background: #e8e8e8; border-radius: 4px; overflow: hidden;
}
.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #1a73e8, #4285f4);
  border-radius: 4px; transition: width 0.3s ease;
}
.progress-text {
  display: flex; justify-content: space-between;
  margin-top: 8px; font-size: 0.85rem; color: #666;
}
.progress-steps { color: #999; font-size: 0.8rem; }
</style>