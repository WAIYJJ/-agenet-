<template>
  <div :class="['day-card', { open: isOpen, highlight: highlight }]" @click="isOpen = !isOpen">
    <!-- 表头行（始终显示） -->
    <div class="day-header">
      <span class="day-badge">第{{ day.day_index + 1 }}天</span>
      <div class="day-info">
        <span class="day-date">{{ day.date }}</span>
        <span class="day-weather" v-if="w">{{ w.day_weather }} {{ w.day_temp }}°~{{ w.night_temp }}°</span>
      </div>
      <p class="day-desc">{{ day.description }}</p>
      <span class="arrow">{{ isOpen ? '▲' : '▼' }}</span>
    </div>

    <!-- 展开详情（点击后显示） -->
    <div class="day-body" v-if="isOpen" @click.stop>
      <!-- 景点 -->
      <div class="block" v-if="day.attractions?.length">
        <h4>📍 游览景点</h4>
        <div class="item" v-for="(a, i) in day.attractions" :key="i">
          <strong>{{ a.name }}</strong>
          <span v-if="a.ticket_price !== undefined"> · 🎫 {{ a.ticket_price === 0 ? '免费' : '¥' + a.ticket_price }}</span>
          <span v-if="a.visit_duration"> · ⏱ {{ a.visit_duration }}分钟</span>
          <div class="sub" v-if="a.address">🏠 {{ a.address }}</div>
          <div class="sub" v-if="a.description">{{ a.description }}</div>
          <SpotImage v-if="getImage(a.name)" :image-url="getImage(a.name).image_url"
                     :name="a.name" :photographer="getImage(a.name).photographer" />
        </div>
      </div>

      <!-- 餐饮 -->
      <div class="block" v-if="day.meals?.length">
        <h4>🍽 推荐餐饮</h4>
        <div class="item" v-for="(m, i) in day.meals" :key="i">
          <strong>{{ mealIcon(m.type) }} {{ m.name }}</strong>
          <span v-if="m.estimated_cost"> · ¥{{ m.estimated_cost }}</span>
          <div class="sub" v-if="m.description">{{ m.description }}</div>
        </div>
      </div>

      <!-- 酒店 -->
      <div class="block" v-if="day.hotel?.name && day.hotel.name !== '无'">
        <h4>🏨 住宿</h4>
        <div class="item">
          <strong>{{ day.hotel.name }}</strong>
          <span v-if="day.hotel.rating"> · ⭐{{ day.hotel.rating }}</span>
          <span v-if="day.hotel.price_range"> · 💰{{ day.hotel.price_range }}</span>
          <div class="sub" v-if="day.hotel.address">{{ day.hotel.address }}</div>
          <div class="sub" v-if="day.hotel.distance">{{ day.hotel.distance }}</div>
        </div>
      </div>

      <!-- 交通 -->
      <div class="block transport" v-if="day.transportation">
        🚗 {{ day.transportation }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({ day: Object, weather: Object, highlight: Boolean, unsplashImages: Array })
const w = props.weather
const isOpen = ref(false)

import SpotImage from './SpotImage.vue'

function mealIcon(t) {
  return { breakfast: '🥐', lunch: '🍱', dinner: '🍲' }[t] || '🍽'
}

function getImage(name) {
  if (!name) return null
  return (props.unsplashImages || []).find(i => {
    const iname = i.name || ''
    // 双向包含匹配：如"宽窄巷子"匹配"宽窄巷子历史文化街区"
    return iname.includes(name) || name.includes(iname)
  })
}
</script>

<style scoped>
.day-card {
  background: #fff; border-radius: 10px; border: 1px solid #e8e8e8;
  padding: 14px 16px; margin-bottom: 8px;
  cursor: pointer; transition: all 0.15s;
}
.day-card:hover { border-color: #1a73e8; }
.day-card.open { border-color: #1a73e8; box-shadow: 0 2px 8px rgba(26,115,232,0.1); }
.day-card.highlight { border-color: #ea4335; box-shadow: 0 2px 8px rgba(234,67,53,0.15); background: #fef7f6; }

.day-header {
  display: flex; align-items: flex-start; gap: 10px; flex-wrap: wrap;
}
.day-badge {
  background: #1a73e8; color: #fff; padding: 2px 10px;
  border-radius: 10px; font-weight: 700; font-size: 0.8rem;
  flex-shrink: 0; margin-top: 1px;
}
.day-info { display: flex; flex-direction: column; gap: 2px; }
.day-date { font-weight: 600; font-size: 0.9rem; color: #333; }
.day-weather { font-size: 0.78rem; color: #e67e22; }
.day-desc { font-size: 0.85rem; color: #666; flex: 1; min-width: 200px; margin: 0; }
.arrow { color: #999; font-size: 0.7rem; margin-left: auto; flex-shrink: 0; margin-top: 4px; }

/* 展开区域 */
.day-body {
  margin-top: 12px; padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}
.block { margin-top: 10px; }
.block h4 { font-size: 0.88rem; color: #333; margin-bottom: 6px; }

.item {
  background: #f9fafb; border-radius: 6px; padding: 7px 10px;
  margin-bottom: 4px; font-size: 0.83rem;
}
.sub { font-size: 0.76rem; color: #999; margin-top: 2px; }

.transport {
  font-size: 0.83rem; color: #555;
  background: #f0f7ff; padding: 7px 10px; border-radius: 6px;
}
</style>