# Data Model Reference

## Table of Contents

- [JSONL Record Schema](#jsonl-record-schema)
- [Field Rules](#field-rules)
- [Block Format](#block-format)
- [Block Rendering Rules](#block-rendering-rules)

---

## JSONL Record Schema

Each JSONL record must follow the common structure below:

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
- Required
- Format: `YYYY-MM-DD HH:MM:SS`

### `ai`
- Required
- Must be equal to the externally passed `AI_ID` at runtime
- AI must not guess or invent other AI names

### `feature`
- Required
- Write the actual feature/domain name in the project

### `status`
- Required
- Allowed values: `done` / `doing` / `blocked` / `failed` / `skipped`

### `summary`
- Required
- Clarify "what was done + why" in one sentence

### `work_status`
- Can be an empty array `[]`
- If this round stems from a given AI's own todo / plan / checklist, try to retain original text
- Suggest keeping completion markers for each item: `[x] ...` / `[ ] ...`

### `files`
- Required, at least one item

### `files[].path`
- Required
- Relative paths within the project are preferred

### `files[].lines`
- Required
- Can be a single line, range, or multiple blocks
- Example: `12` / `12-20` / `12-20,45,80-93`

### `files[].edit`
- Required
- Concise explanation of modifications made to this file in this round

### `files[].refs`
- Can be an empty array `[]`
- The references here must belong "only to the current file"
- It is prohibited to have multiple files share a generic group of references lacking specific attribution

---

## Block Format

A single text block appended to `worklog.md` must adhere to this fixed format:

```
=== WORKLOG START ===
[<TIMESTAMP>] [<AI_ID>] [<FEATURE_NAME>] [<STATUS>]
<SUMMARY>

Work Status:
- <WORK_ITEM_1>
- <WORK_ITEM_2>

Files:
- <FILE_PATH_1> | <LINE_INFO_1> | <EDIT_SUMMARY_1>
  Refs:
  - <REF_1>
  - <REF_2>

- <FILE_PATH_2> | <LINE_INFO_2> | <EDIT_SUMMARY_2>
  Refs:
  - <REF_1>
  - <REF_2>
=== WORKLOG END ===
```

## Block Rendering Rules

1. **`Work Status:` section is omittable** — Output only when `work_status` is non-empty.
2. **`Files:` section is required** — Every file is grouped separately.
3. **Multiple files cannot share a single `Refs` block.**
4. **`Refs:` section is omittable** — Output only when the file contains `refs`.
5. **File Ordering** — Order must correspond to actual sequence of changes this round or as arranged by the AI, and remaining stable within the identical record.
