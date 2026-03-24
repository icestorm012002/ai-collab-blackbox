---
name: ai-collab-blackbox
description: >
  为多 AI / 多通路协作开发提供统一的工作记录协议。每个 AI 在每轮任务结束后，
  把本轮工作写入项目内 .ai/<AI_ID>/ 目录，同时生成人类可读的方块日志
  (worklog.md) 和机器可检索的结构化日志 (worklog.jsonl)，可选维护全局汇总
  (all_time.jsonl)。Use when: (1) AI 修改代码、新增/删除文件、重构、修复 bug、
  更新配置后记录工作, (2) 完成一组待办中的若干项后记录进度, (3) 任务被阻塞、
  失败或跳过时记录状态, (4) 需要让后续 AI 快速了解谁做了什么、改了哪些文件、
  当前状态和剩余工作, (5) 即使本轮完全没有改动也可记录但必须写清状态。
---

# ai-collab-blackbox

为多 AI / 多通路协作开发提供统一的工作记录协议。

## Required Runtime Inputs

调用方必须在运行 Skill 前提供以下上下文值，AI 不得自行发明。

| 变量 | 必填 | 说明 |
|------|------|------|
| `PROJECT_ROOT` | 是 | 项目根目录路径 |
| `AI_ID` | 是 | 当前 AI 的唯一目录标识，只能由外部传入 |
| `FEATURE_NAME` | 是 | 本轮工作的功能名，必须是项目内实际功能 |
| `STATUS` | 是 | 只能是: `done` / `doing` / `blocked` / `failed` / `skipped` |
| `SUMMARY` | 是 | 一句话同时说明"做了什么 + 为了什么" |
| `WORK_ITEMS` | 否 | 本轮工作列表状态，保留 `[x]`/`[ ]` 标记 |
| `FILE_CHANGES` | 是 | 本轮修改文件列表，至少一条 |
| `TIMESTAMP` | 是 | 格式: `YYYY-MM-DD HH:MM:SS`，程序生成优先 |

`FILE_CHANGES` 每个文件必须包含:
- `path` — 项目内相对路径
- `lines` — 受影响行号 (如 `12` / `12-20` / `12-20,45,80-93`)
- `edit` — 修改说明
- `refs` — 该文件自己的关联项 (可为空)

## Output Directory Contract

```
${PROJECT_ROOT}/.ai/<AI_ID>/worklog.md      ← 方块日志 (人类可读)
${PROJECT_ROOT}/.ai/<AI_ID>/worklog.jsonl   ← 结构化日志 (机器检索)
${PROJECT_ROOT}/.ai/all_time.jsonl          ← 全局时间汇总 (可选)
```

目录不存在时必须先创建。每个 AI 只写自己的目录。

## Core Rules

1. 每轮任务结束后，**必须**追加一条记录，不是"可选"。
2. 同一条记录必须同时存在于 `worklog.md` 和 `worklog.jsonl`。
3. 程序可选地把同一条 JSON 追加到 `all_time.jsonl`。
4. `ai` 字段必须使用外部传入的 `AI_ID`，不允许自行猜测。
5. `feature` 必须写项目中的实际功能名，不写抽象词。
6. `summary` 必须一句话说明"做了什么 + 为了什么"。
7. 每个文件只写自己的关联项，不把多个文件共用无法区分归属的关联项。
8. 没有的字段可留空或省略，但不能伪造。
9. 所有写入都使用**追加模式**，不覆盖历史记录。
10. 任何占位符 (如 `<AI_ID>` / `<FILE_PATH>`) 不得原样落盘。

## Data Model

### JSONL Record

每条记录独占一行，结构见 `references/data-model.md`。

快速参考:

```json
{
  "ts": "YYYY-MM-DD HH:MM:SS",
  "ai": "<AI_ID>",
  "feature": "<FEATURE_NAME>",
  "status": "done",
  "summary": "实现了 X 以支持 Y",
  "work_status": ["[x] 任务A", "[ ] 任务B"],
  "files": [
    {
      "path": "src/foo.py",
      "lines": "12-20,45",
      "edit": "添加了重试逻辑",
      "refs": ["关联到 bar.py 的错误处理"]
    }
  ]
}
```

**字段详细规则**: 见 [references/data-model.md](references/data-model.md)

### Block Format (worklog.md)

每次追加一个完整方块:

```
=== WORKLOG START ===
[YYYY-MM-DD HH:MM:SS] [<AI_ID>] [user-auth] [done]
Implemented login retry logic to improve authentication reliability

Work Items:
- [x] Add retry on timeout
- [ ] Add rate limiting

Files:
- src/auth/login.py | 12-45 | Added retry wrapper
  Refs:
  - Depends on src/auth/base.py abstract interface

- src/config.py | 88 | Added max retry config
=== WORKLOG END ===
```

**方块渲染规则**: 见 [references/data-model.md](references/data-model.md)

## Program Flow

优先实现 **Mode A** (AI 输出 JSON → 程序校验 → 程序生成三份文件)。

**详细流程和校验规则**: 见 [references/program-flow.md](references/program-flow.md)

## Scripts

- **`scripts/write_worklog.py`** — 主执行脚本 (Mode A 完整流程)
  - 接收 JSON → 校验 → 写入 `worklog.jsonl` → 渲染方块写入 `worklog.md` → 追加 `all_time.jsonl`
- `scripts/validate_worklog.py` — 校验 JSONL 记录是否符合规范
- `scripts/render_block.py` — 将 JSON 记录渲染为方块日志文本

## AI Execution Flow

每轮任务结束后，AI 必须执行以下步骤:

### Step 1: 构造 JSON 记录

将本轮工作整理为一条符合规范的 JSON:

```json
{
  "ts": "YYYY-MM-DD HH:MM:SS",
  "ai": "<外部传入的 AI_ID>",
  "feature": "实际功能名",
  "status": "done",
  "summary": "做了什么以实现什么",
  "work_status": ["[x] 已完成项", "[ ] 未完成项"],
  "files": [
    {
      "path": "src/foo.py",
      "lines": "12-20,45",
      "edit": "改动说明",
      "refs": []
    }
  ]
}
```

### Step 2: 调用写入脚本

```bash
python <SKILL_DIR>/scripts/write_worklog.py --project-root <PROJECT_ROOT> --json '<JSON>'
```

脚本会自动完成: 校验 → 写入 jsonl → 渲染方块 → 写入 md → 追加 all_time

### Step 3: 确认输出

脚本成功后会输出:
```
[OK] worklog.jsonl <- .ai/<AI_ID>/worklog.jsonl
[OK] worklog.md    <- .ai/<AI_ID>/worklog.md
[OK] all_time.jsonl <- .ai/all_time.jsonl
[DONE] AI=<AI_ID>, feature=<FEATURE>, status=<STATUS>
```

若校验失败，脚本会输出错误详情并以 exit code 1 退出，不写入任何文件。

## Minimal AI Instruction Snippet

下面这段可以直接给编程 AI 当作硬提示:

> 当你完成当前轮任务后，必须把本轮工作记录到项目内 `.ai/<AI_ID>/` 目录下。
> 你必须输出一条结构化记录，包含时间、AI 标识、功能名、状态、一句话总结、
> 工作列表状态、文件改动列表，以及每个文件自己的关联项。AI_ID 必须使用外部
> 传入值，不允许自行猜测。程序会基于你的结构化记录生成 worklog.md、
> worklog.jsonl 和全局 all_time.jsonl。你的记录必须可解析、字段完整、
> 不得使用示例值或占位符原样输出。

## Non-Goals

本 Skill 不负责:
- 自动解析 IDE 所有操作历史
- 自动生成 git diff
- 自动推断真实行号是否百分百准确
- 自动理解所有任务规划系统
- 自动决定项目目录结构以外的命名规范

## Final Principle

> 以结构化记录为源，以方块日志为展示，以全局时间线为检索入口。
