#!/usr/bin/env python3
"""
render_block.py — 将 JSON 记录渲染为 ai-collab-blackbox 方块日志格式。

Usage:
    python render_block.py --json '<json-string>'
    python render_block.py <jsonl-file> [--line <N>]

Output:
    标准输出打印渲染后的方块文本。
    可直接追加到 worklog.md。
"""

import argparse
import json
import sys


def render_block(record: dict) -> str:
    """Render a single JSON record into block format."""
    lines = []

    # Header
    lines.append("=== WORKLOG START ===")
    lines.append(
        f"[{record['ts']}] [{record['ai']}] "
        f"[{record['feature']}] [{record['status']}]"
    )
    lines.append(record["summary"])

    # Work status (optional)
    work_status = record.get("work_status", [])
    if work_status:
        lines.append("")
        lines.append("工作列表状态:")
        for item in work_status:
            lines.append(f"- {item}")

    # Files (required)
    files = record.get("files", [])
    if files:
        lines.append("")
        lines.append("文件:")
        for i, f in enumerate(files):
            if i > 0:
                lines.append("")  # blank line between file groups

            path = f.get("path", "")
            file_lines = f.get("lines", "")
            edit = f.get("edit", "")
            lines.append(f"- {path} | {file_lines} | {edit}")

            refs = f.get("refs", [])
            if refs:
                lines.append("  关联:")
                for ref in refs:
                    lines.append(f"  - {ref}")

    lines.append("=== WORKLOG END ===")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="将 JSON 记录渲染为 ai-collab-blackbox 方块日志格式"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("file", nargs="?", help="JSONL 文件路径")
    group.add_argument("--json", dest="json_str", help="单条 JSON 字符串")
    parser.add_argument(
        "--line", type=int, default=0,
        help="渲染 JSONL 文件中第 N 行 (1-indexed，默认渲染全部)"
    )
    args = parser.parse_args()

    if args.json_str:
        try:
            record = json.loads(args.json_str)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}", file=sys.stderr)
            sys.exit(1)
        print(render_block(record))
    else:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    if args.line > 0 and i != args.line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"Line {i}: JSON 解析错误 — {e}", file=sys.stderr)
                        continue
                    if i > 1 and args.line == 0:
                        print()  # blank line between blocks
                    print(render_block(record))
                    if args.line > 0:
                        break
        except FileNotFoundError:
            print(f"文件不存在: {args.file}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
