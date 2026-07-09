"""天气查询Agent — 直接调用MCP工具"""

import json
from app.agents.state import TravelState
from app.core.mcp_client import get_tools_for


def _parse_mcp(msg_content):
    if isinstance(msg_content, list) and msg_content and 'text' in msg_content[0]:
        return json.loads(msg_content[0]['text'])
    return json.loads(msg_content)


async def weather_agent(state: TravelState) -> dict:
    tools = get_tools_for("weather")
    if not tools:
        return {"weather_info": {}, "messages": []}

    result = await tools[0].ainvoke({"city": state['destination']})
    try:
        weather_info = _parse_mcp(result)
    except:
        weather_info = {}
    return {"weather_info": weather_info, "messages": []}