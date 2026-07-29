from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    value: int


def node_a(state: State):
    print("进入节点A")
    return {"value": state['value'] + 1}

def node_b(state: State):
    print("进入节点B")
    return {"value": state['value'] + 1}

def node_c(state: State):
    print("进入节点C")
    print("该书是一个技术")
    return {"value": state['value'] + 1}

def route_fun(state: State):
    value = state['value']
    if value % 2 == 0:
        return "b"
    else:
        return "c"


graph = StateGraph(state_schema=State)

graph.add_node(node_a)
graph.add_node(node_b)
graph.add_node(node_c)

graph.add_edge(START, "node_a")

graph.add_conditional_edges("node_a", route_fun, {
    "b": "node_b",
    "c": "node_c",
})

graph.add_edge( "node_b", END)
graph.add_edge( "node_c", END)


compile = graph.compile()


res = compile.invoke({"value": 2})


print(res)

