# Open Memory Boost

Open Memory Boost 是一个面向 Codex 的本地优先记忆层。

它帮助 AI 助手跨会话记住稳定事实、用户偏好、项目决策和会话摘要，同时不依赖外部记忆服务。

## 为什么要做这个

LLM 擅长推理，但不擅长长期连续性。

Open Memory Boost 提供一套轻量、可审计的记忆流程：

- 记住重要内容
- 忽略一次性噪声
- 将长对话压缩成可复用上下文
- 只召回当前任务真正需要的记忆

## 它做什么

Open Memory Boost 包含两部分：

### 1. Codex Skill

定义记忆工作流：

- 捕获稳定信息
- 分类记忆内容
- 压缩重复或低信号条目
- 在回答前召回相关记忆
- 当用户修正内容时更新记忆

### 2. 本地 Markdown 记忆运行时

一个小型命令行工具，将记忆存储为纯 Markdown 文件。

支持命令：

- `init` - 创建新的记忆库
- `add` - 添加一条记忆
- `search` - 搜索已有记忆
- `list` - 列出所有记忆

## 记忆类型

Open Memory Boost 将信息组织为几个简单类别：

- `Facts`
- `Preferences`
- `Decisions`
- `Open Questions`
- `Session Summaries`

这样能让记忆保持结构化、可读、可审查。

## 核心特性

- 本地优先，可离线使用
- 不需要外部 API
- 使用人类可读的 Markdown 存储
- 提供简单的记忆增删查工具
- 面向稳定、可复用的上下文，而不是原始聊天记录
- 方便审计、备份和纳入 Git 管理

## 工作方式

1. 助手识别对话中的稳定信息。
2. 将这些信息压缩为一条记忆。
3. 记忆写入本地 Markdown 文件。
4. 后续请求时，助手搜索相关记忆。
5. 召回的上下文用于提升连续性和一致性。

## 示例

```powershell
open-memory-boost init
open-memory-boost add facts "User prefers concise answers"
open-memory-boost add preferences "User prefers Chinese responses for local work"
open-memory-boost search concise
open-memory-boost list
```

## 项目结构

```text
open-memory-boost/
├─ skill/
│  ├─ SKILL.md
│  ├─ agents/openai.yaml
│  └─ references/
├─ memory_boost/
│  ├─ cli.py
│  ├─ store.py
│  └─ __main__.py
├─ examples/
├─ README.md
├─ README.zh-CN.md
├─ LICENSE
└─ pyproject.toml
```

## 设计原则

- 保持记忆稳定
- 保持记忆简洁
- 保持记忆显式
- 保持记忆可审计
- 保持记忆本地化

## 适用场景

Open Memory Boost 适合以下需求：

- 记住语气和格式偏好
- 跨会话保存项目决策
- 跟踪持续进行中的工作
- 总结已完成会话
- 在回答前检索相关上下文
- 在不依赖外部服务的前提下维持连续性

## 安装

克隆仓库后，将 `skill/` 目录作为 Codex skill 安装来源。

CLI 需要 Python 3.10+，然后运行：

```powershell
open-memory-boost init
```

## 许可证

MIT
