<template>
  <div class="travel-form">
    <h2>✈️ 填写旅行需求</h2>
    <form @submit.prevent="onSubmit">
      <div class="form-group">
        <label for="destination">目的地城市</label>
        <input
          id="destination"
          v-model="form.destination"
          type="text"
          placeholder="如：成都、杭州、丽江"
          required
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="startDate">出发日期</label>
          <input
            id="startDate"
            v-model="form.start_date"
            type="date"
            required
          />
        </div>
        <div class="form-group">
          <label for="endDate">返回日期</label>
          <input
            id="endDate"
            v-model="form.end_date"
            type="date"
            required
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="budget">预算（元）</label>
          <input
            id="budget"
            v-model.number="form.budget"
            type="number"
            placeholder="如：5000"
          />
        </div>
        <div class="form-group">
          <label>旅行偏好（可多选）</label>
          <div class="tag-group">
            <span v-for="t in tags" :key="t" :class="['tag', { active: selectedTags.includes(t) }]"
                  @click="toggleTag(t)">{{ tagIcon(t) }} {{ t }}</span>
          </div>
          <input v-if="selectedTags.includes('自定义')" v-model="customPref"
                 type="text" placeholder="输入自定义偏好..." class="custom-input" />
        </div>
      </div>

      <button type="submit" class="submit-btn" :disabled="isLoading">
        <span v-if="isLoading">🤔 AI正在思考...</span>
        <span v-else>🚀 开始规划</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const props = defineProps({ isLoading: Boolean })
const emit = defineEmits(['submit'])

const tags = ['自然风光', '美食', '历史文化', '亲子', '蜜月', '徒步', '打卡拍照', '休闲度假', '自定义']
const selectedTags = ref([])
const customPref = ref('')

const form = reactive({
  destination: '', start_date: '', end_date: '', budget: null, preferences: '',
})

function toggleTag(t) {
  const i = selectedTags.value.indexOf(t)
  if (i >= 0) selectedTags.value.splice(i, 1)
  else selectedTags.value.push(t)
  // 构建 preferences 字符串
  const parts = selectedTags.value.filter(x => x !== '自定义')
  if (selectedTags.value.includes('自定义') && customPref.value) parts.push(customPref.value)
  form.preferences = parts.join('、')
}

function tagIcon(t) {
  const map = { '自然风光': '🏕', '美食': '🍜', '历史文化': '🏛', '亲子': '👶', '蜜月': '💑', '徒步': '🚶', '打卡拍照': '📸', '休闲度假': '🏖', '自定义': '✏️' }
  return map[t] || ''
}

function onSubmit() {
  emit('submit', { ...form })
  // 延迟清空——等规划开始后再重置（避免提交失败时丢失输入）
  setTimeout(() => {
    form.destination = ''; form.start_date = ''; form.end_date = ''
    form.budget = null; form.preferences = ''
    selectedTags.value = []; customPref.value = ''
  }, 2000)
}
</script>

<style scoped>
.travel-form {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.travel-form h2 {
  font-size: 1.3rem;
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 6px;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #1a73e8;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: #1a73e8;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #1557b0;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.tag-group {
  display: flex; flex-wrap: wrap; gap: 8px;
}
.tag {
  padding: 6px 12px; border-radius: 16px; border: 1px solid #ddd;
  font-size: 0.85rem; cursor: pointer; user-select: none;
  transition: all 0.15s; background: #fafafa;
}
.tag:hover { border-color: #1a73e8; }
.tag.active {
  background: #e8f0fe; border-color: #1a73e8; color: #1a73e8; font-weight: 600;
}
.custom-input {
  margin-top: 8px;
}
</style>
