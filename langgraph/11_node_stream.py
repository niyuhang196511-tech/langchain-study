from typing import TypedDict

from langgraph.constants import END, START
from langgraph.graph import StateGraph


class State(TypedDict):
    value: int
    message: str


def double_node(state: State):
    value = state["value"] * 2
    return {"value": value, "message": f"value={value}"}


graph = StateGraph(State)
graph.add_node("double", double_node)
graph.add_edge(START, "double")
graph.add_edge("double", END)
compiled = graph.compile()

# updates 模式按节点产出增量，适合向 UI 或日志逐步转发执行进度。
for chunk in compiled.stream({"value": 21, "message": ""}, stream_mode="updates"):
    print(chunk)
