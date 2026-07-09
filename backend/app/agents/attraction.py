"""景点搜索Agent — 直接调用MCP工具"""

import json
from app.agents.state import TravelState
from app.core.mcp_client import get_tools_for


def _parse_mcp(msg_content):
    """统一解析 MCP 工具返回的 [{'type':'text','text':'...'}] 格式"""
    if isinstance(msg_content, list) and msg_content and 'text' in msg_content[0]:
        return json.loads(msg_content[0]['text'])
    return json.loads(msg_content)


async def attraction_agent(state: TravelState) -> dict:
    tools = get_tools_for("attraction")
    if not tools:
        return {"attractions": [], "messages": []}

    result = await tools[0].ainvoke({
        "city": state['destination'],
        "keywords": state.get('preferences') or '热门景点',
        "offset": 10,
    })
    try:
        attractions = _parse_mcp(result)
    except:
        attractions = []
    return {"attractions": attractions, "messages": []}