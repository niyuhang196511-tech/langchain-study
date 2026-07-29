from typing import TypedDict

from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.types import CachePolicy, RetryPolicy
from langgraph.cache.memory import InMemoryCache
from langgraph.checkpoint.memory import InMemorySaver

count = 0

class State(TypedDict):
    query: str
    final_result: str

def get_info(state: State):
    global count
    print(f"第{count+1}次执行")

    if count != 3:
        count += 1
        raise Exception("报错了")

    query = state["query"]
    return {"final_result": f"用户问题：{query}，结果为挺好。"}

state_graph = StateGraph(state_schema=State)

state_graph.add_node(get_info, retry_policy=RetryPolicy(max_attempts=6))

state_graph.add_edge(START, "get_info")
state_graph.add_edge("get_info", END)

compile = state_graph.compile()

res = compile.invoke({"query": "北京的天气怎么样？"}, config={
    "configurable": {
        "thread_id": "aaaa",
    }
})
print(res)
