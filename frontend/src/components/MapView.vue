<template>
  <div class="map-view">
    <div class="map-header">🗺 地图</div>
    <div ref="mapContainer" class="amap-container">
      <div v-if="loadError" class="map-error">⚠️ 地图加载失败，请检查JS API Key</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  hotels: { type: Array, default: () => [] },
  highlightDay: { type: Number, default: -1 },
  planDays: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:highlightDay'])
const mapContainer = ref(null)
const loadError = ref(false)
const COLORS = ['#1a73e8','#ea4335','#34a853','#fbbc04','#ff6d01','#8e24aa']
let map = null
let overlays = []

onMounted(() => {
  if (window.AMap) return initMap()
  const key = import.meta.env.VITE_AMAP_KEY
  const sec = import.meta.env.VITE_AMAP_SECURITY_KEY || ''
  const s = document.createElement('script')
  s.src = `https://webapi.amap.com/maps?v=2.0&key=${key}&securityJsCode=${sec}`
  s.onload = initMap
  s.onerror = () => { loadError.value = true }
  document.head.appendChild(s)
})

function initMap() {
  if (!mapContainer.value || !window.AMap) return
  map = new window.AMap.Map(mapContainer.value, {
    center: [116, 39], zoom: 12, resizeEnable: true,
  })
  drawAll()
}

function clearAll() {
  overlays.forEach(o => { try { o.setMap?.(null) } catch {} })
  overlays = []
}

function drawAll() {
  if (!map) return
  clearAll()
  if (!props.planDays?.length) return

  let allSpots = []
  props.planDays.forEach((day, di) => {
    const spots = (day.attractions || [])
      .filter(a => a.location?.longitude && a.location?.latitude)
      .map(a => ({ name: a.name, lng: a.location.longitude, lat: a.location.latitude, day: di }))
    if (!spots.length) return
    allSpots.push(...spots)

    const color = COLORS[di % COLORS.length]
    const active = props.highlightDay < 0 || props.highlightDay === di

    // 路线
    if (spots.length > 1) {
      overlays.push(new window.AMap.Polyline({
        path: spots.map(s => [s.lng, s.lat]),
        strokeColor: color, strokeWeight: active ? 4 : 2,
        strokeOpacity: active ? 0.85 : 0.15, map,
      }))
    }

    // 标记
    spots.forEach(s => {
      const m = new window.AMap.Marker({
        position: [s.lng, s.lat], map, zIndex: 10,
        label: { content: s.name, direction: 'top', offset: [0, -12] },
      })
      m.on('click', () => {
        emit('update:highlightDay', s.day)
        new window.AMap.InfoWindow({ content: `<b>第${s.day+1}天 · ${s.name}</b>` })
          .open(map, [s.lng, s.lat])
      })
      overlays.push(m)
    })
  })

  // 酒店标记（默认蓝色水滴）
  props.hotels?.forEach(h => {
    if (!h.lng || !h.lat) return
    const m = new window.AMap.Marker({ position: [h.lng, h.lat], map, zIndex: 5 })
    m.on('click', () => new window.AMap.InfoWindow({
      content: `<b>${h.name}</b>${h.price ? '<br>¥'+h.price : ''}${h.rating ? '<br>⭐'+h.rating : ''}`,
    }).open(map, [h.lng, h.lat]))
    overlays.push(m)
  })

  if (allSpots.length) map.setFitView(null, false, [60, 60, 60, 300])
}

// 点击DayCard → 地图定位到该天第一个景点
watch(() => props.highlightDay, (di) => {
  if (!map || di < 0 || !props.planDays?.[di]) return
  const first = (props.planDays[di].attractions || [])
    .find(a => a.location?.longitude)
  if (first) {
    map.setCenter([first.location.longitude, first.location.latitude])
    map.setZoom(15)
  }
  drawAll()
})

watch(() => [props.planDays, props.hotels], () => drawAll(), { deep: true })
</script>

<style scoped>
.map-view {
  border-radius: 12px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  position: sticky; top: 20px;
}
.map-header {
  background: #1a73e8; color: #fff;
  padding: 10px 16px; font-size: 0.95rem; font-weight: 600;
}
.amap-container { width: 100%; height: 600px; position: relative; }
.map-error {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: #fef2f2; color: #b91c1c; font-size: 0.9rem;
}
</style>