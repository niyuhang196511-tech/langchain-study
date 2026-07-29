# 06. LangGraph 状态图与持久执行

> 资料基线：2026-07-29；示例按本项目锁定的 `langgraph 1.2.9` 编写。API 更新较快，升级后应以官方文档和本地类型检查为准。

## 1. LangGraph 解决什么问题

LangChain 的 Runnable 适合固定的输入输出链；Agent 适合由模型动态选择工具。LangGraph 位于更底层，用有向图表达“状态如何被节点读取和更新、下一步走哪条边”。因此它适合有分支、循环、长时间运行、需要暂停恢复或人工审批的流程。

```text
State（共享数据）
   ↓
节点（纯函数或副作用步骤）
   ↓
边（固定边 / 条件边 / 循环边）
   ↓
Checkpoint（可选的持久状态）
```

本目录的 [01_example.py](../langgraph/01_example.py) 是最小图；[02_langgraph_serial_graph.py](../langgraph/02_langgraph_serial_graph.py) 和 [03_langgraph_parallel_graph.py](../langgraph/03_langgraph_parallel_graph.py) 对比串行与并行。

## 2. StateGraph、节点与边

状态通常用 `TypedDict` 描述。节点接收当前状态，只返回需要更新的字段；图会把更新合并到下一步状态。

```python
from typing import TypedDict
from langgraph.constants import END, START
from langgraph.graph import StateGraph

class State(TypedDict):
    query: str
    answer: str

def answer_node(state: State):
    return {"answer": f"收到：{state['query']}"}

graph = StateGraph(State)
graph.add_node("answer", answer_node)
graph.add_edge(START, "answer")
graph.add_edge("answer", END)
app = graph.compile()
print(app.invoke({"query": "你好"}))
```

`START` 和 `END` 是图的入口、出口；节点名称应稳定且唯一。`compile()` 会校验图并返回可调用对象，之后使用 `invoke`、`ainvoke`、`stream` 或 `astream`。如果一个节点同时连到多个后继节点，这些后继在同一 super-step 中并行执行；[03](../langgraph/03_langgraph_parallel_graph.py) 展示了两个检索分支汇聚到最终节点。

## 3. Schema 边界与 Reducer

图可以分别声明输入和输出 schema，避免把内部字段暴露给调用方。[04](../langgraph/04_langgraph_input_output_isolation.py) 使用 `InputState`、`OutputState` 和内部 `State` 完成隔离；节点也可以声明更窄的参数类型，实现私有中间状态（见 [05](../langgraph/05_langgraph_private_state.py)）。

默认情况下，同一字段的新值会覆盖旧值。需要累积列表、合并事件时，为字段声明 reducer：

```python
import operator
from typing import Annotated, TypedDict

class State(TypedDict):
    events: Annotated[list[str], operator.add]
```

[06](../langgraph/06_langgraph_state_overwrite.py) 对比了覆盖与 `operator.add` 合并。Reducer 必须满足清晰的合并语义；并行节点写入同一个字段时尤其要避免隐式的“最后写入者获胜”。

## 4. 条件边与循环

`add_conditional_edges(source, router, mapping)` 让路由函数根据状态返回目标键。路由函数最好是无副作用、可测试的纯函数：

```python
def route(state: State):
    return "retry" if state["attempts"] < 3 else END

graph.add_conditional_edges("work", route, {"retry": "work", END: END})
```

[07_edge_conditional.py](../langgraph/07_edge_conditional.py) 展示条件分支，[edge_loop.py](../langgraph/edge_loop.py) 展示计数循环。循环一定要有可证明的终止条件，并设置 `recursion_limit` 或总时长上限；否则异常数据可能让执行一直转圈。

## 5. Config、Runtime 与上下文

运行时配置不是业务状态。`RunnableConfig` 适合本次调用的 tracing、并发和 configurable 参数；`Runtime` 的 context 适合用户身份、租户和请求范围依赖。

```python
def node(state: State, config: RunnableConfig, runtime: Runtime):
    token = config["configurable"]["token"]
    user_id = runtime.context["user_id"]
    ...

app.invoke(input_state, config={"configurable": {"token": "..."}},
          context={"user_id": 1})
```

[08_langgraph_node_input.py](../langgraph/08_langgraph_node_input.py) 展示这两种注入方式。不要把密钥放进可持久化的 State；配置和 context 也应在边界处校验。

## 6. Checkpoint、线程与恢复

传入 checkpointer 后，图会按 `thread_id` 保存每个 super-step 的状态。`InMemorySaver` 适合测试；生产环境应使用持久后端，例如 SQLite、Postgres 或 LangGraph 提供的托管方案。

```python
from langgraph.checkpoint.memory import InMemorySaver

app = graph.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "conversation-001"}}
app.invoke({"query": "第一问"}, config=config)
app.invoke({"query": "继续"}, config=config)
```

[07_langgraph_state_save.py](../langgraph/07_langgraph_state_save.py) 使用 SQLite checkpointer；运行时数据库位于 `langgraph/db/state.db`，已被 `.gitignore` 排除。Checkpoint 是恢复执行的基础，但不是跨用户的长期记忆；长期用户资料应放在显式的 Store 或业务数据库中。

## 7. 缓存与重试

节点缓存适合确定性、代价高且输入可稳定序列化的工作；不能把带副作用的写操作随意缓存。`CachePolicy` 与 `InMemoryCache` 的示例见 [09_node_cache.py](../langgraph/09_node_cache.py)。

`RetryPolicy(max_attempts=...)` 只应重试瞬时失败（网络错误、短暂限流）。节点必须尽量幂等；付款、发消息等副作用应使用服务端幂等键，不能依赖“重试看起来只执行了一次”。见 [10_node_retry.py](../langgraph/10_node_retry.py)。

## 8. 流式与人工审批

`stream()` 可按节点更新、消息 token 或自定义事件输出。`stream_mode="updates"` 适合把节点进度转发到 UI；[11_node_stream.py](../langgraph/11_node_stream.py) 是最小示例。生产 UI 要处理断线、重复事件和最终状态确认，不能只把中间文本当作最终答案。

`interrupt(payload)` 会暂停图并把待处理信息返回给调用方；调用方在同一个 `thread_id` 下用 `Command(resume=value)` 恢复。[12_node_interrupt.py](../langgraph/12_node_interrupt.py) 展示审批流程。恢复前应验证操作者权限和 resume 数据；审批节点之前的副作用必须幂等，因为恢复或重放可能再次经过相关步骤。

## 9. 与 LangChain Agent 的关系

`create_agent` 建立在 LangGraph 的状态与执行能力之上，适合标准的模型-工具循环。直接使用 StateGraph 则可以精确控制状态 schema、路由、重试、审批和持久化。经验法则：流程固定时用普通函数/Runnable；流程有少量明确分支时用 StateGraph；工具选择和步骤数量真正由模型决定时再使用 Agent。

## 10. 常见问题清单

- 节点返回了 schema 中不存在的字段，或把完整 State 当作更新返回，导致状态契约难以维护。
- 并行节点写同一字段却没有 reducer，结果依赖调度顺序。
- 条件边没有覆盖所有返回值，运行时出现无法路由。
- 使用 `InMemorySaver` 误以为重启进程后数据仍在。
- 重试包含不可幂等副作用，造成重复写入。
- 把不可信网页/工具结果当作指令执行，忽略 Prompt Injection 风险。
- 未限制循环次数、模型调用数、工具超时和总预算。

## 官方资料

- [LangGraph Python Overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Memory](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Interrupts / Human-in-the-loop](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [Durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- [Caching](https://docs.langchain.com/oss/python/langgraph/cache)
- [Retry policies](https://docs.langchain.com/oss/python/langgraph/graph-api#retry-policies)
