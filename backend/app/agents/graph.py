"""LangGraph 工作流 — 并行DAG + ReAct两阶段规划"""

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, RetryPolicy
from app.agents.state import TravelState
from app.agents.coordinator import coordinator_analyze, coordinator_synthesize
from app.agents.attraction import attraction_agent
from app.agents.weather import weather_agent
from app.agents.hotel import hotel_agent
from app.agents.unsplash import unsplash_agent

retry = RetryPolicy(retry_on=Exception, max_attempts=2, initial_interval=1, backoff_factor=2)


def dispatch_all(state: TravelState) -> list[Send]:
    return [Send("attraction_agent", state), Send("weather_agent", state), Send("hotel_agent", state)]


def build_travel_graph():
    graph = StateGraph(TravelState)

    graph.add_node("attraction_agent", attraction_agent, retry=retry)
    graph.add_node("weather_agent", weather_agent, retry=retry)
    graph.add_node("hotel_agent", hotel_agent, retry=retry)
    graph.add_node("unsplash_agent", unsplash_agent)
    graph.add_node("coordinator_analyze", coordinator_analyze, retry=retry)
    graph.add_node("coordinator_synthesize", coordinator_synthesize, retry=retry)

    # START → 3子Agent并行
    graph.add_conditional_edges(START, dispatch_all, ["attraction_agent", "weather_agent", "hotel_agent"])

    # 子Agent完成 → ReAct阶段1分析
    graph.add_edge("attraction_agent", "coordinator_analyze")
    graph.add_edge("weather_agent", "coordinator_analyze")
    graph.add_edge("hotel_agent", "coordinator_analyze")

    # ReAct阶段1 → Unsplash → 阶段2
    graph.add_edge("coordinator_analyze", "unsplash_agent")
    graph.add_edge("unsplash_agent", "coordinator_synthesize")

    graph.add_edge("coordinator_synthesize", END)

    return graph.compile()