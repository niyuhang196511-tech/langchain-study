from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    count: int
    max_count: int
    result: str


def node_a(state: State):
    print("node_a")

    count = state['count']

    count = count + 1

    return {"count": count, "result": f"第『{count -1}』次执行"}


def node_b(state: State):
    print("node_b")
    max_count = state['max_count']
    return {"result": f"最大次数为『{max_count}』"}


def route_fun(state: State):
    print("route_fun")
    count = state['count']
    max_count = state['max_count']

    if count >= max_count:
        return END
    else:
        return "node_a"

graph = StateGraph(state_schema=State)

graph.add_node(node_a)
graph.add_node(node_b)

graph.add_edge(START, "node_a")

graph.add_conditional_edges("node_a", route_fun)

graph.add_edge( "node_b", "node_a")


compile = graph.compile()


res = compile.invoke({"count": 1, "max_count": 5}, config={"recursion_limit": 20})

print(res)
