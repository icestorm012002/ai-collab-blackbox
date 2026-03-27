# Data Model Reference

## Table of Contents

- [JSONL Record Schema](#jsonl-record-schema)
- [Field Rules](#field-rules)
- [Block Format](#block-format)
- [Block Rendering Rules](#block-rendering-rules)

---

## JSONL Record Schema

每条 JSONL 记录必须遵守以下通用结构:

```json
{
  "ts": "<TIMESTAMP>",
  "ai": "<AI_ID>",
  "feature": "<FEATURE_NAME>",
  "status": "<STATUS>",
  "summary": "<SUMMARY>",
  "work_status": [
    "<WORK_ITEM_1>",
    "<WORK_ITEM_2>"
  ],
  "files": [
    {
      "path": "<FILE_PATH>",
      "lines": "<LINE_INFO>",
      "edit": "<EDIT_SUMMARY>",
      "refs": [
        "<REF_1>",
        "<REF_2>"
      ]
    }
  ]
}
```

## Field Rules

### `ts`
- 必填
- 格式: `YYYY-MM-DD HH:MM:SS`

### `ai`
- 必填
- 必须等于运行时传入的 `AI_ID`
- 不允许模型自行猜测别的 AI 名称

### `feature`
- 必填
- 写项目中的实际功能名

### `status`
- 必填
- 只能是: `done` / `doing` / `blocked` / `failed` / `skipped`

### `summary`
- 必填
- 一句话写清"做了什么 + 为了什么"

### `work_status`
- 可为空数组 `[]`
- 如果本轮来自某个 AI 自己的 todo / plan / checklist，则尽量原文保留
- 每项建议保留完成标记: `[x] ...` / `[ ] ...`

### `files`
- 必填，至少一项

### `files[].path`
- 必填
- 项目内相对路径优先

### `files[].lines`
- 必填
- 可写单行、范围或多段
- 例如: `12` / `12-20` / `12-20,45,80-93`

### `files[].edit`
- 必填
- 对该文件本轮改动的简洁说明

### `files[].refs`
- 可为空数组 `[]`
- 这里的关联必须属于"当前文件自己的关联"
- 不允许把多个文件共用一组无法区分归属的关联项

---

## Block Format

`worklog.md` 中每次追加一个方块，格式必须固定:

```
=== WORKLOG START ===
[<TIMESTAMP>] [<AI_ID>] [<FEATURE_NAME>] [<STATUS>]
<SUMMARY>

工作列表状态:
- <WORK_ITEM_1>
- <WORK_ITEM_2>

文件:
- <FILE_PATH_1> | <LINE_INFO_1> | <EDIT_SUMMARY_1>
  关联:
  - <REF_1>
  - <REF_2>

- <FILE_PATH_2> | <LINE_INFO_2> | <EDIT_SUMMARY_2>
  关联:
  - <REF_1>
  - <REF_2>
=== WORKLOG END ===
```

## Block Rendering Rules

1. **`工作列表状态:` 段可省略** — 仅当 `work_status` 非空时输出。
2. **`文件:` 段必须存在** — 每个文件单独成组。
3. **不能把多个文件共享一组 `关联`。**
4. **`关联:` 段可省略** — 仅当该文件存在 `refs` 时输出。
5. **文件顺序** — 按本轮实际修改顺序或 AI 自己整理后的顺序，同一条记录内部要稳定。
