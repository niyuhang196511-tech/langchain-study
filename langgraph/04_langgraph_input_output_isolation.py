# 创建穿行图
from typing import TypedDict

from langgraph.constants import START,END
from langgraph.graph import StateGraph



class InputState(TypedDict):
    query: str

class OutputState(TypedDict):
    rag_result: str
    search_result: str

class State(TypedDict, InputState, OutputState):
    pass

def rag_node(state: State):
    print(state)
    return {"rag_result": "rag_result"}

def search_node(state: State):
    print(state)
    return {"search_result": "search_result"}

def final_node(state: State):
    print(state)

state_graph = StateGraph(state_schema=State, input_schema=InputState, output_schema=OutputState)
state_graph.add_node(rag_node).add_node(search_node).add_node(final_node)
state_graph.add_edge(START, "rag_node").add_edge(START, "search_node").add_edge("rag_node", "final_node").add_edge("search_node", "final_node").add_edge("final_node", END)

compile_graph = state_graph.compile()

res = compile_graph.invoke({"query": "你好"})
print(res)
