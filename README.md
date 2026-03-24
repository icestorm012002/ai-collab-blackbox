# ai-collab-blackbox ⬛

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## 🇬🇧 English

> A unified work-logging protocol for multi-AI / multi-thread collaborative development. The flight recorder for your AI agents.

When multiple AI agents work on the same project — each agent logs its own work into a structured, machine-readable file after every task round. Every subsequent AI can instantly know: **who did what, which files were changed, current status, and what's left to do.**

### Why

In multi-AI development workflows, there's no standard way to:
- Track **which AI changed what and why**
- Know **current task status** when handing off between agents
- Record **blocked or failed attempts** (which git never shows)
- Give the next AI **immediate context** without re-reading the whole codebase

`ai-collab-blackbox` is the **flight recorder for your AI agents** — structured, append-only, and searchable.

### How It Works

Each AI appends one record per task round to its own directory:

```text
.ai/
├── <AI_ID>/
│   ├── worklog.md       ← Human-readable block log
│   └── worklog.jsonl    ← Machine-searchable structured log
└── all_time.jsonl       ← Global timeline across all AIs
```

### Quick Start

**1. Install**
Copy the skill into your project:
```bash
cp -r ai-collab-blackbox/. your-project/.agents/skills/ai-collab-blackbox/
```

**2. Log a work record**
```bash
python scripts/write_worklog.py --project-root /path/to/your/project --file record.json
```

*(See [SKILL.md](./SKILL.md) and [references](./references) for detailed JSON schemas)*

---

<a name="中文"></a>
## 🇨🇳 中文

> 为多 AI / 多线程协作开发提供的统一工作记录协议。让您的 AI 智能体拥有专属的“飞行黑匣子”。

当多个 AI 智能体在同一个项目上并行协作时——每个 AI 在每轮任务结束后，都会将自己的工作行为写成结构化的记录。这使得后续接手的每一个 AI 都能瞬间知晓：**谁做了什么，改了哪些文件，任务状态如何，以及还剩下什么待办事项。**

### 为什么需要它？

在多 AI 协同开发工作流中，目前缺乏一套标准规范来解决以下痛点：
- 追踪 **哪个 AI 在什么时候改了什么，原因是什么**
- 在不同智能体间交接任务时，极其精准地传递 **当前任务状态**
- 记录 **受阻或失败的尝试**（传统的 Git Commit 只记录成功结果，无法体现踩坑过程）
- 不必让下一个 AI 耗费资源去重新阅读整个代码库，就能获得 **即时的全局上下文**

`ai-collab-blackbox` 就是您 AI 智能体的 **飞行黑匣子**——高度结构化、仅追加写入、且机器100%可检索。

### 工作原理

每个 AI 在处理完一轮任务后，会将该轮日志写入自己的专属目录：

```text
.ai/
├── <AI_ID>/
│   ├── worklog.md       ← 人类可读的方块日志 (方便人工查阅)
│   └── worklog.jsonl    ← 机器检索的结构化日志 (供 AI 解析)
└── all_time.jsonl       ← 跨所有 AI 的全局工程时间线
```

### 快速上手

**1. 融合进您的项目**
将此技能包复制到您的本地项目中即可：
```bash
cp -r ai-collab-blackbox/. your-project/.agents/skills/ai-collab-blackbox/
```

**2. 记录单次工作日志**
```bash
python scripts/write_worklog.py --project-root /path/to/your/project --file record.json
```

*(查阅 [SKILL.md](./SKILL.md) 和 [references](./references) 以获取包含全部说明的 JSON Schema)*

---

## 🚀 About A1 Coder / 关于 A1 Coder

This project is proudly developed by the **A1 Coder** team. 
本项目由 **A1 Coder** 团队自豪地开发与维护。

**A1 Coder** is dedicated to building new paradigm products for human-machine collaboration in the AI era. 
🔥 **A1 Coder** 致力于打造 AI 时代**人机协作新范式**的杀手级产品。

Our current product ecosystem includes / 我们的核心产品生态包含：
- ⬛ **ai-collab-blackbox**: The unified multi-AI / multi-thread worklog protocol. 
  **(统一的多 AI / 多线程协作日志协议)**
- 💻 **Commander CLI (AI IDE Base)**: A multi-thread, multi-node AI control terminal and IDE foundation for enterprise-grade autonomous development. 
  **(多线程、多节点 AI 控制终端与 IDE 基座，专为企业级全链路自主开发设计)**

---

## License

MIT-0
