"""高德地图 API MCP Server"""

import sys
from pathlib import Path
# 确保能 import app 模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json, asyncio
import httpx
from mcp.server.fastmcp import FastMCP
from app.core.config import settings

AMAP_BASE_URL = "https://restapi.amap.com/v3"

mcp = FastMCP("amap-travel-tools")


async def _amap_get(url: str, params: dict, retries: int = 2) -> dict:
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, params=params)
                return resp.json()
        except Exception:
            if attempt < retries:
                await asyncio.sleep(1 * (attempt + 1))
            else:
                raise
    return {}


@mcp.tool()
async def search_attractions(city: str, keywords: str = "景点", offset: int = 10) -> str:
    """搜索指定城市的旅游景点"""
    params = {"key": settings.amap_api_key, "keywords": keywords, "city": city,
              "types": "110000", "offset": offset, "output": "JSON"}
    data = await _amap_get(f"{AMAP_BASE_URL}/place/text", params)
    pois = data.get("pois", [])
    results = []
    for p in pois:
        loc = p.get("location", "").split(",")
        results.append({"name": p.get("name", ""),
                        "lat": float(loc[1]) if len(loc) == 2 else 0,
                        "lng": float(loc[0]) if len(loc) == 2 else 0,
                        "address": p.get("address", ""),
                        "rating": p.get("biz_ext", {}).get("rating", "")})
    return json.dumps(results, ensure_ascii=False)


@mcp.tool()
async def query_weather(city: str) -> str:
    """查询指定城市的天气预报"""
    params = {"key": settings.amap_api_key, "city": city, "extensions": "all", "output": "JSON"}
    data = await _amap_get(f"{AMAP_BASE_URL}/weather/weatherInfo", params)
    forecasts = data.get("forecasts", [])
    if not forecasts:
        return "{}"
    f_list = [{"date": d.get("date", ""), "weather": d.get("dayweather", ""),
               "temp_high": d.get("daytemp", ""), "temp_low": d.get("nighttemp", ""),
               "wind": d.get("daywind", "")} for d in forecasts[0].get("casts", [])]
    return json.dumps({"city": city, "forecast": f_list}, ensure_ascii=False)


@mcp.tool()
async def search_hotels(city: str, keywords: str = "酒店", offset: int = 10) -> str:
    """搜索指定城市的酒店住宿"""
    params = {"key": settings.amap_api_key, "keywords": keywords, "city": city,
              "types": "100000", "offset": offset, "output": "JSON"}
    data = await _amap_get(f"{AMAP_BASE_URL}/place/text", params)
    pois = data.get("pois", [])
    results = []
    for p in pois:
        loc = p.get("location", "").split(",")
        results.append({"name": p.get("name", ""),
                        "lat": float(loc[1]) if len(loc) == 2 else 0,
                        "lng": float(loc[0]) if len(loc) == 2 else 0,
                        "address": p.get("address", ""),
                        "price": p.get("biz_ext", {}).get("cost", ""),
                        "rating": p.get("biz_ext", {}).get("rating", "")})
    return json.dumps(results, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")