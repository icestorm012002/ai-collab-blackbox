# Program Flow Reference

## Table of Contents

- [Mode A: AI outputs JSON first (Recommended)](#mode-a-ai-outputs-json-first)
- [Mode B: AI outputs block first (Compatibility)](#mode-b-ai-outputs-block-first)
- [Validation Rules](#validation-rules)
- [Writing Rules](#writing-rules)
- [Search Expectations](#search-expectations)
- [What The AI Must Understand](#what-the-ai-must-understand)

---

## Mode A: AI outputs JSON first

**Recommended mode.**

Flow:
1. AI outputs a structured JSON record
2. Program validates fields
3. Program appends JSON to:
   - `worklog.jsonl`
   - `all_time.jsonl`
4. Program renders the same JSON as a text block and appends to:
   - `worklog.md`

Pros:
- Most stable
- Best for search/retrieval
- Best for validation
- Immune to AI formatting drift for block text

## Mode B: AI outputs block first

**Compatibility mode.**

Flow:
1. AI outputs block text conforming to format
2. Program parses block
3. Program converts to JSON
4. Program writes to `worklog.jsonl` and `all_time.jsonl`
5. If program confirms block format is standard, append as-is to `worklog.md`
6. If block format is non-standard, program re-renders standard block from parsed results and writes it

---

## Validation Rules

The program or Skill executor must validate the following:

| Item | Rule |
|--------|------|
| `AI_ID` | Cannot be empty |
| `STATUS` | Must be within allowed values: `done` / `doing` / `blocked` / `failed` / `skipped` |
| `SUMMARY` | Cannot be empty |
| `files` | At least one item |
| `files[].path` | Required |
| `files[].lines` | Required |
| `files[].edit` | Required |
| `files[].refs` | If present, must uniquely belong to the current file |
| Placeholder Check | No placeholders should be written as-is (e.g., `<AI_ID>`, `<FILE_PATH>`, `<STATUS>`) |

**If validation fails:**
- Must not write to official logs
- Must return error message to the caller

---

## Writing Rules

1. All writes must use **append mode**.
2. Do not overwrite historical records.
3. `worklog.md` appends complete blocks.
4. `worklog.jsonl` places each record on a single dedicated line.
5. `all_time.jsonl` places each record on a single dedicated line.
6. Programs should use safe-append logic if capable, preventing file corruption.

---

## Search Expectations

Subsequent tools should at least support the following filters based on `worklog.jsonl` or `all_time.jsonl`:

- Query by AI
- Query by feature name
- Query by status
- Query by file path
- Query by time range
- Keyword search by lines
- Full-text arbitrary search

---

## What The AI Must Understand

AI using this Skill must understand the following requirements:

1. After each task round, recording is not "optional", but "mandatory".
2. Records must center around actual changes of the current round. No vague statements.
3. `ai` field must use the externally passed `AI_ID`.
4. `feature` must use the actual feature name from the project, no abstract terms.
5. `summary` must simply state "what was done + why" in one sentence.
6. Each file must only write its own references.
7. Omitted fields can be left empty or missing, but cannot be falsified.
8. Do not write other AI names into your own log identity field.
