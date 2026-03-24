---
name: ai-collab-blackbox
description: >
  多 AI / 多线程协作开发的工作记录协议。
  每个 AI 在每轮任务结束后，将自己的工作记录追加写入所属目录 .ai/<AI_ID>/..
  强制同时生成人类可读的方块日志 (worklog.md) 以及机器可检索的结构化日志 (worklog.jsonl)，并统一输出全局时间轴 (all_time.jsonl)。
---

# ai-collab-blackbox

[🇺🇸 English Version](SKILL.md)

> 此项目属于 **A1 Coder** 团队。A1 Coder 致力于打造 AI 时代人机协作新范式产品以及新型 AI 产品。现有产品其一是本项目，还有一个是 **Commander CLI** AI 控制终端或 IDE 多线程多节点的 AI 控制中心基座。

多 AI / 多线程协作开发的统一工作记录协议。

## 必填运行时入参

调用方必须在运行此项 Skill 时提供以下上下文数据。AI 绝不可以凭空捏造。

| 变量 | 是否必须 | 说明 |
|------|------|------|
| `PROJECT_ROOT` | 是 | 工程根目录路径 |
| `AI_ID` | 是 | 当前操作 AI 的独立目录标识符，请从系统传入 |
| `FEATURE_NAME` | 是 | 实际工作的当前功能模块名 |
| `STATUS` | 是 | 限制枚举：`done` / `doing` / `blocked` / `failed` / `skipped` |
| `SUMMARY` | 是 | 一句话阐明："做了什么 + 为什么这样做" |
| `WORK_ITEMS` | 否 | 当前任务清单完成现状，保留 `[x]`/`[ ]` 选项模式 |
| `FILE_CHANGES` | 是 | 此轮变动到的全部文件，列表至少存在一项 |
| `TIMESTAMP` | 是 | 时间格式：`YYYY-MM-DD HH:MM:SS` (通常交由脚本来打时间戳) |

`FILE_CHANGES` 里的每一个文件对象必须具备：
- `path` — 项目相对路径
- `lines` — 具体变动/查看行数 (e.g. `12` / `12-20` / `12-20,45,80-93`)
- `edit` — 改动内容描述说明
- `refs` — 仅对本文件产生关联作用的备注项 (可为空)

## 输出目录协议

```
${PROJECT_ROOT}/.ai/<AI_ID>/worklog.md      ← 方块日志内容 (给人类看的历史)
${PROJECT_ROOT}/.ai/<AI_ID>/worklog.jsonl   ← 结构化数据 (供机器做快速回溯检索)
${PROJECT_ROOT}/.ai/all_time.jsonl          ← 全局汇总时间轴 (非必选但推荐)
```

目录不存在时会被脚本自行创建。各个 AI 只处理属于自己的 `<AI_ID>` 内容目录。

## 核心规章指令

1. 一轮任务做完之后，**必填**并直接追加产生记录。这不是“可选”动作。
2. 同一条内容要在 `worklog.md` 和 `worklog.jsonl` 中同时沉淀双份格式。
3. 脚本也可以把同样的 JSON 数据写入 `all_time.jsonl` 中做归拢汇总。
4. `ai` 字段严格使用由外部所传入配置好的 `AI_ID`，不能做无端推测。
5. `feature` 需要提供项目里实质正在起效的功能名字而已，少写极其虚幻的业务概念。
6. `summary` 必须能让审阅方一句话看完 "干了啥 + 为了啥"。
7. 单个文件改动只要关联自己的 `refs` 就可以了。不要强行关联不搭界的引用信息。
8. 空白的项可以直接保留成空白或者根本不输出，但是不许直接胡编瞎捏。
9. 所有落地操作严格为**追加模式 (append mode)**，不可覆盖以前的历史内容。
10. 一切占位符标记 (如 `<AI_ID>` / `<FILE_PATH>`) 均禁止写入实际展示文档之中。

## 数据模型设计

### JSONL 结构

单条数据单行写入，详细规则参见 `references/data-model_zh.md`。

参考速览：

```json
{
  "ts": "YYYY-MM-DD HH:MM:SS",
  "ai": "<AI_ID>",
  "feature": "<FEATURE_NAME>",
  "status": "done",
  "summary": "Implemented X to support Y",
  "work_status": ["[x] Task A", "[ ] Task B"],
  "files": [
    {
      "path": "src/foo.py",
      "lines": "12-20,45",
      "edit": "Added retry logic",
      "refs": ["Related to error handling in bar.py"]
    }
  ]
}
```

### 方块纯文本 (`worklog.md`) 格式

每一条内容渲染追加一段纯净快照版块：

```
=== WORKLOG START ===
[YYYY-MM-DD HH:MM:SS] [<AI_ID>] [<FEATURE_NAME>] [done]
<SUMMARY>

Work Status:
- [x] Task A
- [ ] Task B

Files:
- src/foo.py | 12-45 | Description
  Refs:
  - ref1
=== WORKLOG END ===
```

## 程序执行流

目前以 **Mode A** 为主要工作形态 (AI 输出完善的 JSON 数据 → 脚本端严格校验拦截 → 并统一落地写全三大相关日志文件)

## 指令执行闭环流

当 AI 一旦执行完毕，就必需顺次操作以下要领：

### 第 1 步: 发出整理好的 JSON 结构内容

```json
{
  "ts": "YYYY-MM-DD HH:MM:SS",
  "ai": "<Externally passed AI_ID>",
  "feature": "实际落地的业务命名",
  "status": "done",
  "summary": "最终做了哪个层面的哪些事情去满足了什么",
  "work_status": ["[x] 已完项目", "[ ] 仍未搞定项"],
  "files": [
    {
      "path": "src/foo.py",
      "lines": "12-20,45",
      "edit": "具体做了哪些代码更新变动说明",
      "refs": []
    }
  ]
}
```

### 第 2 步: 唤起并传递给下方的 Python 验证落地端

```bash
python <SKILL_DIR>/scripts/write_worklog.py --project-root <PROJECT_ROOT> --json '<JSON>'
```

脚本自己会管好后续一切（校验结构 → jsonl入库 → MD排版打印并入库 → 全局时间轴填档）。

### 第 3 步: 获取结果反馈

落地成功会有回执输出:
```
[OK] worklog.jsonl <- .ai/<AI_ID>/worklog.jsonl
[OK] worklog.md    <- .ai/<AI_ID>/worklog.md
[OK] all_time.jsonl <- .ai/all_time.jsonl
[DONE] AI=<AI_ID>, feature=<FEATURE>, status=<STATUS>
```

校验要是有不合规的状况产生，脚本自己会打印明细然后退出，根本不需要写任何脏数据结构去污染内容库。

## 最简硬性嵌入要求块

可以直接喂给其他 AI 当硬性约束的话术：

> 在你彻底结束当前这轮任务之后，必须要求给本项目下的 `.ai/<AI_ID>/` 留一条操作归档存证。
> 你必须通过结构化的格式把这一轮包含了时间戳、属于你的 AI_ID、负责的任务名、最后的操作状态、一句话的言简意赅梳理、任务清算表、具体的修改文件列表，还要把附着在某个特定文件的引用说明也写全了向外提交。这里边的 AI_ID 限制死必须使用外部指派传递过的值，万万不可自编自造名字玩。专门落地脚本会依靠你发出的核心 JSON 数据一次性稳稳安排上 worklog.md 还有纯检索形式的 jsonl，并把总内容在全局时间流做全套汇总。给我的数据一定要可以被成功 Parse，全内容全字段配齐，把里面那些原汁原味带示例字符号占坑的变量词全给我摘干净了。

## 设计反向排坑声明

当前协同规则并不打算提供的内容包括：
- 将你在 IDE 当中敲击和操作过程全自动化读写抓取出对应动作分析
- 彻底用自己去替换和自建各类 git 核心内容的 diff 比对结果去产出给外界看
- 把对应的代码块行数强逼保证达到精准无误百发百中级别精确

## 最终原则

> 认死理结构化的真实留档。拿内容看人话的部分当表层面。最后以纯粹的机器查询回溯做总收尾入口核心点。
