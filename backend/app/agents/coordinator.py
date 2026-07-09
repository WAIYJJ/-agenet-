"""规划协调Agent — ReAct两阶段：分析→生成"""

import re, json, math
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import TravelState
from app.core.config import settings

PLANNER_SYSTEM = """你是行程规划专家。你的任务是根据景点、天气、酒店信息生成旅行计划。

请严格按照以下JSON格式返回（不要输出其他内容）:
```json
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [{
    "date": "YYYY-MM-DD", "day_index": 0,
    "description": "当日行程概述",
    "transportation": "交通方式",
    "accommodation": "住宿类型",
    "hotel": {"name":"","address":"","location":{"longitude":0,"latitude":0},"price_range":"","rating":"","distance":"","type":"","estimated_cost":0},
    "attractions": [{
      "name":"","address":"","location":{"longitude":0,"latitude":0},
      "visit_duration":120,"description":"","travel_tips":[""],"category":"","ticket_price":0
    }],
    "meals": [
      {"type":"breakfast","name":"","description":"","estimated_cost":0},
      {"type":"lunch","name":"","description":"","estimated_cost":0},
      {"type":"dinner","name":"","description":"","estimated_cost":0}
    ]
  }],
  "weather_info": [{"date":"","day_weather":"","night_weather":"","day_temp":0,"night_temp":0,"wind_direction":"","wind_power":""}],
  "overall_suggestions": "",
  "budget": {"total_attractions":0,"total_hotels":0,"total_meals":0,"total_transportation":0,"total":0}
}
```

规则:
- 每天2-3个景点，考虑距离和游览时长
- 温度纯数字，不含°C
- 早中晚三餐必填
- budget汇总各项真实费用
- travel_tips: 每个景点1-2条，写最佳时段/注意事项/特色推荐
"""

ANALYZE_PROMPT = """## 任务：分析旅行规划要素

请根据以下信息，进行行程分析（不生成JSON，只分析）：

1. 列出所有可用景点及其位置（坐标），计算景点间大致距离
2. 根据天气预报，判断每天适合户外还是室内活动
3. 考虑酒店位置与景点的距离，推荐合理的住宿区域
4. 规划每天合理的游览顺序（优先把距离近的景点安排在同一天）
5. 确定每天的交通方式

请详细输出以上5点分析结果。"""


def get_llm(temp=0.5):
    return ChatOpenAI(model=settings.llm_model, api_key=settings.llm_api_key,
                      base_url=settings.llm_base_url, temperature=temp, max_retries=2, timeout=60)


async def coordinator_analyze(state: TravelState) -> dict:
    """第一阶段：ReAct分析"""
    llm = get_llm(0.3)
    landmarks = _build_landmarks(state)
    response = await llm.ainvoke([SystemMessage(content=ANALYZE_PROMPT), HumanMessage(content=landmarks)])
    return {"messages": [response], "plan_status": "analyzing"}


async def coordinator_synthesize(state: TravelState) -> dict:
    """第二阶段：基于分析生成JSON方案"""
    llm = get_llm(0.4)
    landmarks = _build_landmarks(state)

    # 取第一阶段分析结果
    analysis = ""
    for msg in state.get("messages", []):
        if msg.type == "ai" and msg.content and len(msg.content) > 100:
            analysis = msg.content
            break

    prompt = ""
    if analysis:
        prompt = f"## 分析结果\n{analysis}\n\n## 任务\n基于以上分析，生成旅行规划JSON。"
    else:
        prompt = f"## 任务\n根据以下信息生成旅行规划JSON。"

    response = await llm.ainvoke([SystemMessage(content=PLANNER_SYSTEM), HumanMessage(content=f"{prompt}\n\n{landmarks}")])

    return _build_result(response.content, state)


def _build_landmarks(state: TravelState) -> str:
    lines = [f"目的地：{state['destination']}  日期：{state['start_date']}→{state['end_date']}  预算：{state.get('budget','不限')}  偏好：{state.get('preferences','无')}"]

    lines.append("\n## 景点")
    if state.get("attractions"):
        for a in state["attractions"][:10]:
            lines.append(f"- {a['name']} 坐标({a.get('lng',0):.4f},{a.get('lat',0):.4f}) 评分{a.get('rating','?')} 地址{a.get('address','')}")

    lines.append("\n## 天气")
    if state.get("weather_info"):
        for w in state["weather_info"].get("forecast", [])[:7]:
            lines.append(f"- {w['date']}: {w['weather']} {w['temp_low']}~{w['temp_high']}° 风向{w.get('wind','?')}")

    # 酒店按距离排序
    hotels = state.get("hotels") or []
    attractions = state.get("attractions") or []
    if hotels and attractions:
        for h in hotels:
            hlng, hlat = h.get("lng", 0), h.get("lat", 0)
            if hlng and hlat:
                dists = [math.sqrt((hlat - a.get("lat", 0))**2 + (hlng - a.get("lng", 0))**2) for a in attractions[:5] if a.get("lat") and a.get("lng")]
                h["_dist"] = sum(dists) / len(dists) if dists else float("inf")
            else:
                h["_dist"] = float("inf")
        hotels.sort(key=lambda h: h.get("_dist", float("inf")))

    lines.append("\n## 酒店（已按距离排序）")
    for h in hotels[:5]:
        lines.append(f"- {h['name']} 坐标({h.get('lng',0):.4f},{h.get('lat',0):.4f}) 价格{h.get('price','?')} 评分{h.get('rating','?')} 地址{h.get('address','')}")

    return "\n".join(lines)


def _build_result(final_plan: str, state: TravelState) -> dict:
    plan_json = {}
    try:
        m = re.search(r'```json\s*([\s\S]*?)\s*```', final_plan)
        plan_json = json.loads(m.group(1) if m else final_plan)
    except:
        plan_json = {"raw_text": final_plan}

    itinerary = []
    attractions = state.get("attractions") or []
    for a in attractions[:8]:
        itinerary.append({"day": 1, "place": a["name"], "lat": a["lat"], "lng": a["lng"], "type": "attraction"})
    hotels = state.get("hotels") or []
    for h in hotels[:3]:
        itinerary.append({"day": 1, "place": h["name"], "lat": h["lat"], "lng": h["lng"], "type": "hotel"})

    return {
        "messages": [], "final_plan": final_plan, "plan_json": plan_json,
        "itinerary": itinerary, "attractions": attractions, "hotels": hotels,
        "weather_info": state.get("weather_info"),
        "unsplash_images": state.get("unsplash_images") or [],
        "plan_status": "complete",
    }