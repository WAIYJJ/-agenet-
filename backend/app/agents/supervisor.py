"""监督者(父Agent)原型 — 设计参考，当前未接入工作流

此文件为父Agent动态调度模式的架构探索。由于LangGraph的fan-in语义在
Send+barrier模式下需要额外状态跟踪才能收敛，当前生产环境使用graph.py中
的固定DAG架构。此代码保留作为后续升级参考。
"""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings

SUPERVISOR_PROMPT = """你是旅行规划监督者(Supervisor Agent)。分析当前状态，动态决策下一步调用哪些子Agent。

可调用的子Agent:
- attraction_agent: 搜索景点
- weather_agent: 查询天气
- hotel_agent: 搜索酒店
- unsplash_agent: 获取景点配图
- coordinator_synthesize: 生成最终方案（所有数据就绪时调用）

决策逻辑:
1. 首次运行（景点/天气/酒店都无）→ 并行调用 attraction_agent, weather_agent, hotel_agent
2. 景点和天气已有，但无酒店 → 调用 hotel_agent
3. 全部数据都有，但无配图 → 调用 unsplash_agent
4. 全部就绪 → 调用 coordinator_synthesize (FINISH)

输出严格JSON:
单Agent: {"actions": ["attraction_agent"], "reason": "需要景点数据"}
并行: {"actions": ["attraction_agent","weather_agent","hotel_agent"], "reason": "首次，并行获取基础数据"}
结束: {"actions": ["coordinator_synthesize"], "reason": "所有数据就绪，生成方案"}"""


def get_llm():
    return ChatOpenAI(model=settings.llm_model, api_key=settings.llm_api_key,
                      base_url=settings.llm_base_url, temperature=0, max_tokens=200)


async def supervisor_agent(state: dict) -> dict:
    """父Agent：分析状态+决策下一步"""
    status = {
        "attractions": "✅" if state.get("attractions") else "❌",
        "weather_info": "✅" if state.get("weather_info") else "❌",
        "hotels": "✅" if state.get("hotels") else "❌",
        "unsplash_images": "✅" if state.get("unsplash_images") else "❌",
        "destination": state.get("destination", ""),
    }

    llm = get_llm()
    resp = await llm.ainvoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=json.dumps(status, ensure_ascii=False)),
    ])

    try:
        text = resp.content.strip()
        if text.startswith("```"): text = text.split("\n",1)[1].rsplit("\n",1)[0]
        decision = json.loads(text)
    except:
        decision = {"actions": ["coordinator_synthesize"], "reason": "Fallback：JSON解析失败，直接生成方案"}

    # 判断是否结束
    actions = decision.get("actions", [])
    done = "coordinator_synthesize" in actions

    return {
        "messages": [resp],
        "supervisor_decision": decision,
        "supervisor_done": done,
    }