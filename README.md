# ai-collab-blackbox

[🇨🇳 中文说明 (Chinese Version)](README_zh.md)

> A1 Coder team's collaborative blackbox protocol for AI work handoff.
>
> This repo ships in two layers:
> - a normal project skill folder for AI agents
> - an optional global command that can deploy that skill into any target project and run the built-in logging programs

`ai-collab-blackbox` is not just a document. It includes an actual program layer that validates AI-provided JSON records and writes structured work logs into the project.

---

## What It Is

When multiple AI agents work on the same codebase, each round should leave behind a clean, machine-readable handoff record.

This project provides exactly that:
- append-only work history
- per-AI logs
- a global timeline
- a normal skill folder AI can read inside the project
- script utilities that write the final files safely

---

## Deployment Model

### 1. Normal skill in the project

The actual skill still lives as a normal folder inside the project:

```text
<project>/.agents/skills/ai-collab-blackbox/
```

That folder contains:
- `SKILL.md`
- `SKILL_zh.md`
- `references/`
- `scripts/`

This is the part AI reads and uses in-project.

### 2. Optional global command

If you install the package globally, you get:

```bash
ai-blackbox
```

That command can:
- deploy the skill folder into any target project
- show the bundled skill content
- run the program functions directly:
  - `write`
  - `validate`
  - `render`

So the final model is:
- project-local skill
- global helper command

---

## Install

### Option A: Use as a normal skill only

Copy this directory directly into the target project:

```bash
cp -r ai-collab-blackbox/. <project>/.agents/skills/ai-collab-blackbox/
```

### Option B: Install the global helper command

From source:

```bash
pip install .
```

Or from a packaged release zip/wheel:

```bash
pip install ai-collab-blackbox.zip
```

---

## Global Command Usage

### Deploy the skill into any project

```bash
ai-blackbox init --project-root /path/to/project
```

This creates:

```text
/path/to/project/.agents/skills/ai-collab-blackbox/
```

### Query where the skill would be installed

```bash
ai-blackbox where --project-root /path/to/project
```

### Show command info

```bash
ai-blackbox info
```

### Show the bundled skill text

```bash
ai-blackbox show-skill --lang zh
ai-blackbox show-skill --lang en
```

---

## Program Capabilities

This repo includes real executable logic, not just skill docs.

### Write worklog files

```bash
ai-blackbox write --project-root /path/to/project --file record.json
```

### Validate a JSON / JSONL record

```bash
ai-blackbox validate record.jsonl
```

### Render a readable block log

```bash
ai-blackbox render .ai/claude_opus_4/worklog.jsonl
```

---

## Files Written

For each AI, the protocol writes:

```text
.ai/
├── <AI_ID>/
│   ├── worklog.md
│   └── worklog.jsonl
└── all_time.jsonl
```

---

## Why This Shape

A normal skill alone is readable by AI, but it cannot install itself globally.
A pure CLI alone can run commands, but it is not a normal in-project skill.

So this repo keeps both:
- the skill directory for AI usage
- the global CLI for deployment and direct program execution

This is the cleanest way to support both workflows.

---

## Non-Goals

This project does not:
- parse IDE history automatically
- generate git diffs automatically
- replace git
- invent AI identifiers on its own

---

## License

MIT-0

---

## Author

[@icestomr012002](https://github.com/icestorm012002)
