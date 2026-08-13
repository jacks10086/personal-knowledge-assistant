# 个人知识助手

> 当前状态：**旧版 v0.1 基线，等待从 Day 6 开始按模块重建**。

## 项目目标

使用 Python 手写生产导向的 Agent Harness，并以本地个人学习资料作为真实业务场景。第一阶段最终链路：

```text
本地资料
→ 导入与切分
→ 本地检索
→ KnowledgeSearchTool
→ 基于证据回答并返回引用
→ Session / Trace
→ 自动化测试与评估
→ CLI / FastAPI / Docker
```

开发路线和个人学习记录保存在独立私密仓库，不随本公开项目发布。公开仓库只维护项目代码、测试和技术文档。

## 当前代码说明

`agent.py` 是 Day 1 阶段主要由 AI 生成的单文件原型，现保留为“改造前”对照基线。它目前包含：

- OpenAI-compatible DeepSeek 调用；
- 多轮消息和简单滑动窗口；
- 计算器、当前时间、文件读取工具；
- Agent Loop 和 CLI；
- 调试输出。

它**不是生产级实现**，已知问题包括：

- Provider、Agent Loop、Tool、CLI 混在一个文件；
- `calculate` 使用 `eval`；
- `read_file` 没有 `knowledge_root` 沙箱；
- 缺少正式 Provider Protocol、Typed Event、Session 和 Trace；
- 现有 `test.py`、`test_api.py`、`test_window.py` 是手工脚本，不是完整 pytest 套件；
- 错误、超时、重试、取消、日志脱敏和持久化尚未系统实现。

从 Day 6 起不继续向 `agent.py` 堆核心功能，而是在新模块中由学习者亲手实现 Harness。

## 运行旧基线

前提：本地 `.env` 已配置模型相关环境变量。

```powershell
cd "D:\code\claude code\ai-agent-book\my-learning\projects\personal-knowledge-assistant"
python agent.py
```

> `.env` 和个人数据不得提交 Git。文件读取工具当前不安全，只能在了解风险的情况下用于旧版观察实验。

## 新 Harness 目标结构

目录只随功能逐步创建，不一次生成空架子：

```text
src/knowledge_assistant/
├── core/          # Message、Event、Provider、Tool、Agent Loop
├── providers/     # DeepSeekProvider、ScriptedProvider
├── session/       # 内存 Session、JSONL
├── storage/       # SQLite
├── retrieval/     # keyword、vector、service
├── tools/         # filesystem、knowledge_search
├── application.py
├── cli.py
├── api.py
└── config.py

tests/
├── unit/
├── integration/
└── evals/
```

## 第一阶段边界

必须做：

- 本地单用户；
- 安全文件访问；
- Provider 抽象与 ScriptedProvider；
- 异步 Agent Loop 和事件流；
- Session、Trace、JSONL、SQLite；
- 关键词基线与最小本地向量检索；
- 引用、拒答、测试和评估；
- CLI、FastAPI、Docker、README。

暂不做：

- 前端、登录、RBAC、多用户和多租户；
- Redis、Celery、微服务和 Kubernetes；
- 任意 Shell/Python 执行；
- 多 Agent、GraphRAG、Reranker、专用向量数据库；
- 第一阶段 Pi 二次开发项目。

## 学习与开发分工

- 学习者亲手设计和实现核心 Harness；
- AI 按项目问题定位书、Tau、Pi 和 Python 资料；
- AI 编写大部分测试样板、Mock、故障用例并执行代码审查；
- 核心逻辑失败时，由学习者理解原因并修改；
- 每个功能以“能运行、能验证、能讲清”验收。
