# 创建穿行图
from typing import TypedDict

from langgraph.constants import START,END
from langgraph.graph import StateGraph


class State(TypedDict):
    query: str
    rag_result: str
    search_result: str


def rag_node(state: State):
    user_input = state.get('query')
    return {"rag_result": "rag_result"}

def search_node(state: State):
    user_input = state.get('query')
    return {"search_result": "search_result"}

state_graph = StateGraph(state_schema=State)
state_graph.add_node(rag_node).add_node(search_node)
state_graph.add_edge(START, "rag_node").add_edge("rag_node", "search_node").add_edge("search_node", END)

compile_graph = state_graph.compile()

res = compile_graph.invoke({"query": "你好"})
print(res)

graph_structure = compile_graph.get_graph()
try:
    print(graph_structure.draw_ascii())
except ImportError:
    print("安装 grandalf 后可显示 ASCII 图：uv add grandalf")
