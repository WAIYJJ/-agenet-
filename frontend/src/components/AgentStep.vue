<template>
  <div :class="['agent-step', `step-${step.status}`]">
    <div class="step-icon">
      <span v-if="step.status === 'running'">⏳</span>
      <span v-if="step.status === 'done'">✅</span>
      <span v-if="step.status === 'pending'">⏸</span>
      <span v-if="step.status === 'error'">❌</span>
    </div>
    <div class="step-content">
      <div class="step-header">
        <span class="step-agent">{{ agentLabel }}</span>
        <span :class="['step-status', step.status]">{{ statusLabel }}</span>
      </div>
      <div class="step-detail" v-if="step.content">
        <p>{{ step.content }}</p>
        <details v-if="step.data?.traceback" class="error-details">
          <summary>查看详细错误</summary>
          <pre>{{ step.data.traceback }}</pre>
        </details>
        <details v-if="step.data?.type" class="error-details">
          <summary>错误类型</summary>
          <pre>{{ step.data.type }}</pre>
        </details>
      </div>
      <div class="step-data" v-if="step.data && step.status === 'done'">
        <div v-if="step.agent === 'attraction'" class="data-list">
          <div v-for="item in step.data" :key="item.name" class="data-item">
            📍 {{ item.name }} <span class="data-rating">⭐ {{ item.rating || '-' }}</span>
          </div>
        </div>
        <div v-if="step.agent === 'weather'" class="weather-list">
          <div v-for="day in step.data.forecast" :key="day.date" class="weather-item">
            🌤 {{ day.date }}: {{ day.weather }} {{ day.temp_low }}°~{{ day.temp_high }}°
          </div>
        </div>
        <div v-if="step.agent === 'hotel'" class="data-list">
          <div v-for="item in step.data" :key="item.name" class="data-item">
            🏨 {{ item.name }} <span class="data-price">¥{{ item.price || '-' }}</span>
            <span class="data-rating">⭐ {{ item.rating || '-' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  step: Object,
})

const agentLabel = computed(() => {
  const map = {
    coordinator: '🧠 规划协调',
    attraction: '📍 景点搜索',
    weather: '🌤 天气查询',
    hotel: '🏨 酒店推荐',
    system: '🔔 系统',
  }
  return map[props.step.agent] || props.step.agent
})

const statusLabel = computed(() => {
  const map = {
    running: '进行中...',
    done: '已完成',
    pending: '等待中',
    error: '出错了',
  }
  return map[props.step.status] || props.step.status
})
</script>

<style scoped>
.agent-step {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  transition: all 0.3s;
}

.step-running {
  border-color: #1a73e8;
  background: #f0f7ff;
}

.step-done {
  border-color: #34a853;
  background: #f0fff4;
}

.step-error {
  border-color: #ea4335;
  background: #fce8e6;
}

.step-icon {
  font-size: 1.2rem;
}

.step-content {
  flex: 1;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.step-agent {
  font-weight: 600;
  font-size: 0.95rem;
}

.step-status {
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.step-status.running {
  color: #1a73e8;
  background: #e8f0fe;
}

.step-status.done {
  color: #34a853;
  background: #e8f5e9;
}

.step-status.error {
  color: #ea4335;
  background: #fce8e6;
}

.step-detail {
  color: #666;
  font-size: 0.85rem;
  margin-bottom: 8px;
}

.error-details {
  margin-top: 8px;
}

.error-details summary {
  cursor: pointer;
  color: #ea4335;
  font-weight: 600;
  font-size: 0.8rem;
}

.error-details pre {
  margin-top: 4px;
  padding: 8px;
  background: #fef2f2;
  border-radius: 4px;
  font-size: 0.7rem;
  color: #b91c1c;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

.data-list,
.weather-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.data-item,
.weather-item {
  font-size: 0.85rem;
  color: #555;
}

.data-rating,
.data-price {
  color: #999;
  margin-left: 8px;
}
</style>