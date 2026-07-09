<template>
  <div class="app-layout">
    <!-- 左侧会话栏 -->
    <SessionSidebar />

    <!-- 右侧内容 -->
    <div class="main-content">
      <header class="page-header">
        <h1>🌍 智能旅游规划助手</h1>
        <p>输入您的旅行需求，AI为您生成个性化行程方案</p>
      </header>

      <div class="form-section">
        <TravelForm @submit="handleSubmit" :is-loading="active?.isLoading || false" />
      </div>

      <div class="top-section" v-if="active && (active.steps.length > 0 || active.planJson)">
        <ResultDisplay :steps="active.steps" :plan-json="active.planJson" :is-loading="active.isLoading" />
      </div>

      <div class="export-row" v-if="active?.planJson">
        <ExportButton />
      </div>

      <div v-if="active?.planJson">
        <TripOverview :plan-json="active.planJson" class="plan-content-area" />

        <div class="split-section">
          <div class="split-left">
            <h3>📅 每日行程 ({{ active.planJson.days?.length || 0 }}天)</h3>
            <div class="days-list">
              <DayCard
                v-for="(day, i) in active.planJson.days"
                :key="i" :day="day" :weather="active.planJson.weather_info?.[i]"
                :highlight="activeDay === i" :unsplash-images="active.unsplashImages"
                @click="activeDay = i"
              />
            </div>
          </div>
          <div class="split-right">
            <MapView
              :hotels="active.mapData.hotels"
              :highlight-day="activeDay" :plan-days="active.planJson?.days"
              @update:highlightDay="activeDay = $event"
            />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useTravelStore } from '../stores/travel'
import SessionSidebar from '../components/SessionSidebar.vue'
import TravelForm from '../components/TravelForm.vue'
import ResultDisplay from '../components/ResultDisplay.vue'
import TripOverview from '../components/TripOverview.vue'
import DayCard from '../components/DayCard.vue'
import MapView from '../components/MapView.vue'
import ExportButton from '../components/ExportButton.vue'

const store = useTravelStore()
const active = computed(() => store.active())
const activeDay = ref(-1)

function handleSubmit(formData) {
  activeDay.value = -1
  store.startPlanning(formData)
}

</script>

<style scoped>
.app-layout {
  display: flex; min-height: 100vh;
  max-width: 1400px; margin: 0 auto;
  border-radius: 14px; overflow: hidden;
  box-shadow: 0 0 0 1px #e5e7eb, 0 4px 24px rgba(0,0,0,0.06);
  background: #fff;
}
.main-content { flex: 1; min-width: 0; padding: 20px; max-width: 1200px; }

.page-header { text-align: center; padding: 20px 20px 10px; }
.page-header h1 { font-size: 2rem; color: #1a73e8; margin-bottom: 6px; }
.page-header p { color: #666; font-size: 1rem; }

.form-section { display: flex; justify-content: center; margin-bottom: 20px; }
.form-section :deep(.travel-form) { max-width: 600px; width: 100%; }

.top-section { margin-bottom: 20px; }
.export-row { display: flex; justify-content: flex-end; margin-bottom: 10px; }

.split-section { display: flex; gap: 20px; align-items: flex-start; margin-top: 16px; }
.split-left {
  flex: 1; min-width: 0; max-height: 650px; overflow-y: auto;
  background: #fff; border-radius: 12px; padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.split-left h3 { margin-bottom: 14px; font-size: 1rem; color: #333; }
.split-right { flex: 1; min-width: 0; }
.days-list { display: flex; flex-direction: column; gap: 8px; }
.split-left::-webkit-scrollbar { width: 6px; }
.split-left::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
</style>