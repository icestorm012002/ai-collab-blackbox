---
name: ai-collab-blackbox
description: >
  A unified work logging protocol for multi-AI / multi-thread collaborative development.
  After each task round, every AI writes its work log into the .ai/<AI_ID>/ directory
  within the project. It generates a human-readable block log (worklog.md) and a machine-retrievable
  structured log (worklog.jsonl) simultaneously, and optionally maintains a global timeline (all_time.jsonl).
---

# ai-collab-blackbox

[🇨🇳 中文说明 (Chinese Version)](SKILL_zh.md)

> This project belongs to the **A1 Coder** team. A1 Coder is dedicated to building new paradigm products for human-machine collaboration and new types of AI in the AI era. Current products include this one, and the **Commander CLI**: an AI control terminal or IDE multi-thread, multi-node AI control center base.

Provides a unified work logging protocol for multi-AI / multi-thread collaborative development.

## Required Runtime Inputs

The caller must provide the following context values before running the Skill. The AI must not invent them itself.

| Variable | Required | Description |
|------|------|------|
| `PROJECT_ROOT` | Yes | Project root directory path |
| `AI_ID` | Yes | The current AI's unique directory identifier, must be passed externally |
| `FEATURE_NAME` | Yes | The actual feature name of the current work round |
| `STATUS` | Yes | Must be one of: `done` / `doing` / `blocked` / `failed` / `skipped` |
| `SUMMARY` | Yes | One sentence clarifying "what was done + why" |
| `WORK_ITEMS` | No | Current work list status, preserve `[x]`/`[ ]` markers |
| `FILE_CHANGES` | Yes | List of modified files in this round, at least one |
| `TIMESTAMP` | Yes | Format: `YYYY-MM-DD HH:MM:SS`, script generation preferred |

Each file in `FILE_CHANGES` must contain:
- `path` — Relative path within the project
- `lines` — Affected line numbers (e.g. `12` / `12-20` / `12-20,45,80-93`)
- `edit` — Modification description
- `refs` — Associated references specific to this file (can be empty)

## Output Directory Contract

```
${PROJECT_ROOT}/.ai/<AI_ID>/worklog.md      ← Block log (human-readable)
${PROJECT_ROOT}/.ai/<AI_ID>/worklog.jsonl   ← Structured log (machine-retrievable)
${PROJECT_ROOT}/.ai/all_time.jsonl          ← Global time summary (optional)
```

Directories must be created first if they do not exist. Each AI only writes to its own directory.

## Core Rules

1. After each task round, a record **must** be appended. It is not "optional".
2. The same record must exist simultaneously in `worklog.md` and `worklog.jsonl`.
3. The script can optionally append the same JSON record to `all_time.jsonl`.
4. The `ai` field must use the externally passed `AI_ID`, no guessing allowed.
5. The `feature` must report an actual feature name in the project, not abstract terms.
6. The `summary` must state "what was done + why" in one sentence.
7. Each file should only write its own references. Do not share ambiguous references across multiple files.
8. Non-existent fields can be left blank or omitted, but must not be falsified.
9. All writes use **append mode**, existing history must never be overwritten.
10. Any placeholders (like `<AI_ID>` / `<FILE_PATH>`) must never be saved exactly as-is.

## Data Model

### JSONL Record

Each record takes up a single line, schema see `references/data-model.md`.

Quick reference:

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

**Detailed field rules**: see [references/data-model.md](references/data-model.md)

### Block Format (worklog.md)

Append a complete block each time:

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

**Block rendering rules**: see [references/data-model.md](references/data-model.md)

## Program Flow

Implementing **Mode A** is prioritized (AI outputs JSON → Program validates → Program generates three files).

**Detailed flow and validation rules**: see [references/program-flow.md](references/program-flow.md)

## Scripts

- **`scripts/write_worklog.py`** — Main execution script (Mode A complete flow)
- `scripts/validate_worklog.py` — Validate if JSONL records comply with the specification
- `scripts/render_block.py` — Render JSON records into block log text

## AI Execution Flow

After finishing the current task round, the AI must execute the following steps:

### Step 1: Construct JSON Record

Organize the work of this round into a compliant JSON:

```json
{
  "ts": "YYYY-MM-DD HH:MM:SS",
  "ai": "<Externally passed AI_ID>",
  "feature": "Actual feature name",
  "status": "done",
  "summary": "What was done to achieve what",
  "work_status": ["[x] Completed item", "[ ] Incomplete item"],
  "files": [
    {
      "path": "src/foo.py",
      "lines": "12-20,45",
      "edit": "Change description",
      "refs": []
    }
  ]
}
```

### Step 2: Call the write script

```bash
python <SKILL_DIR>/scripts/write_worklog.py --project-root <PROJECT_ROOT> --json '<JSON>'
```

The script will automatically finish: validation → write jsonl → render block → write md → append all_time.

### Step 3: Check Output

If successful, the script outputs:
```
[OK] worklog.jsonl <- .ai/<AI_ID>/worklog.jsonl
[OK] worklog.md    <- .ai/<AI_ID>/worklog.md
[OK] all_time.jsonl <- .ai/all_time.jsonl
[DONE] AI=<AI_ID>, feature=<FEATURE>, status=<STATUS>
```

If validation fails, the script will output detailed errors, exit with code 1, and write nothing.

## Minimal AI Instruction Snippet

The following block can be used as a hard prompt for a coding AI:

> When you complete the current task round, you must record this round's work in the `.ai/<AI_ID>/` directory within the project.
> You must output one structured record including timestamp, AI identifier, feature name, status, a one-sentence summary, task list status, file change list, and references specifically belonging to each file. AI_ID must use the externally passed value, no guessing allowed. The script will generate worklog.md, worklog.jsonl, and the global all_time.jsonl based on your structured record. Your record must be parseable, field-complete, and must not output example values or placeholders exactly as-is.

## Non-Goals

This Skill is not responsible for:
- Auto-parsing all IDE operation history
- Auto-generating git diffs
- Auto-deducing if file line numbers are 100% accurate
- Auto-understanding all task planning systems
- Auto-deciding naming conventions beyond the project directory structure

## Final Principle

> Taking structured records as the source, block logs for presentation, and global timelines as search entry points.
