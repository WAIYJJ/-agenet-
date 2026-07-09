// 开发环境直连后端，生产环境用相对路径
const API_BASE = 'http://localhost:8000/api/travel'

export async function submitTravelPlan(formData, handlers) {
  const response = await fetch(`${API_BASE}/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData),
  })

  if (!response.ok) {
    const text = await response.text()
    handlers.onError?.({ message: `HTTP ${response.status}: ${text}` })
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const d = line.slice(6).trim()
        if (d === '[DONE]') { handlers.onDone?.(); return }
        try {
          const evt = JSON.parse(d)
          handleEvent(evt, handlers)
        } catch(e) {
          // 非JSON行忽略
        }
      }
    }
  }
  handlers.onDone?.()
}

function handleEvent(evt, handlers) {
  switch (evt.event_type) {
    case 'coordinator_thinking':
      handlers.onCoordinatorThinking?.(evt.data.content || '')
      break
    case 'agent_start':
      handlers.onAgentStart?.(evt.data.agent)
      break
    case 'agent_tool_call':
      handlers.onAgentToolCall?.(evt.data.tool, evt.data.args)
      break
    case 'agent_result':
      handlers.onAgentResult?.(evt.data.agent, evt.data.data)
      break
    case 'plan_complete':
      console.log('plan_complete received:', JSON.stringify(evt.data).slice(0, 300))
      handlers.onPlanComplete?.(evt.data)
      break
    case 'error':
      // 后端详细错误信息
      handlers.onError?.(evt.data)
      break
  }
}