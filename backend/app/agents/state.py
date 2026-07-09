"""LangGraph 工作流状态定义"""

from typing import Annotated, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TravelState(TypedDict):
    """旅行规划工作流的状态Schema"""

    # 用户输入
    destination: str
    start_date: str
    end_date: str
    budget: Optional[float]
    preferences: Optional[str]

    # 子Agent结果
    attractions: Optional[list[dict]]  # [{name, lat, lng, address, rating, description, type}]
    weather_info: Optional[dict]       # {city, forecast: [{date, weather, temp_high, temp_low}], tips}
    hotels: Optional[list[dict]]       # [{name, lat, lng, address, price, rating}]

    # Unsplash 图片结果
    unsplash_images: Annotated[Optional[list[dict]], lambda a, b: b or a]

    # 协调结果
    messages: Annotated[list[BaseMessage], add_messages]
    final_plan: Optional[str]          # 最终规划方案（Markdown文本）
    itinerary: Optional[list[dict]]    # [{day, activities: [{time, place, lat, lng}]}]
    plan_status: str                   # planning / sub_agents_done / complete
