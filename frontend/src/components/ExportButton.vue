<template>
  <button class="export-btn" @click="doExport" :disabled="exporting">
    <span v-if="exporting">⏳ 导出中...</span>
    <span v-else>📥 导出方案图片</span>
  </button>
</template>

<script setup>
import { ref } from 'vue'

const exporting = ref(false)

async function doExport() {
  exporting.value = true
  try {
    // 点击未展开的DayCard使其展开
    const dayCards = document.querySelectorAll('.split-left .day-card')
    const toRestore = []
    dayCards.forEach(card => {
      if (!card.classList.contains('open')) {
        card.click()
        toRestore.push(card)
      }
    })
    await new Promise(r => setTimeout(r, 200))

    // 构建临时导出容器（无高度限制）
    const overview = document.querySelector('.plan-content-area')
    const left = document.querySelector('.split-left')
    if (!overview || !left) { exporting.value = false; return }

    const wrapper = document.createElement('div')
    wrapper.style.cssText = 'position:fixed;left:-9999px;top:0;width:800px;background:#f5f7fa;padding:16px;z-index:-1'
    const ovClone = overview.cloneNode(true)
    const lClone = left.cloneNode(true)
    // 移除高度限制，让内容完全展开
    lClone.style.cssText = 'max-height:none;overflow:visible;height:auto'
    wrapper.appendChild(ovClone)
    wrapper.appendChild(lClone)
    document.body.appendChild(wrapper)
    await new Promise(r => setTimeout(r, 100))

    const html2canvas = (await import('html2canvas')).default
    const canvas = await html2canvas(wrapper, {
      useCORS: true, scale: 2, backgroundColor: '#f5f7fa',
    })

    document.body.removeChild(wrapper)
    toRestore.forEach(card => card.click())

    const link = document.createElement('a')
    link.download = `旅行方案_${new Date().toISOString().slice(0, 10)}.png`
    link.href = canvas.toDataURL()
    link.click()
  } catch (e) {
    console.error('Export failed:', e)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.export-btn {
  padding: 8px 16px; background: #fff;
  border: 1px solid #1a73e8; border-radius: 8px;
  color: #1a73e8; font-size: 0.85rem; cursor: pointer;
  transition: all 0.15s;
}
.export-btn:hover:not(:disabled) { background: #e8f0fe; }
.export-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>