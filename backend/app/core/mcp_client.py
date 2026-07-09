"""共享 MCP 客户端 — 单例管理，所有 Agent 复用同一 Server 连接"""

import asyncio
import logging
import sys
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)

_client: MultiServerMCPClient | None = None
_tools: dict[str, list] = {}
_lock = asyncio.Lock()

# MCP Server 路径 & 环境
_SERVER_PATH = Path(__file__).parent / "mcp_server.py"
_BACKEND_DIR = Path(__file__).parent.parent.parent  # backend/


async def init_mcp_client():
    """启动 MCP Server 子进程，获取工具缓存。"""
    global _client, _tools

    async with _lock:
        if _client is not None:
            return

        logger.info(f"Starting MCP Server ({_SERVER_PATH})...")
        _client = MultiServerMCPClient({
            "amap": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(_SERVER_PATH)],
                "env": {"PYTHONPATH": str(_BACKEND_DIR)},
            }
        })

        all_tools = await _client.get_tools()
        logger.info(f"MCP tools loaded: {[t.name for t in all_tools]}")

        _tools = {
            "attraction": [t for t in all_tools if t.name == "search_attractions"],
            "weather": [t for t in all_tools if t.name == "query_weather"],
            "hotel": [t for t in all_tools if t.name == "search_hotels"],
        }


async def close_mcp_client():
    """关闭 MCP 连接。"""
    global _client, _tools
    if _client is not None:
        logger.info("Closing MCP Server...")
        _client = None
        _tools = {}


def get_tools_for(agent: str) -> list:
    """获取指定 Agent 的工具列表（无需 await，init 后即可用）"""
    return _tools.get(agent, [])