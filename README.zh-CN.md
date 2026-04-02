# Open Memory Boost

[![CI](https://github.com/156631890/Open-Memory-Boost/actions/workflows/ci.yml/badge.svg)](https://github.com/156631890/Open-Memory-Boost/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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

## 快速开始

```powershell
git clone git@github.com:156631890/Open-Memory-Boost.git
cd Open-Memory-Boost
open-memory-boost init
open-memory-boost add facts "User prefers concise answers"
open-memory-boost search concise
```

## 记忆类型

Open Memory Boost 将信息组织为几个简单类别：

- `Facts`
- `Preferences`
- `Decisions`
- `Open Questions`
- `Session Summaries`

## 项目结构

```text
open-memory-boost/
├─ skill/
├─ memory_boost/
├─ examples/
├─ README.md
├─ README.zh-CN.md
├─ CHANGELOG.md
├─ LICENSE
└─ pyproject.toml
```

## 安装

CLI 需要 Python 3.10+，然后运行：

```powershell
open-memory-boost init
```

## 发布

本仓库的发布流程很简单：

- 更新 changelog
- 打标签
- 从 tag 创建 GitHub Release

## 许可证

MIT
