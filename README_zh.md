# ai-collab-blackbox

[🇺🇸 English Version](README.md)

> 为多 AI / 多智能体协作开发提供的统一工作记录协议。
>
> 此项目属于 **A1 Coder** 团队。A1 Coder 致力于打造 AI 时代人机协作新范式产品以及新型 AI 产品。现有产品其一是本项目，还有一个是 **Commander CLI** AI 控制终端或 IDE 多线程多节点的 AI 控制中心基座。

当多个 AI 智能体在同一个项目上协作时——每个 AI 在每轮任务结束后，都会将自己的工作记录追加到一个结构化的、机器可读的文件中。后续接手的每一个 AI 都能瞬间知晓：**谁做了什么，改了哪些文件，当前状态如何，以及还剩下什么待办事项。**

---

## 为什么需要它

在多 AI 协同工作流中，目前没有标准的方法来：
- 追踪 **哪个 AI 改了什么内容，原因是什么**
- 在智能体间交接完毕时，确切获知 **当前的精确状态**
- 记录 **受阻或失败的尝试**（传统的 git 记录中无法展现这一点）
- 给接手的下一个 AI **提供即时的上下文**，而不必让它重新阅读整个代码库

`ai-collab-blackbox` 是位于您 AI 智能体之中的 **飞行黑匣子**——高度结构化，仅追加写入，并且可以直接被检索。

---

## 工作机制

每个 AI 在每轮任务结束后将单条记录追加写入自己的目录下：

```
.ai/
├── <AI_ID>/
│   ├── worklog.md       ← 人类可读的方块日志记录
│   └── worklog.jsonl    ← 机器可检索的结构化日志
└── all_time.jsonl       ← 跨越所有协作 AI 的全局时间轴
```

**Mode A (推荐):** AI 输出完整的结构化 JSON → 传递给脚本执行校验 → 自动化生成并写入 3 份对应文件。

---

## 快速开始

### 1. 安装

将此技能包全部复制到您的项目中或以 OpenClaw 的 skill 直接安装：

```bash
# 复制技能目录文件
cp -r ai-collab-blackbox/.  your-project/.agents/skills/ai-collab-blackbox/
```

### 2. 记录工作日志

提前准备好一份 JSON 记录并通过运行写入脚本执行落地：

```bash
python scripts/write_worklog.py \
  --project-root /path/to/your/project \
  --file record.json
```

示例数据的 `record.json`：

```json
{
  "ts": "2026-03-24 12:00:00",
  "ai": "claude_opus_4",
  "feature": "user-auth",
  "status": "done",
  "summary": "Implemented login retry logic to improve auth reliability",
  "work_status": [
    "[x] Add retry on timeout",
    "[ ] Add rate limiting"
  ],
  "files": [
    {
      "path": "src/auth/login.py",
      "lines": "12-45",
      "edit": "Added retry wrapper with exponential backoff",
      "refs": ["Depends on src/auth/base.py abstract interface"]
    }
  ]
}
```

输出反馈：
```
[OK] worklog.jsonl <- .ai/claude_opus_4/worklog.jsonl
[OK] worklog.md    <- .ai/claude_opus_4/worklog.md
[OK] all_time.jsonl <- .ai/all_time.jsonl
[DONE] AI=claude_opus_4, feature=user-auth, status=done
```

### 3. 校验日志文件

```bash
python scripts/validate_worklog.py .ai/claude_opus_4/worklog.jsonl
```

### 4. 纯净渲染 JSONL 的块级信息

```bash
python scripts/render_block.py .ai/claude_opus_4/worklog.jsonl
```

---

## 数据模型

### JSONL 结构参考说明

| 字段 | 必须项 | 基本说明 |
|-------|----------|-------------|
| `ts` | ✅ | 时间戳约束规范：`YYYY-MM-DD HH:MM:SS` |
| `ai` | ✅ | AI 身份识别符 — 要求从外部获得提供，坚决不可 AI 自己乱造 |
| `feature` | ✅ | 对应项目中实际涉及的模块或功能名称 |
| `status` | ✅ | 取值限定：`done` / `doing` / `blocked` / `failed` / `skipped` |
| `summary` | ✅ | 简短描述："改动操作了什么 + 核心目的是什么" |
| `work_status` | ➖ | 目前待办清单（采用经典 `[x]`/`[ ]` ） |
| `files` | ✅ | 改动的文件内容数组 (最少为 1 项内容) |
| `files[].path` | ✅ | 文件基于项目的相对结构路径 |
| `files[].lines` | ✅ | 受波及关联的行段落：`12` / `12-20` / `12-20,45` |
| `files[].edit` | ✅ | 对这次更改情况的简介说明 |
| `files[].refs` | ➖ | 针对该单一文件，所引用的参考内容情况 |

### 日志方块形态 (`worklog.md`)

```
=== WORKLOG START ===
[2026-03-24 12:00:00] [claude_opus_4] [user-auth] [done]
Implemented login retry logic to improve auth reliability

Work Items:
- [x] Add retry on timeout
- [ ] Add rate limiting

Files:
- src/auth/login.py | 12-45 | Added retry wrapper
  Refs:
  - Depends on src/auth/base.py abstract interface
=== WORKLOG END ===
```

---

## 核心规章指令

1. **绝对强制** — 每一轮工作结束时必须执行反馈式记录，没有任何例外情况
2. **纯粹追加** — 坚决不要覆盖之前的历史时间内容
3. **AI_ID 外围注入** — AI 绝不可伪造其自身名号
4. **单次写入包含其三** — `worklog.md` + `worklog.jsonl` + `all_time.jsonl` 
5. **严禁遗留原始填充码** — 例如占位文本 `<AI_ID>`, `<FILE_PATH>` 等禁止保留成实际呈现
6. **文件归属单立 refs** — 该文件的 `refs` 限定反映该文件的直接引用内容范围

---

## 基础脚本集

| 脚本说明 | 操作应用目的 |
|--------|---------|
| `scripts/write_worklog.py` | **主运转核心** — 完成验证并协同落地三份记录内容 |
| `scripts/validate_worklog.py` | 查证单项或单文件的内部合规性内容检测 |
| `scripts/render_block.py` | 可靠地将对应内容的记录向纯文本日志板块模式内靠齐 |

---

## 全局框架一致性与兼容机制

该记录机制遵守 [AgentSkills](https://openclaw.ai) 的技术底层格式可以顺畅进入 OpenClaw 的 skill 层。而文件夹对应的 `SKILL_zh.md` 会承载向不同 AI 发送全量说明约束的全部协议范本集。

---

## 不在设计意图内

当前的协同技术**绝不去涉及**的内容为：
- 读取/拦截任何操作产生的直接历史内容痕迹
- 去自动生产及导出 Git 操作内的对应比较说明
- 基于完全对准确文件内具体精准的修改行实现死磕
- 更换替代掉 git 本身 — 它的核心是成为针对 Git 内容的重要协同插件与补齐模块

---

## 开源协议许可

MIT-0 — 随你所愿，不加限制。

---

## 作者信息登记

[@icestomr012002](https://github.com/icestomr012002)
