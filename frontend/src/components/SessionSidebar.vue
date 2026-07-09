<template>
  <div class="sidebar">
    <!-- 新规划按钮 -->
    <button class="new-btn" @click="store.newSession()">
      <span class="new-icon">＋</span> 新建规划
    </button>

    <!-- 当前会话（最近一个） -->
    <div class="section" v-if="recent">
      <div class="section-title">当前规划</div>
      <div :class="['item', 'current', { active: store.activeId === recent.id }]"
           @click="store.switchSession(recent.id)">
        <span class="dot"></span>
        <div class="info">
          <div class="name">{{ recent.name || '新规划' }}</div>
          <div class="sub">{{ recent.formData?.start_date || '' }} {{ recent.formData?.end_date || '' }}</div>
        </div>
        <span class="del" v-if="sessions.length > 1" @click.stop="store.deleteSession(recent.id)">🗑</span>
      </div>
    </div>

    <!-- 历史会话 -->
    <div class="section" v-if="history.length">
      <div class="section-title">历史规划</div>
      <div
        v-for="s in history" :key="s.id"
        :class="['item', { active: store.activeId === s.id }]"
        @click="store.switchSession(s.id)"
      >
        <div class="info">
          <div class="name">{{ s.name || '未命名' }}</div>
          <div class="sub">{{ s.formData?.start_date || '' }} {{ s.formData?.end_date || '' }}</div>
        </div>
        <span class="del" @click.stop="store.deleteSession(s.id)">🗑</span>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty" v-if="!sessions.length">
      <p>暂无规划</p>
      <p class="hint">点击上方按钮创建</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTravelStore } from '../stores/travel'
const store = useTravelStore()
store.ensureActive()

const sessions = computed(() => store.sessions)
const recent = computed(() => sessions.value[0] || null)
const history = computed(() => sessions.value.slice(1))
</script>

<style scoped>
.sidebar {
  width: 240px; min-height: 100vh;
  background: #f9fafb; border-right: 1px solid #e5e7eb;
  display: flex; flex-direction: column; flex-shrink: 0;
  user-select: none;
}

/* 新建按钮 */
.new-btn {
  margin: 14px 12px 8px; padding: 10px 0;
  background: #fff; color: #1a73e8; border: 1px solid #d2e3fc;
  border-radius: 10px; cursor: pointer;
  font-size: 0.88rem; font-weight: 600;
  transition: all 0.15s;
  display: flex; align-items: center; justify-content: center; gap: 4px;
}
.new-btn:hover { background: #e8f0fe; box-shadow: 0 1px 4px rgba(26,115,232,0.15); }
.new-icon { font-size: 1.1rem; font-weight: 300; }

/* 分区 */
.section { padding: 6px 10px; }
.section-title {
  font-size: 0.72rem; color: #999; font-weight: 600;
  padding: 8px 6px 6px; text-transform: uppercase; letter-spacing: 0.5px;
}

/* 会话项 */
.item {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 10px; border-radius: 8px;
  cursor: pointer; transition: background 0.12s; margin-bottom: 2px;
  position: relative;
}
.item:hover { background: #e8eaed; }
.item.active { background: #e8f0fe; }
.item.active .name { color: #1a73e8; }

/* 当前会话特殊样式 */
.item.current {
  background: #fff; border: 1px solid #d2e3fc;
}
.item.current:hover { background: #f5f8ff; }
.item.current.active { background: #e8f0fe; border-color: #1a73e8; }

.dot {
  width: 7px; height: 7px; border-radius: 50%; background: #1a73e8;
  flex-shrink: 0;
}

.info { flex: 1; min-width: 0; }
.name {
  font-size: 0.84rem; font-weight: 500; color: #333;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.sub {
  font-size: 0.72rem; color: #aaa; margin-top: 1px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.del {
  font-size: 0.75rem; opacity: 0;
  transition: opacity 0.15s; cursor: pointer; flex-shrink: 0;
}
.item:hover .del { opacity: 0.5; }
.del:hover { opacity: 1 !important; }

.empty {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: #bbb; font-size: 0.85rem;
}
.empty .hint { font-size: 0.75rem; margin-top: 4px; color: #ccc; }
</style>