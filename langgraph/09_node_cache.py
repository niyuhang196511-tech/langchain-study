from typing import TypedDict

from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.types import CachePolicy
from langgraph.cache.memory import InMemoryCache
from langgraph.checkpoint.memory import InMemorySaver


class State(TypedDict):
    query: str
    final_result: str

def get_info(state: State):
    print(state)
    query = state["query"]
    return {"final_result": f"用户问题：{query}，结果为挺好。"}

state_graph = StateGraph(state_schema=State)

state_graph.add_node(get_info, cache_policy=CachePolicy())

state_graph.add_edge(START, "get_info")
state_graph.add_edge("get_info", END)

compile = state_graph.compile(cache=InMemoryCache(), checkpointer=InMemorySaver())

res = compile.invoke({"query": "北京的天气怎么样？"}, config={
    "configurable": {
        "thread_id": "aaaa",
    }
})
print(res)

res = compile.invoke({"query": "北京的天气怎么样？"}, config={
    "configurable": {
        "thread_id": "aaaa",
    }
})
print(res)
