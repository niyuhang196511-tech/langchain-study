import operator
import sqlite3
from pathlib import Path
from typing import TypedDict, Annotated
from langgraph.checkpoint.sqlite import SqliteSaver

from langgraph.constants import START,END
from langgraph.graph import StateGraph


class UserState(TypedDict):
    girl_friends: Annotated[list[str], operator.add]

def first_node(state: UserState):
    print(state)
    return {"girl_friends": ["张三"]}

def second_node(state: UserState):
    print(state)
    # raise Exception("xxx")
    return {"girl_friends": ["李四"]}

def last_node(state: UserState):
    print(state)
    return {"girl_friends": ["王五"]}

state_graph = StateGraph(state_schema=UserState)

state_graph.add_node(first_node)
state_graph.add_node(second_node)
state_graph.add_node(last_node)

state_graph.add_edge(START, "first_node")
state_graph.add_edge("first_node", "second_node")
state_graph.add_edge("second_node", "last_node")
state_graph.add_edge("last_node", END)

db_path = Path(__file__).with_name("db") / "state.db"
db_path.parent.mkdir(exist_ok=True)
conn = sqlite3.connect(db_path, check_same_thread=False)

# 创建checkpointer
checkpointer = SqliteSaver(conn)

compile_graph = state_graph.compile(checkpointer=checkpointer)

# res = compile_graph.invoke({}, config={
#     "configurable": {
#         "thread_id": "aaa",
#     }
# })
#
# print(res)

res = compile_graph.invoke(None, config={
    "configurable": {
        "thread_id": "aaa",
    }
})

print(res)
