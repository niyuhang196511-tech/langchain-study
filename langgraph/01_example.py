from typing import TypedDict

from langgraph.graph import StateGraph
from langgraph.constants import START,END


# 定义状态
class HelloState(TypedDict):
    message: str

# 定义节点
def hello_node(state: HelloState):
    # 获取状态中的message值
    msg = state['message']
    return {"message": f"Hello {msg}"}

# 创建状态图实例
state_graph = StateGraph(state_schema=HelloState)
# 给状态图添加节点
state_graph.add_node(hello_node)
# 给状态图添加边
state_graph.add_edge(START, "hello_node").add_edge("hello_node", END)

# 编译状态图
compile_state_graph = state_graph.compile()

# 执行
res = compile_state_graph.invoke({"message": "LangGraph"})

print(res)

# 获取图片
graph_structure = compile_state_graph.get_graph()
try:
    print(graph_structure.draw_ascii())
except ImportError:
    print("安装 grandalf 后可显示 ASCII 图：uv add grandalf")
