# 04. Agent、Tool、MCP 与 Memory

## 1. Agent 循环

Agent 是“模型调用工具，观察结果，再决定下一步”的循环：

```text
用户输入 -> Model -> 最终回答
                 \
                  Tool Call -> Tool Result -> Model -> ...
```

LangChain 1.x 使用 `create_agent` 创建可配置的 Agent harness。它底层构建在 LangGraph 上，因此天然支持状态、持久化、流式和 Middleware。

```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=[search],
    system_prompt="必要时使用搜索工具；引用搜索来源。",
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "查询今天的天气"}],
})
print(result["messages"][-1].content)
```

Agent 调用次数不固定。必须设置模型调用/工具调用限制、超时和失败策略，避免循环失控。

## 2. Tool 的契约

工具是名称、描述、输入 Schema 和执行函数的组合：

```python
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气。仅用于天气问题。"""
    return f"{city}: 晴"
```

设计质量直接影响模型是否会正确选工具：

- 名称使用稳定的 `snake_case`。
- 参数必须有类型标注；复杂参数使用 Pydantic Schema。
- 描述说明何时使用、何时不要使用、参数单位与结果语义。
- 返回简洁的结构化数据，避免把数万行原始结果塞回模型。
- 工具内部校验权限、参数和业务规则，不能相信模型已经校验。
- 读操作与写操作分开；写操作应支持幂等键和人工审批。

`config` 与 `runtime` 是保留参数名。需要访问 State、Context、Store、Stream Writer 等运行信息时使用官方的 `ToolRuntime` 注入。

## 3. 手动 Tool Calling 闭环

`bind_tools()` 只让模型知道工具 Schema，不会自动执行工具。完整流程是：

1. 模型返回带 `tool_calls` 的 `AIMessage`。
2. 应用执行每个工具调用。
3. 把原 `AIMessage` 和对应 `ToolMessage` 都追加到历史。
4. 再次调用模型得到解释或下一个 Tool Call。

`13_tool_call.py` 展示了这个闭环。它适合学习协议；复杂循环优先交给 `create_agent`，否则还要手工处理多个调用、错误、重试和终止条件。

## 4. 短期记忆：Checkpointer

短期记忆属于一个会话 thread，最常见内容是消息历史：

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(model=model, tools=[], checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "conversation-001"}}

agent.invoke(
    {"messages": [{"role": "user", "content": "我叫小王。"}]},
    config=config,
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "我叫什么？"}]},
    config=config,
)
```

相同 `thread_id` 会恢复同一状态，不同 ID 应隔离。`InMemorySaver` 重启即丢失，生产使用 Postgres、MongoDB 等持久 Checkpointer。

对话不是越长越好。长历史会增加费用、延迟与注意力噪声，常见策略包括删除过期消息、滑动窗口、对旧历史做摘要，以及把稳定偏好写入长期记忆。

## 5. 长期记忆：Store

长期记忆跨 thread 保存，底层是按 namespace 和 key 组织的 JSON 文档：

```text
Checkpointer -> thread 范围 -> “这段对话刚才说了什么”
Store        -> user/org 范围 -> “这个用户长期偏好什么”
Vector Store -> knowledge 范围 -> “外部资料中有哪些相关内容”
```

三者不要混淆。长期记忆常分为：

- Semantic：用户事实与偏好，例如语言和单位。
- Episodic：过去任务、反馈和结果。
- Procedural：系统如何执行任务的规则，通常体现在 Prompt 或策略中。

使用 Store 时 namespace 应包含可信的 user/org ID，并设置数据删除、过期、纠错和隐私机制。不要让模型把每句对话都永久保存。

## 6. Runtime Context 与 State

- State：会话内可变数据，例如 messages、计数器、当前订单。
- Runtime Context：单次运行传入的不可变依赖，例如 user ID、角色、部署环境。
- Store：跨会话持久数据。

身份和权限应来自认证系统提供的 Runtime Context，不能从用户 Prompt 中解析后直接相信。工具再依据该身份做服务端鉴权。

## 7. MCP

MCP（Model Context Protocol）标准化应用向模型提供 Tool、Resource 和 Prompt 的方式。`langchain-mcp-adapters` 会把 MCP Tool 转换成 LangChain Tool：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "weather": {
        "transport": "http",
        "url": "https://example.com/mcp",
        "headers": {"Authorization": "Bearer ..."},
    },
})
tools = await client.get_tools()
agent = create_agent(model=model, tools=tools)
```

常见 Transport：

- `stdio`：启动本地子进程，通过标准输入输出通信。
- `http` / `streamable-http`：连接远端服务。
- SSE：旧规范中的方式，新增服务优先使用 Streamable HTTP。

`MultiServerMCPClient` 默认是无状态的，每次工具调用会创建并清理新的 Session。服务端需要跨调用状态时，显式使用 `client.session()` 管理 Session 生命周期。

MCP 只是协议，不是安全边界。接入第三方 Server 前要审查工具权限、认证、输入输出、超时和数据去向；高风险工具仍需审批。

## 8. Middleware 与 Context Engineering

Agent 可靠性的核心通常不是“更聪明地写一句 Prompt”，而是在正确时机给模型正确上下文。Middleware 可以在 Agent 生命周期中：

- 动态生成 System Prompt 或筛选工具。
- 在长对话中摘要、裁剪消息。
- 对模型和工具增加重试、Fallback、调用上限。
- 检测/脱敏 PII，增加 Guardrail。
- 记录日志和指标。
- 在高风险 Tool 前暂停并请求人工审批。

常用内置 Middleware 包括 Summarization、Human-in-the-loop、Model/Tool retry、Fallback、Call limit 和 PII detection。Middleware hook 运行在 `create_agent` 编译出的 LangGraph 内，不是额外的独立 Runtime。

## 9. Human-in-the-loop

发送邮件、执行 SQL、付款、删除数据等工具不应只靠 Prompt 约束。HITL Middleware 会在匹配的 Tool Call 前触发 interrupt，把图状态保存到 Checkpointer；人工可以 approve、edit 或 reject，随后用同一 thread 恢复执行。

生产要求：

1. 使用持久 Checkpointer，否则进程重启后无法恢复。
2. 给审批界面显示工具名、完整参数、影响范围和请求来源。
3. 审批之后重新鉴权，防止等待期间权限或资源状态变化。
4. 副作用 Tool 使用幂等键，处理恢复与网络重试导致的重复执行。

## 10. 流式 Agent

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "查天气"}]},
    stream_mode="updates",
):
    print(chunk)
```

前端通常需要区分模型 token、工具开始/完成、进度、最终答案和 interrupt，而不是把所有事件当作字符串拼接。对用户展示工具执行状态，但不要泄漏密钥、内部 Prompt 或敏感参数。

## 11. 推荐练习

1. 给 `13_tool_call.py` 增加参数 Schema、无 Tool Call 分支和多个 Tool Call 处理。
2. 用两个不同 `thread_id` 验证 `16_memory.py` 的状态隔离。
3. 新增长期 Store，分别保存两个用户的语言偏好。
4. 为一个“删除记录”假工具增加 HITL，测试 approve/reject。
5. 中断远端 MCP 服务，观察错误如何以 ToolMessage 返回并设计重试上限。

## 参考

- [Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [Tools](https://docs.langchain.com/oss/python/langchain/tools)
- [Short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)
- [Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)
- [Middleware](https://docs.langchain.com/oss/python/langchain/middleware/overview)
- [Context engineering](https://docs.langchain.com/oss/python/langchain/context-engineering)
- [MCP](https://docs.langchain.com/oss/python/langchain/mcp)
- [Human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
