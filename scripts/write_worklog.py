#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
write_worklog.py — ai-collab-blackbox 的主执行脚本 (Mode A)

完整流程:
  AI 输出 JSON → 校验 → 写入 worklog.jsonl → 渲染方块写入 worklog.md → 追加 all_time.jsonl

Usage:
    # 从 stdin 读取 JSON
    echo '{"ts":"...","ai":"...","feature":"...","status":"done","summary":"...","work_status":[],"files":[...]}' | python write_worklog.py --project-root <PROJECT_ROOT>

    # 从命令行参数传入 JSON
    python write_worklog.py --project-root <PROJECT_ROOT> --json '<JSON_STRING>'

    # 从文件读取 JSON
    python write_worklog.py --project-root <PROJECT_ROOT> --file <JSON_FILE>

    # 跳过 all_time.jsonl
    python write_worklog.py --project-root <PROJECT_ROOT> --json '...' --no-global

Exit codes:
    0 — 写入成功
    1 — 校验失败或写入错误
"""

import argparse
import json
import os
import sys
from datetime import datetime

# 导入同目录下的 validate 和 render 模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from validate_worklog import validate_record
from render_block import render_block


def safe_append(filepath: str, content: str) -> None:
    """安全追加写入文件。确保内容以换行结尾。"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if not content.endswith("\n"):
        content += "\n"

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)


def ensure_timestamp(record: dict) -> dict:
    """如果记录没有 ts 字段，自动填充当前时间。"""
    if not record.get("ts"):
        record["ts"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return record


def write_worklog(record: dict, project_root: str, write_global: bool = True) -> None:
    """
    执行完整的 Mode A 写入流程:
    1. 校验 JSON 记录
    2. 写入 worklog.jsonl
    3. 渲染方块并写入 worklog.md
    4. (可选) 追加到 all_time.jsonl
    """
    # 自动补 timestamp
    record = ensure_timestamp(record)

    # --- Step 1: 校验 ---
    errors = validate_record(record)
    if errors:
        print("[FAIL] validation failed:\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        print(f"\n{len(errors)} error(s), nothing written.", file=sys.stderr)
        sys.exit(1)

    ai_id = record["ai"]
    ai_dir = os.path.join(project_root, ".ai", ai_id)
    jsonl_path = os.path.join(ai_dir, "worklog.jsonl")
    md_path = os.path.join(ai_dir, "worklog.md")
    global_path = os.path.join(project_root, ".ai", "all_time.jsonl")

    # --- Step 2: 写入 worklog.jsonl ---
    json_line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    safe_append(jsonl_path, json_line)
    print(f"[OK] worklog.jsonl <- {jsonl_path}")

    # --- Step 3: 渲染方块并写入 worklog.md ---
    block = render_block(record)
    safe_append(md_path, "\n" + block + "\n")
    print(f"[OK] worklog.md    <- {md_path}")

    # --- Step 4: 追加到 all_time.jsonl ---
    if write_global:
        safe_append(global_path, json_line)
        print(f"[OK] all_time.jsonl <- {global_path}")
    else:
        print(f"[SKIP] all_time.jsonl (--no-global)")

    print(f"\n[DONE] AI={ai_id}, feature={record['feature']}, status={record['status']}")


def main():
    parser = argparse.ArgumentParser(
        description="ai-collab-blackbox 主执行脚本: JSON → 校验 → 写入三份日志文件"
    )
    parser.add_argument(
        "--project-root", required=True,
        help="项目根目录路径 (PROJECT_ROOT)"
    )

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--json", dest="json_str",
        help="JSON 字符串 (单条记录)"
    )
    input_group.add_argument(
        "--file", dest="json_file",
        help="包含 JSON 的文件路径"
    )

    parser.add_argument(
        "--no-global", action="store_true",
        help="不写入 all_time.jsonl"
    )

    args = parser.parse_args()

    # 读取 JSON 输入
    if args.json_str:
        raw = args.json_str
    elif args.json_file:
        try:
            with open(args.json_file, "r", encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            print(f"[FAIL] file not found: {args.json_file}", file=sys.stderr)
            sys.exit(1)
    else:
        # 从 stdin 读取
        if sys.stdin.isatty():
            print("Waiting for JSON from stdin (Ctrl+Z to end)...", file=sys.stderr)
        raw = sys.stdin.read()

    raw = raw.strip()
    if not raw:
        print("[FAIL] no JSON input received", file=sys.stderr)
        sys.exit(1)

    try:
        record = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    # 执行写入
    write_worklog(
        record=record,
        project_root=args.project_root,
        write_global=not args.no_global,
    )


if __name__ == "__main__":
    main()
