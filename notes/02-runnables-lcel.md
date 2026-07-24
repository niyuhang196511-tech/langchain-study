# 02. Runnable 与 LCEL

## 1. 心智模型

LCEL（LangChain Expression Language）用 `|` 表示数据从左向右流动。它本质上是 Runnable 的组合语法，不是一种新的编程语言：

```text
输入 dict -> PromptValue -> AIMessage -> str
            prompt        model       parser
```

组合后的 Chain 本身仍是 Runnable，因此继续拥有同步、异步、批量、流式和配置接口。

## 2. 串行组合

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("把下面文本概括为一句话：\n{text}")
chain = prompt | model | StrOutputParser()

result = chain.invoke({"text": "..."})
```

`A | B | C` 等价于 `RunnableSequence(A, B, C)`。每一步输出必须符合下一步输入契约。排错时逐步调用并打印 `type()`，通常很快能定位 `dict`、`PromptValue`、`AIMessage`、`str` 混用的问题。

## 3. 并行组合

`RunnableParallel` 会把同一份输入交给多个分支，并返回字典：

```python
from langchain_core.runnables import RunnableParallel

analysis = RunnableParallel(
    summary=summary_chain,
    keywords=keyword_chain,
)

result = analysis.invoke({"text": "..."})
# {"summary": "...", "keywords": "..."}
```

并行能降低互不依赖步骤的总时延，但会同时消耗 Provider 配额。分支有依赖时不应并行。

## 4. 传递、映射与自定义逻辑

常用构件：

- `RunnablePassthrough()`：原样传递输入。
- `RunnablePassthrough.assign(...)`：保留原字典并增加字段。
- `RunnableLambda(fn)`：把普通函数接入链。
- 字典字面量：在 LCEL 中会被自动转换为 `RunnableParallel`。

最小 2-Step RAG 的骨架：

```python
from langchain_core.runnables import RunnablePassthrough

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | rag_prompt
    | model
    | StrOutputParser()
)
```

这里输入问题同时流向 Retriever 和 `question`；检索结果先格式化为上下文，再进入 Prompt。

## 5. 流式

普通 Chain 可使用 `stream()` / `astream()`：

```python
for chunk in chain.stream({"text": "..."}):
    print(chunk, end="", flush=True)
```

流式链的关键是每个中间步骤都能增量处理。一个必须拿齐所有内容才返回的普通函数会形成缓冲点，使后续才开始输出。

Agent 还可以流式返回：

- `updates`：每个 Agent/Tool 步骤后的状态更新。
- `messages`：LLM token 与消息元数据。
- `custom`：工具主动发送的进度事件。

官方文档从 LangChain 1.3 起建议新项目优先了解 typed event streaming；`stream_mode` 仍适合理解和兼容现有代码。

## 6. 重试、Fallback 与配置

Runnable 可以增加运行策略：

```python
robust_model = model.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)

fallback_model = primary_model.with_fallbacks([backup_model])
```

工程原则：

1. 只对超时、连接错误、限流等瞬时问题重试。
2. 指数退避并加入 jitter，避免并发请求同步重试。
3. 有副作用的 Tool 默认不能整体重试，否则可能重复扣款或写数据。
4. Fallback 模型要验证 Prompt、Tool Schema 与结构化输出是否兼容。
5. 为整条请求设置总时间预算，不能让每一层各自无限重试。

## 7. Runnable 还是 Agent

| 问题 | Runnable/普通代码 | Agent |
| --- | --- | --- |
| 步骤是否预先确定 | 是 | 否 |
| 调用次数 | 可预测 | 可能循环，需限制 |
| 时延与成本 | 较稳定 | 波动更大 |
| 调试难度 | 较低 | 较高 |
| 典型场景 | 翻译、抽取、固定 RAG | 搜索研究、多工具动态决策 |

能画出固定 DAG 时，先用 Runnable 或 LangGraph 显式节点。Agent 是动态决策机制，不是“更高级的 Chain”。

## 8. 当前实验与练习

- `04_runablesequence.py`：串行的 Prompt、Model、Parser。
- `05_runableparallel.py`：同一输入并行翻译；结果键 `chinese` 实际放的是日语结果，后续可重命名为 `japanese`。

推荐练习：

1. 为并行翻译增加第三种语言，并使用 `batch()` 处理 10 条文本。
2. 给模型 Runnable 增加 timeout、retry、tags，观察 Trace。
3. 编写“检索 + 引用格式化 + 回答”的固定 Chain，再与 Agentic RAG 比较调用次数。

## 参考

- [Runnable API Reference](https://reference.langchain.com/python/langchain-core/runnables/)
- [Streaming](https://docs.langchain.com/oss/python/langchain/streaming)
- [Event streaming](https://docs.langchain.com/oss/python/langchain/event-streaming)
