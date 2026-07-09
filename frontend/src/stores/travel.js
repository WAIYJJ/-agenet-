import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { submitTravelPlan } from '../api/travel'

const STORAGE_KEY = 'travel_sessions'
const AGENT_NAME_MAP = {
  'coordinator_analyze': 'coordinator', 'coordinator_synthesize': 'coordinator',
  'attraction_agent': 'attraction', 'weather_agent': 'weather', 'hotel_agent': 'hotel',
}

function loadSessions() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [] } catch { return [] }
}
function saveSessions(sessions) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
}

export const useTravelStore = defineStore('travel', () => {
  const sessions = ref(loadSessions())
  const activeId = ref(sessions.value[0]?.id || null)

  function active() { return sessions.value.find(s => s.id === activeId.value) }

  function ensureActive() {
    if (!active()) {
      const s = { id: Date.now().toString(36), name: '', formData: {},
                  planJson: null, mapData: { attractions: [], hotels: [] },
                  steps: [], isLoading: false, planText: '', createdAt: Date.now() }
      sessions.value.unshift(s)
      activeId.value = s.id
    }
  }

  function newSession() {
    const s = { id: Date.now().toString(36), name: '', formData: {},
                planJson: null, mapData: { attractions: [], hotels: [] },
                steps: [], isLoading: false, planText: '', createdAt: Date.now() }
    sessions.value.unshift(s)
    activeId.value = s.id
  }

  function switchSession(id) { activeId.value = id }

  function deleteSession(id) {
    const idx = sessions.value.findIndex(s => s.id === id)
    if (idx < 0) return
    sessions.value.splice(idx, 1)
    if (activeId.value === id) activeId.value = sessions.value[0]?.id || null
    if (!sessions.value.length) newSession()
  }

  async function startPlanning(formData) {
    ensureActive()
    const s = active()
    if (!s) return

    s.name = formData.destination || '未命名'
    s.formData = { ...formData }
    s.isLoading = true
    s.steps = [{ agent: 'system', status: 'running', content: '正在连接 AI 服务...', data: null }]
    s.planJson = null
    s.planText = ''
    s.mapData = { attractions: [], hotels: [] }
    s.unsplashImages = []

    try {
      await submitTravelPlan(formData, {
        onCoordinatorThinking: (content) => {
          const si = s.steps.findIndex(st => st.agent === 'system')
          if (si >= 0) s.steps.splice(si, 1)
          const ex = s.steps.find(st => st.agent === 'coordinator' && st.status === 'running')
          if (ex) ex.content += content
          else s.steps.push({ agent: 'coordinator', status: 'running', content, data: null })
        },
        onAgentStart: (agent) => {
          const si = s.steps.findIndex(st => st.agent === 'system')
          if (si >= 0) s.steps.splice(si, 1)
          s.steps.push({ agent: AGENT_NAME_MAP[agent] || agent, status: 'running', content: '正在处理...', data: null })
        },
        onAgentToolCall: (tool) => {
          const step = s.steps.find(st => st.status === 'running' && st.agent !== 'coordinator')
          if (step) step.content = `调用工具: ${tool}`
        },
        onAgentResult: (agent, data) => {
          const d = AGENT_NAME_MAP[agent] || agent
          const step = s.steps.find(st => st.agent === d && st.status === 'running')
          if (step) { step.status = 'done'; step.data = data; step.content = '已完成' }
          if (d === 'attraction') s.mapData.attractions = data
          if (d === 'hotel') s.mapData.hotels = data
        },
        onPlanComplete: (planData) => {
          s.planText = planData.plan || ''
          let pj = planData.plan_json
          if (!pj || Object.keys(pj).length === 0) {
            const m = (planData.plan || '').match(/```json\s*([\s\S]*?)\s*```/)
            if (m) { try { pj = JSON.parse(m[1]) } catch {} }
          }
          if (pj && !pj.days && !pj.raw_text) pj = null
          s.planJson = pj
          if (planData.attractions?.length) s.mapData.attractions = planData.attractions
          if (planData.hotels?.length) s.mapData.hotels = planData.hotels
          s.unsplashImages = planData.unsplash_images || []
          s.steps.forEach(st => { if (st.status === 'running') st.status = 'done' })
        },
        onError: (errData) => {
          s.steps.push({ agent: 'system', status: 'error', content: errData.message || '未知错误', data: errData })
        },
        onDone: () => { s.isLoading = false },
      })
    } catch (err) {
      s.isLoading = false
      s.steps.push({ agent: 'system', status: 'error', content: err.message || '请求失败', data: null })
    }
  }

  watch(sessions, (v) => saveSessions(v), { deep: true })

  return { sessions, activeId, active, newSession, switchSession, deleteSession, startPlanning, ensureActive }
})