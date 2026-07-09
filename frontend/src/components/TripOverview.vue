<template>
  <div class="trip-overview" v-if="planJson">
    <!-- 城市日期概览 -->
    <div class="overview-header">
      <div class="city-info">
        <h2>🏙 {{ planJson.city || '旅行' }}</h2>
        <p>{{ planJson.start_date }} → {{ planJson.end_date }} · {{ planJson.days?.length || 0 }}天</p>
      </div>
      <div class="total-budget" v-if="planJson.budget?.total">
        <span class="budget-label">预估总花费</span>
        <span class="budget-num">¥{{ planJson.budget.total.toLocaleString() }}</span>
      </div>
    </div>

    <!-- 预算明细 -->
    <div class="budget-row" v-if="planJson.budget">
      <div class="budget-item">🎫 景点 ¥{{ planJson.budget.total_attractions || 0 }}</div>
      <div class="budget-item">🏨 住宿 ¥{{ planJson.budget.total_hotels || 0 }}</div>
      <div class="budget-item">🍽 餐饮 ¥{{ planJson.budget.total_meals || 0 }}</div>
      <div class="budget-item">🚗 交通 ¥{{ planJson.budget.total_transportation || 0 }}</div>
    </div>

    <!-- 天气速览 -->
    <div class="weather-strip" v-if="planJson.weather_info?.length">
      <div v-for="w in planJson.weather_info" :key="w.date" class="weather-day">
        <div class="w-date">{{ shortDate(w.date) }}</div>
        <div class="w-icon">{{ w.day_weather }}</div>
        <div class="w-temp">{{ w.day_temp }}° / {{ w.night_temp }}°</div>
      </div>
    </div>

    <!-- 总体建议 -->
    <div class="suggestions" v-if="planJson.overall_suggestions">
      <h4>💡 旅行建议</h4>
      <p>{{ planJson.overall_suggestions }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({ planJson: Object })

function shortDate(dateStr) {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  return parts.length === 3 ? `${parts[1]}/${parts[2]}` : dateStr
}
</script>

<style scoped>
.trip-overview {
  background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
  color: #fff;
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 16px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.city-info h2 { font-size: 1.4rem; margin-bottom: 4px; }
.city-info p { font-size: 0.85rem; opacity: 0.85; }

.total-budget { text-align: right; }
.budget-label { display: block; font-size: 0.75rem; opacity: 0.8; }
.budget-num { font-size: 1.6rem; font-weight: 700; }

.budget-row {
  display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap;
}
.budget-item {
  background: rgba(255,255,255,0.18);
  padding: 6px 12px; border-radius: 6px; font-size: 0.8rem;
}

.weather-strip {
  display: flex; gap: 8px; margin-top: 16px; overflow-x: auto;
}
.weather-day {
  background: rgba(255,255,255,0.15);
  padding: 8px 12px; border-radius: 8px; text-align: center;
  min-width: 72px;
}
.w-date { font-size: 0.7rem; opacity: 0.8; }
.w-icon { font-size: 0.9rem; margin: 2px 0; }
.w-temp { font-size: 0.72rem; opacity: 0.9; }

.suggestions {
  margin-top: 16px; padding-top: 14px;
  border-top: 1px solid rgba(255,255,255,0.2);
}
.suggestions h4 { font-size: 0.9rem; margin-bottom: 6px; }
.suggestions p { font-size: 0.8rem; line-height: 1.5; opacity: 0.9; }
</style>