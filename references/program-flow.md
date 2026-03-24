# Program Flow Reference

## Table of Contents

- [Mode A: AI outputs JSON first (推荐)](#mode-a-ai-outputs-json-first)
- [Mode B: AI outputs block first (兼容)](#mode-b-ai-outputs-block-first)
- [Validation Rules](#validation-rules)
- [Writing Rules](#writing-rules)
- [Search Expectations](#search-expectations)
- [What The AI Must Understand](#what-the-ai-must-understand)

---

## Mode A: AI outputs JSON first

**推荐模式。**

流程:
1. AI 产出一条结构化 JSON
2. 程序校验字段
3. 程序将 JSON 追加到:
   - `worklog.jsonl`
   - `all_time.jsonl`
4. 程序将同一条 JSON 渲染为方块并追加到:
   - `worklog.md`

优点:
- 最稳定
- 最好检索
- 最好校验
- 不怕 AI 方块格式漂移

## Mode B: AI outputs block first

**兼容模式。**

流程:
1. AI 直接输出符合格式的方块文本
2. 程序解析方块
3. 程序转成 JSON
4. 程序写入 `worklog.jsonl` 和 `all_time.jsonl`
5. 如果程序确认方块格式标准，可原样追加到 `worklog.md`
6. 如果方块格式不标准，程序可按解析结果重渲染标准方块再写入

---

## Validation Rules

程序或 Skill 执行器应做以下校验:

| 校验项 | 规则 |
|--------|------|
| `AI_ID` | 不能为空 |
| `STATUS` | 必须在允许值内: `done` / `doing` / `blocked` / `failed` / `skipped` |
| `SUMMARY` | 不能为空 |
| `files` | 至少一项 |
| `files[].path` | 必填 |
| `files[].lines` | 必填 |
| `files[].edit` | 必填 |
| `files[].refs` | 如果存在，必须属于当前文件 |
| 占位符检查 | 任何占位符不得原样落盘 (如 `<AI_ID>`, `<FILE_PATH>`, `<STATUS>`) |

**若校验失败:**
- 不应写入正式日志
- 应返回错误信息给调用方

---

## Writing Rules

1. 所有写入都使用**追加模式**。
2. 不覆盖历史记录。
3. `worklog.md` 追加完整方块。
4. `worklog.jsonl` 每条记录独占一行。
5. `all_time.jsonl` 每条记录独占一行。
6. 如果程序具备能力，建议使用安全追加方式，避免写坏文件。

---

## Search Expectations

后续工具至少应支持基于 `worklog.jsonl` 或 `all_time.jsonl` 的这些筛选:

- 按 AI 查询
- 按功能名查询
- 按状态查询
- 按文件路径查询
- 按时间范围查询
- 按行号关键字查询
- 按任意词搜索

---

## What The AI Must Understand

使用本 Skill 的 AI 必须理解以下要求:

1. 每轮任务完成后，不是"可选记录"，而是"必须记录"。
2. 记录内容必须围绕本轮实际改动，不得空泛。
3. `ai` 字段必须使用外部传入的 `AI_ID`。
4. `feature` 必须写项目中的实际功能名，不写抽象词堆砌。
5. `summary` 必须一句话说明"做了什么 + 为了什么"。
6. 每个文件只写自己的关联项。
7. 没有的字段可留空或省略，但不能伪造。
8. 不得把别的 AI 名称写进自己的日志身份字段。
