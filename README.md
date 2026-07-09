# 🌍 多Agent智能旅游规划助手

基于 **LangGraph 多Agent协作** 的智能旅游规划Web应用。输入目的地和偏好，5个AI Agent自动完成景点搜索、天气查询、酒店推荐、Unsplash配图和ReAct两阶段方案生成，支持地图联动、多会话对比、方案导出。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 5 Agent协作 | 景点搜索/天气查询/酒店推荐/Unsplash配图/ReAct两阶段规划 |
| 📡 MCP协议 | 高德API封装为MCP Server(FastMCP+stdio)，Agent共享单例连接池 |
| 🖼 Unsplash配图 | LLM翻译中文景点名→英文检索→实景照片，骨架屏加载 |
| 🗺 地图联动 | 高德JS API 2.0原生集成，多日路线分区着色，卡片↔地图双向联动 |
| 💬 多会话管理 | 左侧栏会话列表，新建/切换/删除，localStorage持久化 |
| 📥 方案导出 | html2canvas一键导出PNG完整方案图 |
| 🔄 三级重试 | Agent节点(LangGraph RetryPolicy) + API调用(退避重试) + LLM(max_retries) |
| 🏷 偏好标签 | 8种预设标签（自然风光/美食/亲子等），一键多选 |
| 🌐 多LLM兼容 | OpenAI兼容接口，支持百炼/智谱/DeepSeek热切换 |
| 🧠 ReAct推理 | 协调Agent两阶段：先分析5维度→再精准生成JSON方案 |
| 💡 LLM旅行贴士 | 每个景点自动生成1-2条实用贴士（时段/注意事项/特色推荐） |

---

## 🏗 技术架构

| 层面 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| AI编排 | LangGraph (StateGraph + 条件路由 + RetryPolicy) |
| LLM | 百炼通义千问 (qwen-turbo)，兼容智谱/DeepSeek |
| 工具协议 | MCP (Model Context Protocol) + FastMCP |
| 地图API | 高德 Web服务API + JS API 2.0 |
| 图片API | Unsplash API |
| 前端框架 | Vue 3 + Vite + Pinia |
| 数据流 | SSE 流式推送 (StreamingResponse) |

---

## 🤖 Agent工作流

```
START → 景点搜索 + 天气查询 + 酒店推荐  [3子Agent并行，直调MCP工具]
    ↓
ReAct阶段1: 分析(analyze) → LLM分析景点距离/天气/路线/住宿/交通5维度
    ↓
Unsplash配图 → LLM翻译景点名→英文检索→URL去重
    ↓
ReAct阶段2: 生成(synthesize) → 基于分析结果生成JSON方案 + 距离排序酒店
    ↓
SSE流式推送 → 前端渲染
```

| Agent | 职责 | 数据源 |
|-------|------|--------|
| 📍 景点搜索 | 搜索目的地热门景点，零LLM开销 | 高德 POI 搜索 |
| 🌤 天气查询 | 查询出行期间天气预报，零LLM开销 | 高德 天气查询 |
| 🏨 酒店推荐 | 搜索住宿，后续由协调Agent按景点距离排序 | 高德 POI 搜索 |
| 🖼 Unsplash配图 | LLM翻译中文景点名→英文检索→匹配实景照片 | Unsplash API |
| 🧠 规划协调 | ReAct两阶段：分析5维度→生成JSON方案+旅行贴士 | LLM (qwen-turbo) |

---

## 🚀 快速开始

### 1. 配置 API Key

复制 `backend/.env.example` 为 `backend/.env`，填入你的 Key：

```env
# LLM API（OpenAI兼容接口）
LLM_API_KEY=你的API密钥
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo

# Unsplash图片API（可选，不填则无配图）
UNSPLASH_ACCESS_KEY=

# 高德地图 Web服务API（后端调用，https://console.amap.com）
AMAP_API_KEY=你的高德Web服务Key
```

编辑 `frontend/.env`（参考 `.env.example`）：
```env
VITE_AMAP_KEY=你的高德JS API Key
VITE_AMAP_SECURITY_KEY=你的高德安全密钥
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问

浏览器打开 http://localhost:5173

---

## 📁 项目结构

```
backend/
├── app/
│   ├── main.py                    # FastAPI入口 + lifespan(MCP初始化)
│   ├── api/routes/travel.py       # SSE流式规划接口
│   ├── core/
│   │   ├── config.py              # Pydantic Settings配置管理
│   │   ├── mcp_server.py          # MCP Server(高德3工具+FastMCP)
│   │   └── mcp_client.py          # 共享MCP客户端(单例管理)
│   ├── agents/
│   │   ├── state.py               # LangGraph状态Schema
│   │   ├── graph.py               # 工作流图(并行DAG+重试)
│   │   ├── coordinator.py         # 规划协调Agent(ReAct两阶段)
│   │   ├── attraction.py          # 景点搜索Agent(直调MCP)
│   │   ├── weather.py             # 天气查询Agent(直调MCP)
│   │   ├── hotel.py               # 酒店推荐Agent(直调MCP)
│   │   └── unsplash.py            # Unsplash图片搜索Agent(LLM翻译+API)
│   └── schemas/request.py         # API Pydantic数据模型
├── .env.example                   # 环境变量模板
└── requirements.txt

frontend/
├── src/
│   ├── App.vue
│   ├── main.js
│   ├── views/TravelPlan.vue       # 主页面(侧栏+表单+结果+地图)
│   ├── components/
│   │   ├── TravelForm.vue         # 表单(偏好标签组+预设计标签)
│   │   ├── ResultDisplay.vue      # 进度条(百分比+完成数)
│   │   ├── TripOverview.vue       # 蓝色概览卡片(预算/天气/建议)
│   │   ├── DayCard.vue            # 每日行程卡片(可折叠展开)
│   │   ├── MapView.vue            # 高德地图(路线标记+联动+自动定位)
│   │   ├── SpotImage.vue          # 景点缩略图(骨架屏+加载失败降级)
│   │   ├── SessionSidebar.vue     # 会话侧栏(当前/历史分组)
│   │   ├── ExportButton.vue       # 方案PNG导出(html2canvas)
│   │   └── AgentStep.vue          # Agent步骤卡片(状态/数据展示)
│   ├── stores/travel.js           # Pinia多会话管理+localStorage
│   └── api/travel.js              # SSE客户端(fetch+ReadableStream)
├── .env.example
├── package.json
└── vite.config.js
```
