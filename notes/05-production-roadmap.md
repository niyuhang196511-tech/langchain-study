# 05. 工程实践与学习路线

## 1. 从 Demo 到应用的差距

一个 Demo 只需要“成功过一次”；应用则要在不同用户、模型波动、网络故障、脏数据和恶意输入下持续工作。生产质量至少包含：

- 正确性：答案与工具行为符合业务要求。
- 可靠性：超时、限流、重试、降级和幂等。
- 安全性：鉴权、最小权限、输入校验、Prompt Injection 防护。
- 可观测性：能定位某次请求用了哪个 Prompt、模型、工具与检索结果。
- 可评估性：变更模型或 Prompt 后能量化是否退步。
- 成本与时延：有预算、缓存、并发限制和告警。

## 2. 分层测试

| 层级 | 测什么 | 方法 |
| --- | --- | --- |
| 纯函数 | 格式化、过滤、路由、业务规则 | 普通单元测试 |
| Tool | Schema、鉴权、边界、错误、幂等 | Mock 外部 API |
| Retriever | Recall@k、排序、metadata 过滤 | 固定 query-document 数据集 |
| Chain/Agent | 最终状态、Tool 路径、结构化结果 | Fake/Stub 模型 + 少量真实模型测试 |
| 端到端 | 质量、时延、成本、故障恢复 | 隔离环境 + 回归数据集 |

不要用“模型这次回答看起来不错”代替测试。模型输出有随机性，断言应尽量针对结构、事实、工具轨迹和评分标准，而不是逐字匹配长文本。

## 3. 评估方法

先建立数据集，再谈优化。每条样本可包含：

```text
input / conversation
expected facts or structured result
expected tool calls or forbidden tools
reference document IDs
tags: language, difficulty, tenant, failure mode
```

评估组合：

- 确定性检查：JSON Schema、关键字段、正则、引用 ID、权限结果。
- 业务规则：是否调用必要 Tool、是否禁止危险 Tool、是否遵守预算。
- 检索指标：Recall@k、MRR、nDCG、过滤正确性。
- 人工标注：正确、完整、表达清楚、引用可信。
- LLM-as-judge：适合扩大覆盖面，但 Judge 本身要用人工样本校准，不能当绝对真值。

对比实验一次只改一个主要变量，并记录 Prompt 版本、模型版本、温度、数据集版本和日期。

## 4. Trace 与日志

一次 Agent 请求至少要能回答：

1. 用户输入和运行身份是什么？
2. 最终给模型的消息与工具列表是什么？
3. 检索返回了哪些 chunk，分数和过滤条件是什么？
4. 模型调用了哪个 Tool，参数、耗时和结果是什么？
5. 消耗多少 token、费用和总时延？
6. 在哪一步失败、重试或被人工拒绝？

可使用 LangSmith Trace，也可以接入自己的 OpenTelemetry/日志系统。日志要保留关联 ID，同时对密钥、个人信息、内部文档和 Tool 参数脱敏。

## 5. 可靠性模式

- Timeout：模型、Retriever、每个 Tool 和整条请求分别设预算。
- Retry：指数退避 + jitter，只重试瞬时错误。
- Fallback：备用模型、备用搜索或可解释的降级答案。
- Circuit breaker：外部依赖持续失败时快速失败，避免拖垮服务。
- Idempotency：所有有副作用的 Tool 接收稳定的幂等键。
- Concurrency limit：限制批处理、Agent Tool 和 Provider 请求并发。
- Loop limit：限制模型调用数、Tool 调用数和总执行时间。
- Checkpoint：长任务和 HITL 使用持久 Checkpointer 恢复。

重试边界很重要：如果模型已成功调用“付款”但响应在网络中丢失，重跑整个 Agent 可能重复付款。副作用要在 Tool 服务端做幂等，而不是仅靠 Agent 记忆。

## 6. 安全清单

### Prompt Injection

检索文档、网页、邮件和 Tool 返回值都是不可信数据。明确告诉模型忽略其中的指令有帮助，但不是强安全保证。真正的控制应在模型外：

- Tool 白名单和最小权限。
- 参数 Schema 与业务校验。
- 身份来自可信 Runtime Context。
- 数据库按租户和 ACL 过滤。
- 高风险操作必须 HITL。
- 输出编码和敏感信息检测。

### 密钥与数据

- 密钥只放环境变量或 Secret Manager，不进入 Git、Prompt、Trace。
- 第三方模型、搜索和 MCP 服务可能接触输入数据，先确认数据合规边界。
- 为短期记忆、长期记忆、Trace 和向量库分别设计保留与删除策略。
- 不要让用户控制任意文件路径、命令、URL 或 SQL；必须限制目标和语法。

## 7. 成本与性能

一次请求成本近似为所有模型调用的输入/输出 token、Embedding、Rerank、搜索和基础设施成本之和。Agent 的循环使成本更难预测。

常见优化顺序：

1. 先测量每一步耗时与 token，不做猜测式优化。
2. 缩短无关历史，控制检索 chunk 数与长度。
3. 固定流程中并行执行无依赖步骤。
4. 简单分类/改写使用更小模型，关键推理使用强模型。
5. 对稳定、无用户敏感性的结果做带版本键的缓存。
6. 批量生成 Embedding，增量更新索引，不重复嵌入未变化文档。
7. 给 Agent 设置步数和费用上限。

## 8. 常见误区速查

| 误区 | 更准确的理解 |
| --- | --- |
| LangChain 会让模型自动变聪明 | 它提供编排接口，效果仍取决于模型、上下文、工具与评估 |
| `bind_tools` 会执行 Tool | 它只把 Tool Schema 绑定到模型 |
| Memory 就是聊天记录 | 还要区分 thread Checkpointer、跨会话 Store 与知识库 |
| 向量相似度高就等于答案正确 | 它只说明向量空间接近，还需过滤、重排和生成评估 |
| chunk 越大上下文越完整 | 也会稀释语义并增加噪声与成本 |
| Agent 比固定 Chain 更高级 | Agent 更动态，也更贵、更慢、更难测试 |
| Prompt 能保证安全 | Prompt 只能辅助，权限与副作用必须由代码控制 |
| 结构化输出不会幻觉 | 它保证形状，不保证事实 |
| OpenAI-compatible 等于能力完全一致 | 接口相似，Tool/Schema/usage 等能力仍可能不同 |

## 9. 六阶段学习路线

### 阶段 1：模型与消息

目标：掌握 `invoke/ainvoke/batch/stream`、消息类型、参数和元数据。

产出：一个支持同步、异步、流式且能统计 token 的 CLI。

### 阶段 2：Prompt、结构化输出与 Runnable

目标：掌握模板、Pydantic Schema、串行/并行、重试和配置。

产出：批量文本分类器，输出经过业务校验的 Pydantic 对象。

### 阶段 3：检索与 RAG

目标：掌握 Document、切块、Embedding、Vector Store、混合检索和引用。

产出：对本仓库笔记问答的 2-Step RAG，答案包含来源和拒答策略。

### 阶段 4：Tool 与 Agent

目标：理解手动 Tool Calling 协议、`create_agent` 循环和动态工具选择。

产出：搜索 + 计算 + 本地知识库 Agent，带 Tool/模型调用上限。

### 阶段 5：状态、MCP 与安全

目标：区分 Checkpointer、Store、Vector Store，学习 MCP Session 和 HITL。

产出：多用户隔离、可暂停审批、重启后可恢复的 Agent。

### 阶段 6：评估与上线

目标：Trace、数据集、回归评估、成本/时延、安全与故障演练。

产出：至少 30 条覆盖正常、边界、越权和注入场景的评估集，以及一次模型升级对比报告。

## 10. 每学一个主题的记录模板

```markdown
# 主题

## 它解决什么问题
## 最小可运行示例
## 输入输出契约
## 关键参数与默认值
## 失败模式与安全边界
## 与相近方案的取舍
## 测试/评估方法
## 本次实验结论
## 官方文档与版本日期
```

记录“为什么、何时不该用、如何验证”比只抄 API 更有复习价值。

## 参考

- [LangSmith Observability](https://docs.langchain.com/langsmith/observability)
- [Evaluation concepts](https://docs.langchain.com/langsmith/evaluation-concepts)
- [Test](https://docs.langchain.com/oss/python/langchain/test)
- [Guardrails](https://docs.langchain.com/oss/python/langchain/guardrails)
- [Human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
