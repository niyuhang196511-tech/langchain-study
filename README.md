# LangChain 学习笔记

这个仓库用于学习 LangChain Python 1.x。根目录中的脚本负责验证单个 API，`notes/` 负责解释概念、设计取舍和完整学习路线。

> 笔记基线：2026-07-23；锁定版本为 `langchain 1.3.14`、`langchain-core 1.5.0`、`langgraph 1.2.9`。LangChain 更新较快，复制旧教程代码前先确认它面向 0.x 还是 1.x。

## 学习导航

| 顺序 | 笔记 | 重点 |
| --- | --- | --- |
| 1 | [核心概念与模型调用](notes/01-core-concepts.md) | 生态分层、消息、模型、Prompt、结构化输出 |
| 2 | [Runnable 与 LCEL](notes/02-runnables-lcel.md) | `invoke` 协议、串行/并行、流式与错误处理 |
| 3 | [RAG 与向量检索](notes/03-rag-retrieval.md) | 加载、切块、Embedding、Milvus、RAG 架构与评估 |
| 4 | [Agent、Tool、MCP 与 Memory](notes/04-agents-memory-mcp.md) | Agent 循环、工具、短期/长期记忆、Middleware、HITL |
| 5 | [工程实践与学习路线](notes/05-production-roadmap.md) | 测试、评估、可观测性、安全、分阶段练习 |
| 6 | [LangGraph 状态图与持久执行](notes/06-langgraph.md) | StateGraph、路由、循环、Checkpoint、缓存、重试、流式、人工审批 |

建议先按顺序阅读，再运行同主题脚本。只看 API 容易“会调用但不会设计”，只看概念又不容易发现模型兼容性、环境变量和外部服务问题。

## 一张图理解技术栈

```text
应用
 ├─ 固定流程：Prompt | Model | Parser                (Runnable / LCEL)
 ├─ 检索增强：Load -> Split -> Embed -> Retrieve -> Generate
 └─ 动态流程：Model <-> Tools，直到得到最终结果       (Agent)
                        │
                        ├─ Checkpointer：同一 thread 的短期记忆
                        ├─ Store：跨 thread 的长期记忆
                        └─ Middleware：重试、摘要、护栏、人工审批等

LangChain：模型、工具、Agent 高层接口
LangGraph：Agent 底层状态图、持久化、恢复和长流程编排
LangSmith：Trace、调试、数据集、评估与线上观测
```

核心判断：步骤确定时优先使用普通 Python 或 Runnable；只有模型确实需要动态决定“下一步做什么、调用哪个工具”时才使用 Agent。

## 环境准备

本项目使用 Python 3.12 和 [uv](https://docs.astral.sh/uv/)：

```bash
uv sync
```

在项目根目录创建 `.env`，不要提交真实密钥：

```dotenv
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_MODEL=your-model-name
TAVILY_API_KEY=your-tavily-key
```

这里使用 `ChatOpenAI(base_url=...)` 连接 OpenAI-compatible 服务。兼容接口不代表所有能力完全一致，Tool Calling、JSON Schema、流式 usage 等特性仍要按具体模型验证。

运行示例：

```bash
uv run python 03_prompt_template.py
uv run python 14_agent.py
```

Embedding 和 Milvus 示例还有额外前置条件：

- `08_embedding.py`、`09_vector.py` 依赖本机 `/data/models/embedding/` 下的 BGE 模型。
- `10` 到 `12` 号脚本依赖可访问的 Milvus；连接 URI、向量维度和距离度量必须一致。
- `14_agent.py` 需要 Tavily 密钥；`15_mcp.py` 依赖远端 MCP 服务可用。
- `InMemorySaver`、`InMemoryStore` 只适合学习和测试，生产环境需要数据库后端。
- `langgraph/07_langgraph_state_save.py` 需要 `langgraph-checkpoint-sqlite`；运行产生的 `langgraph/db/state.db` 已忽略。

## 现有代码索引

| 文件 | 学习点 | 配套笔记 |
| --- | --- | --- |
| `01_dotenv.py` | 环境变量 | 本页 |
| `02_openai_chat_completion.py` | 原生 OpenAI SDK 基线 | [01](notes/01-core-concepts.md) |
| `03_langchain.py` | 模型调用、异步、结构化输出 | [01](notes/01-core-concepts.md) |
| `03_prompt_template.py` | Prompt + Model + Parser | [01](notes/01-core-concepts.md) |
| `04_runablesequence.py` | 串行 Runnable | [02](notes/02-runnables-lcel.md) |
| `05_runableparallel.py` | 并行 Runnable | [02](notes/02-runnables-lcel.md) |
| `06_document_loader_md.py` | 文档加载 | [03](notes/03-rag-retrieval.md) |
| `07_document_split.py` | 递归切块 | [03](notes/03-rag-retrieval.md) |
| `08_embedding.py`、`09_vector.py` | 稠密/稀疏向量 | [03](notes/03-rag-retrieval.md) |
| `10` 到 `12` 号脚本 | Milvus 建库、写入、查询 | [03](notes/03-rag-retrieval.md) |
| `13_tool_call.py` | 手动完成工具调用闭环 | [04](notes/04-agents-memory-mcp.md) |
| `14_agent.py` | `create_agent` | [04](notes/04-agents-memory-mcp.md) |
| `15_mcp.py` | MCP 工具接入 | [04](notes/04-agents-memory-mcp.md) |
| `16_memory.py` | Checkpointer 短期记忆 | [04](notes/04-agents-memory-mcp.md) |
| `langgraph/01_example.py` 到 `12_node_interrupt.py` | LangGraph 状态图、路由、持久化、缓存、重试、流式、HITL | [06](notes/06-langgraph.md) |
| `langgraph/edge_loop.py` | 条件循环与终止条件 | [06](notes/06-langgraph.md) |

## 官方资料

- [LangChain Python 1.x 总览](https://docs.langchain.com/oss/python/langchain/overview)
- [LangChain API Reference](https://reference.langchain.com/python/)
- [LangGraph 文档](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangSmith Observability](https://docs.langchain.com/langsmith/observability)
- [LangChain 1.0 迁移指南](https://docs.langchain.com/oss/python/migrate/langchain-v1)

网络文章适合获得思路，最终应以锁定依赖、官方文档和本地实验结果为准。
