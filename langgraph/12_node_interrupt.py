from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    name: str
    days: int
    approved: str


def approved_node(state: State):
    print("进入审批节点")

    name = state["name"]
    days = state["days"]

    approved_res = interrupt({
        "name": name,
        "days": days,
        "approved": "未审批",
    })



    if approved_res:
        return {"approved": "审批通过"}
    else:
        return {"approved": "审批为通过"}

graph = StateGraph(state_schema=State)

graph.add_node(approved_node)

graph.add_edge(START, "approved_node")
graph.add_edge("approved_node", END)

checkpointer = InMemorySaver()

compile = graph.compile(checkpointer=checkpointer)

config = {
    "configurable": {
        "thread_id": "aaaaa"
    }
}

res = compile.invoke({"name": "张三", "days": 10}, config=config)

res1 = compile.invoke(Command(resume=True), config=config)

print(res1)

