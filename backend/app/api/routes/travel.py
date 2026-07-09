"""旅行规划 SSE 接口"""

import json, traceback, asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.request import TravelRequest
from app.agents.graph import build_travel_graph

router = APIRouter(prefix="/api/travel", tags=["travel"])


@router.post("/plan")
async def plan_travel(request: TravelRequest):
    graph = build_travel_graph()
    state = {
        "destination": request.destination,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "budget": request.budget,
        "preferences": request.preferences,
        "messages": [],
        "attractions": None, "weather_info": None, "hotels": None,
        "final_plan": None, "itinerary": None, "plan_status": "planning",
    }

    async def gen():
        try:
            yield _sse(json.dumps({"event_type": "connected", "data": {}}))
            async for ev in graph.astream_events(state, version="v2"):
                s = _fmt(ev)
                if s:
                    yield _sse(s)
                    await asyncio.sleep(0)
            yield _sse("[DONE]")
        except Exception as e:
            yield _sse(json.dumps({"event_type": "error", "data": {"msg": str(e), "trace": traceback.format_exc()}}))
            yield _sse("[DONE]")

    return StreamingResponse(gen(), media_type="text/event-stream")


def _sse(data: str) -> str:
    return f"data: {data}\n\n"


def _fmt(ev: dict) -> str | None:
    k = ev.get("event")
    n = ev.get("name", "")
    d = ev.get("data", {})

    # node start
    if k == "on_chain_start" and n in ("coordinator_analyze", "coordinator_synthesize",
                                         "attraction_agent", "weather_agent", "hotel_agent"):
        return json.dumps({"event_type": "agent_start", "data": {"agent": n}})

    # LLM tokens
    if k == "on_chat_model_stream":
        c = d.get("chunk")
        if c and getattr(c, "content", None):
            return json.dumps({"event_type": "agent_thinking", "data": {"content": c.content}})

    # tool call
    if k == "on_tool_start":
        return json.dumps({"event_type": "agent_tool", "data": {"tool": n, "args": d.get("input", {})}})

    # node end
    if k == "on_chain_end" and n:
        o = d.get("output", {})
        if isinstance(o, dict):
            # plan_complete — from coordinator_synthesize
            if o.get("final_plan"):
                return json.dumps({"event_type": "plan_complete", "data": {
                    "plan": o["final_plan"],
                    "plan_json": o.get("plan_json", {}),
                    "attractions": o.get("attractions", []),
                    "hotels": o.get("hotels", []),
                    "weather_info": o.get("weather_info", {}),
                    "unsplash_images": o.get("unsplash_images", []),
                }})
            # agent_result — from sub-agents
            for key, agent in (("attractions", "attraction"), ("weather_info", "weather"), ("hotels", "hotel")):
                if o.get(key):
                    return json.dumps({"event_type": "agent_result", "data": {"agent": agent, "data": o[key]}})

    return None