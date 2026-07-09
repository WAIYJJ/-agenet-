<template>
  <div class="spot-image" v-if="imageUrl">
    <!-- 加载骨架 -->
    <div class="skeleton" v-if="!loaded"></div>
    <!-- 真实图片 -->
    <img :src="imageUrl" :alt="name" crossorigin="anonymous"
         @load="loaded = true" @error="failed = true"
         :class="{ show: loaded, hide: failed }" />
    <div class="credit" v-if="photographer && loaded">📷 {{ photographer }}</div>
    <div class="credit" v-if="failed">⚠️ 图片加载失败</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
defineProps({ imageUrl: String, name: String, photographer: String })
const loaded = ref(false)
const failed = ref(false)
</script>

<style scoped>
.spot-image {
  margin: 6px 0; border-radius: 8px; overflow: hidden;
  max-width: 240px; min-height: 80px; position: relative;
}
.skeleton {
  width: 100%; height: 135px; background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 8px;
}
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
.spot-image img { width: 100%; display: block; opacity: 0; transition: opacity 0.3s; }
.spot-image img.show { opacity: 1; }
.spot-image img.hide { display: none; }
.credit {
  font-size: 0.65rem; color: #bbb; padding: 2px 6px; text-align: right;
}
</style>