import operator
from typing import TypedDict, Annotated

from langgraph.constants import START,END
from langgraph.graph import StateGraph

def operate_state_value(old_value, new_value):
    return old_value + new_value

class UserState(TypedDict):
    # hobbies: Annotated[list[str], operator.add]
    hobbies: Annotated[list[str], operate_state_value]

def add_hobby1(state: UserState):
    print(state)

    hobbies = ["打篮球"]

    return {"hobbies": hobbies}

def add_hobby2(state: UserState):
    print(state)

    hobbies = ["Rap"]

    return {"hobbies": hobbies}

state_graph = StateGraph(state_schema=UserState)

state_graph.add_node(add_hobby1).add_node(add_hobby2)
state_graph.add_edge(START, "add_hobby1")
state_graph.add_edge("add_hobby1", "add_hobby2")
state_graph.add_edge( "add_hobby2", END)

compile_graph = state_graph.compile()
res = compile_graph.invoke({"hobbies": ["唱"]})

print(res)