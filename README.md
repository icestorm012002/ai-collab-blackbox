# ai-collab-blackbox

> A unified work-logging protocol for multi-AI / multi-agent collaborative development.

When multiple AI agents work on the same project — each agent logs its own work into a structured, machine-readable file after every task round. Every subsequent AI can instantly know: **who did what, which files were changed, current status, and what's left to do.**

---

## Why

In multi-AI development workflows, there's no standard way to:
- Track **which AI changed what and why**
- Know **current task status** when handing off between agents
- Record **blocked or failed attempts** (which git never shows)
- Give the next AI **immediate context** without re-reading the whole codebase

`ai-collab-blackbox` is the **flight recorder for your AI agents** — structured, append-only, and searchable.

---

## How It Works

Each AI appends one record per task round to its own directory:

```
.ai/
├── <AI_ID>/
│   ├── worklog.md       ← Human-readable block log
│   └── worklog.jsonl    ← Machine-searchable structured log
└── all_time.jsonl       ← Global timeline across all AIs
```

**Mode A (recommended):** AI outputs structured JSON → script validates → writes all 3 files automatically.

---

## Quick Start

### 1. Install

Copy the skill into your project or install as an OpenClaw skill:

```bash
# Copy skill files
cp -r ai-collab-blackbox/.  your-project/.agents/skills/ai-collab-blackbox/
```

### 2. Log a work record

Prepare a JSON record and run the write script:

```bash
python scripts/write_worklog.py \
  --project-root /path/to/your/project \
  --file record.json
```

Example `record.json`:

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

Output:
```
[OK] worklog.jsonl <- .ai/claude_opus_4/worklog.jsonl
[OK] worklog.md    <- .ai/claude_opus_4/worklog.md
[OK] all_time.jsonl <- .ai/all_time.jsonl
[DONE] AI=claude_opus_4, feature=user-auth, status=done
```

### 3. Validate a log file

```bash
python scripts/validate_worklog.py .ai/claude_opus_4/worklog.jsonl
```

### 4. Render a block from JSONL

```bash
python scripts/render_block.py .ai/claude_opus_4/worklog.jsonl
```

---

## Data Model

### JSONL Record Schema

| Field | Required | Description |
|-------|----------|-------------|
| `ts` | ✅ | Timestamp: `YYYY-MM-DD HH:MM:SS` |
| `ai` | ✅ | AI identifier — must be externally provided, never self-invented |
| `feature` | ✅ | Actual feature/domain name in the project |
| `status` | ✅ | `done` / `doing` / `blocked` / `failed` / `skipped` |
| `summary` | ✅ | One sentence: "what was done + why" |
| `work_status` | ➖ | Task checklist with `[x]`/`[ ]` markers |
| `files` | ✅ | List of changed files (min 1) |
| `files[].path` | ✅ | Relative path within project |
| `files[].lines` | ✅ | Affected lines: `12` / `12-20` / `12-20,45` |
| `files[].edit` | ✅ | Description of the change |
| `files[].refs` | ➖ | References specific to this file |

### Block Format (`worklog.md`)

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

## Core Rules

1. **Mandatory** — every AI must log after every task round, no exceptions
2. **Append-only** — never overwrite history
3. **AI_ID from outside** — AI must never invent its own identifier
4. **One record = three files** — `worklog.md` + `worklog.jsonl` + `all_time.jsonl`
5. **No raw placeholders** — `<AI_ID>`, `<FILE_PATH>` etc. must never appear in actual logs
6. **Per-file refs** — each file's `refs` only contains references for that file

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write_worklog.py` | **Main runner** — validate + write all 3 log files |
| `scripts/validate_worklog.py` | Validate a JSONL record or file |
| `scripts/render_block.py` | Render JSONL record(s) into block format |

---

## OpenClaw / AgentSkill Compatible

This skill follows the [AgentSkills](https://openclaw.ai) format and can be used directly as an OpenClaw skill. The `SKILL.md` file contains the full protocol specification for AI agents.

---

## Non-Goals

This skill does **not**:
- Auto-parse IDE operation history
- Auto-generate git diffs
- Guarantee line number accuracy
- Replace git — it complements it

---

## License

MIT-0 — do whatever you want.

---

## Author

[@icestomr012002](https://github.com/icestomr012002)
