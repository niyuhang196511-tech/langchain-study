# 01. 核心概念与模型调用

## 1. LangChain 解决什么问题

直接调用模型 SDK 已经能聊天。LangChain 的价值不在“替你发 HTTP 请求”，而在于为模型、消息、工具、检索器和执行流程提供统一接口，让组件可以组合、替换、追踪和测试。

生态分工：

| 项目 | 适用场景 |
| --- | --- |
| LangChain | 模型统一接口、Prompt、Runnable、Tool、`create_agent` |
| LangGraph | 需要显式状态、分支、循环、持久化、暂停恢复的工作流 |
| LangSmith | Trace、调试、数据集、离线评估、线上监控 |
| Deep Agents | 文件系统、上下文压缩、子 Agent 等能力开箱即用的 Agent |

LangChain 1.x 的中心更偏向 Agent，但固定流程的 Runnable/LCEL 依然非常有用。不要为了使用框架而使用 Agent。

## 2. 包结构

- `langchain-core`：消息、Prompt、Runnable、Tool 等抽象。
- `langchain`：Agent 与 Middleware 等高层能力。
- `langchain-openai`、`langchain-huggingface`：Provider 集成。
- `langchain-community`：社区维护的 Loader、Vector Store 等集成。
- `langgraph`：状态图、Checkpointer、Store 和持久执行。

集成被拆成独立包后，教程中的 import 路径很容易过期。遇到 `ImportError` 时先看当前官方集成页和 `uv.lock`，不要盲目降级整个项目。

## 3. 模型与消息

Chat Model 接收字符串或消息列表，返回 `AIMessage`：

```python
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model=os.environ["DEEPSEEK_MODEL"],
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.environ["DEEPSEEK_BASE_URL"],
    temperature=0,
)

response = model.invoke([
    ("system", "你是严谨的 Python 教师。"),
    ("human", "用一句话解释迭代器。"),
])

print(response.content)
print(response.usage_metadata)      # Provider 支持时包含 token 用量
print(response.response_metadata)   # finish reason、model 等元数据
```

四种重要消息：

- `SystemMessage`：角色、边界、输出规则等高优先级上下文。
- `HumanMessage`：用户输入，可包含文本和多模态内容块。
- `AIMessage`：模型输出，也可能携带 `tool_calls`。
- `ToolMessage`：工具执行结果，必须通过 `tool_call_id` 对应原调用。

字符串适合单轮任务；消息列表适合多轮、工具调用和多模态。不要只保存文本而丢掉角色、工具调用 ID 和其他元数据。

## 4. 统一调用协议

多数 LangChain 组件都实现 Runnable 接口：

| 方法 | 含义 |
| --- | --- |
| `invoke(input)` | 单条同步调用 |
| `ainvoke(input)` | 单条异步调用 |
| `batch(inputs)` / `abatch(inputs)` | 批量调用；是否真正批处理取决于组件实现 |
| `stream(input)` / `astream(input)` | 流式输出 |

异步适合已有事件循环的 Web 服务或大量 I/O 并发，不会自动让单次模型推理更快。批量任务要设置合理的并发上限，避免触发 Provider 限流。

`RunnableConfig` 可在调用时携带标签、元数据、回调和并发配置：

```python
result = model.invoke(
    "解释 LCEL",
    config={
        "tags": ["study", "chapter-01"],
        "metadata": {"user_id": "u-001"},
    },
)
```

这些运行元数据适合 Trace 和排错，不应该被当作 Prompt 内容。

## 5. Prompt Template

模板的作用是把动态数据稳定地转换成模型输入：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{domain}领域的教师，只根据给定主题回答。"),
    ("human", "主题：{topic}\n要求：给出定义和一个例子。"),
])

chain = prompt | model | StrOutputParser()
answer = chain.invoke({"domain": "Python", "topic": "生成器"})
```

Prompt 编写原则：

1. 写清任务、输入边界、输出要求和失败策略。
2. 数据与指令使用明确分隔符，外部文档始终按“不可信数据”处理。
3. 需要机器消费时优先使用结构化输出，而不是要求模型“只返回 JSON”后手写解析。
4. Few-shot 示例主要用于消除歧义，不是越多越好；示例也会占上下文和费用。
5. Prompt 应进入版本控制，并用固定数据集回归测试。

## 6. 结构化输出

结构化输出适用于信息抽取、分类、路由和 API 参数生成：

```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="姓名")
    age: int | None = Field(default=None, description="年龄；未知则为空")

structured_model = model.with_structured_output(Person)
person = structured_model.invoke("小王今年 20 岁。")
assert isinstance(person, Person)
```

模型级 `with_structured_output()` 适合单次模型任务。Agent 级结构化结果使用 `create_agent(..., response_format=Schema)`，最终从状态的 `structured_response` 读取。LangChain 会根据模型能力选择 Provider 原生结构化输出或 Tool Strategy。

注意：Schema 是验证边界，不是事实保证。字段格式正确，内容仍可能错误；关键数据要继续做业务校验。

## 7. 参数选择

- `temperature`：控制采样随机性。抽取、分类通常设为 0 或低值；创作任务可提高。
- `max_tokens` / `max_completion_tokens`：限制输出成本，但不同 Provider 参数名和行为可能不同。
- timeout：所有线上模型调用都应有超时。
- retry：只重试瞬时失败；认证失败、无效请求不应盲目重试。
- model：不仅比较效果，也比较上下文、工具调用、结构化输出、时延、价格和限流。

## 8. 当前实验对应关系

- `02_openai_chat_completion.py` 是不使用 LangChain 的基线，有助于理解框架没有改变模型本身。
- `03_langchain.py` 展示消息、异步和 `with_structured_output()`。
- `03_prompt_template.py` 展示最小的 `Prompt | Model | Parser`。

建议实验：给同一抽取任务分别使用自然语言 JSON 指令、`JsonOutputParser` 和 `with_structured_output()`，记录格式错误率与 Provider 兼容性。

## 参考

- [Models](https://docs.langchain.com/oss/python/langchain/models)
- [Messages](https://docs.langchain.com/oss/python/langchain/messages)
- [Structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview)
