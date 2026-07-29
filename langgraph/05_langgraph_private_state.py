# 创建穿行图
from typing import TypedDict

from langgraph.constants import START,END
from langgraph.graph import StateGraph


class State(TypedDict):
    query: str
    final_result: str

class PrivateState(TypedDict):
    rag_result: str
    search_result: str

def rag_node(state: State):
    print(state)
    return {"rag_result": "rag_result"}

def search_node(state: State):
    print(state)
    return {"search_result": "search_result"}

def final_node(state: PrivateState):
    print(state)
    return {"final_result": "final_result"}

state_graph = StateGraph(state_schema=State)
state_graph.add_node(rag_node).add_node(search_node).add_node(final_node)
state_graph.add_edge(START, "rag_node").add_edge(START, "search_node").add_edge("rag_node", "final_node").add_edge("search_node", "final_node").add_edge("final_node", END)

compile_graph = state_graph.compile()

res = compile_graph.invoke({"query": "你好"})
print(res)
