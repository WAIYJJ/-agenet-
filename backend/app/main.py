"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.travel import router as travel_router
from app.core import mcp_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化 MCP Server + RAG，关闭时清理"""
    await mcp_client.init_mcp_client()
    yield
    await mcp_client.close_mcp_client()


app = FastAPI(
    title="智能旅游规划助手",
    description="基于多Agent协作的智能旅游规划API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(travel_router)


@app.get("/")
async def root():
    return {"message": "智能旅游规划助手 API 正在运行"}