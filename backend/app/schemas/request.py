"""旅行规划请求/响应数据模型"""

from typing import Optional
from pydantic import BaseModel, Field


class TravelRequest(BaseModel):
    """前端提交的旅行规划请求"""

    destination: str = Field(description="目的地城市，如：成都")
    start_date: str = Field(description="出发日期，如：2026-07-10")
    end_date: str = Field(description="返回日期，如：2026-07-15")
    budget: Optional[float] = Field(default=None, description="预算（元）")
    preferences: Optional[str] = Field(default=None, description="偏好，如：自然风光、美食")


class SSEEvent(BaseModel):
    """SSE 推送事件的数据格式"""

    event_type: str = Field(description="事件类型")
    data: dict = Field(description="事件数据内容")