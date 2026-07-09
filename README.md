# 🌍 多Agent智能旅游规划助手

基于 **LangGraph 多Agent协作** 的智能旅游规划Web应用。输入目的地和偏好，AI自动搜索景点、查询天气、推荐酒店，结合 **RAG知识库** 和 **Unsplash实景配图**，生成个性化行程方案，支持地图可视化、多会话对比、方案导出。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 多Agent协作 | 6个Agent：景点/天气/酒店/RAG知识库/图片搜索/规划协调 |
| 📡 MCP协议 | 共享MCP Server单例，工具协议标准化，统一API限流 |
| 📚 RAG知识增强 | TF-IDF向量检索 + 52条预置旅游攻略，为景点注入实用Tips |
| 🖼 Unsplash配图 | 自动搜索景点实景照片，展示在行程卡片中 |
| 🗺 地图联动 | 高德JS API 2.0原生集成，行程↔地图双向交互，多日路线分区着色 |
| 💬 多会话管理 | 左侧栏会话列表，支持新建/切换/删除，localStorage持久化 |
| 📥 方案导出 | 点击导出生成PNG完整方案图（概览+全部行程） |
| 🔄 智能重试 | Agent节点 + API调用 + LLM三级重试机制 |
| 🏷 偏好标签 | 8种预设标签（自然风光/美食/亲子等），一键多选 |
| 🌐 多LLM兼容 | OpenAI兼容接口，一键切换百炼/智谱/DeepSeek |

---

## 🏗 技术架构

| 层面 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| AI编排 | LangGraph (StateGraph + 条件路由 + 重试策略) |
| Agent推理 | LangChain (create_react_agent) |
| LLM | 百炼通义千问 (qwen-turbo)，兼容智谱/DeepSeek |
| 工具协议 | MCP (Model Context Protocol) + FastMCP |
| 向量检索 | scikit-learn TF-IDF + 余弦相似度 |
| 地图API | 高德 Web服务API + JS API 2.0 |
| 图片API | Unsplash API |
| 前端框架 | Vue 3 + Vite + Pinia |
| 数据流 | SSE 流式推送 (StreamingResponse) |

---

## 🤖 Agent架构

```
用户提交
    ↓
START → 景点搜索(高德POI) + 天气查询(高德天气) + 酒店推荐(高德POI)  [并行]
    ↓
RAG知识检索(TF-IDF) + Unsplash图片搜索  [并行]
    ↓
规划协调Agent (LLM汇总生成JSON方案 + 按景点距离排序酒店)
    ↓
SSE流式推送 → 前端渲染
```

| Agent | 职责 | 数据源 |
|-------|------|--------|
| 📍 景点搜索 | 搜索目的地热门景点 | 高德 POI 搜索 |
| 🌤 天气查询 | 查询出行期间天气预报 | 高德 天气查询 |
| 🏨 酒店推荐 | 搜索住宿并按景点距离排序 | 高德 POI 搜索 |
| 📚 RAG知识检索 | 为景点匹配攻略Tips | 本地知识库 (52条) |
| 🖼 Unsplash搜索 | 搜索景点实景配图 | Unsplash API |
| 🧠 规划协调 | 汇总信息生成结构化方案 | LLM (qwen-turbo) |

---

## 🚀 快速开始

### 1. 配置 API Key

编辑 `backend/.env`：
```env
# LLM API（百炼兼容接口，支持智谱/DeepSeek）
LLM_API_KEY=你的API密钥
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo

# Unsplash图片API（可选，不填则无配图）
UNSPLASH_ACCESS_KEY=你的Unsplash Access Key

# 高德地图 Web服务API（后端调用）
AMAP_API_KEY=你的高德Web服务API Key
```

编辑 `frontend/.env`：
```env
# 高德地图 JS API（前端地图展示）
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
│   ├── main.py                    # FastAPI入口 + lifespan(MCP+RAG)
│   ├── api/routes/travel.py       # SSE流式规划接口
│   ├── core/
│   │   ├── config.py              # Pydantic Settings配置
│   │   ├── mcp_server.py          # MCP Server(高德3工具+FastMCP)
│   │   ├── mcp_client.py          # 共享MCP客户端(单例管理)
│   │   └── rag.py                 # TF-IDF向量知识库
│   ├── agents/
│   │   ├── state.py               # LangGraph状态Schema
│   │   ├── graph.py               # 工作流图(并行+重试)
│   │   ├── coordinator.py         # 规划协调Agent
│   │   ├── attraction.py          # 景点搜索Agent
│   │   ├── weather.py             # 天气查询Agent
│   │   ├── hotel.py               # 酒店推荐Agent
│   │   ├── knowledge.py           # RAG知识检索Agent
│   │   └── unsplash.py            # Unsplash图片搜索Agent
│   └── schemas/request.py         # API数据模型
├── data/
│   └── travel_guides.json         # 预置旅游攻略知识库(52条)
├── .env
└── requirements.txt

frontend/
├── src/
│   ├── App.vue
│   ├── main.js
│   ├── views/TravelPlan.vue       # 主页面(侧栏+内容)
│   ├── components/
│   │   ├── TravelForm.vue         # 表单(偏好标签组)
│   │   ├── ResultDisplay.vue      # 进度条+概览卡片
│   │   ├── TripOverview.vue       # 蓝色概览卡片
│   │   ├── DayCard.vue            # 每日行程卡片(可折叠)
│   │   ├── MapView.vue            # 高德地图(路线+标记+联动)
│   │   ├── SpotImage.vue          # 景点缩略图
│   │   ├── SessionSidebar.vue     # 会话侧栏
│   │   ├── ExportButton.vue       # 方案导出
│   │   └── AgentStep.vue          # Agent步骤卡片
│   ├── stores/travel.js           # Pinia多会话管理
│   └── api/travel.js              # SSE客户端
├── .env
├── package.json
└── vite.config.js
```