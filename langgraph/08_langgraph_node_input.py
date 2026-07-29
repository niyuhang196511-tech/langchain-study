from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime


class UserState(TypedDict):
    query: str
    token: str
    user_id: int
    user_name: str

config = {
    "configurable": {
        "token": "abcdefghijklmnopqrstuvwxyz",
    }
}

context = {
    "user_id": 1,
    "user_name": "admin",
}

def get_user_info(state: UserState, config: RunnableConfig, runtime: Runtime):
    query = state["query"]
    token = config["configurable"]["token"]

    user_id = runtime.context["user_id"]
    user_name = runtime.context["user_name"]

    return {
        "token": token,
        "user_id": user_id,
        "user_name": user_name,
    }


state_graph = StateGraph(state_schema=UserState)

state_graph.add_node(get_user_info)

state_graph.add_edge(START, "get_user_info")
state_graph.add_edge("get_user_info", END)

compile_graph = state_graph.compile()

res = compile_graph.invoke({
    "query": "你好阿"
}, config=config, context=context)

print(res)