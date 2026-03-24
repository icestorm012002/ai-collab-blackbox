#!/usr/bin/env python3
"""
validate_worklog.py — 校验 JSONL 工作日志记录是否符合 ai-collab-blackbox 规范。

Usage:
    python validate_worklog.py <jsonl-file>
    python validate_worklog.py --json '<json-string>'

Exit codes:
    0 — 全部校验通过
    1 — 存在校验错误
"""

import argparse
import json
import re
import sys


VALID_STATUSES = {"done", "doing", "blocked", "failed", "skipped"}

PLACEHOLDER_PATTERNS = [
    re.compile(r"<AI_ID>", re.IGNORECASE),
    re.compile(r"<FILE_PATH>", re.IGNORECASE),
    re.compile(r"<STATUS>", re.IGNORECASE),
    re.compile(r"<TIMESTAMP>", re.IGNORECASE),
    re.compile(r"<FEATURE_NAME>", re.IGNORECASE),
    re.compile(r"<SUMMARY>", re.IGNORECASE),
    re.compile(r"<LINE_INFO>", re.IGNORECASE),
    re.compile(r"<EDIT_SUMMARY>", re.IGNORECASE),
    re.compile(r"<WORK_ITEM_\d+>", re.IGNORECASE),
    re.compile(r"<REF_\d+>", re.IGNORECASE),
]

TS_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")


def check_placeholders(value: str, field_name: str) -> list:
    """Check if a string contains raw placeholder values."""
    errors = []
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(value):
            errors.append(f"[{field_name}] 包含未替换的占位符: {pattern.pattern}")
    return errors


def validate_record(record: dict, line_num: int = 0) -> list:
    """Validate a single JSONL record. Returns list of error strings."""
    errors = []
    prefix = f"Line {line_num}: " if line_num > 0 else ""

    # --- ts ---
    ts = record.get("ts")
    if not ts:
        errors.append(f"{prefix}[ts] 必填字段缺失")
    elif not isinstance(ts, str):
        errors.append(f"{prefix}[ts] 必须是字符串")
    else:
        if not TS_PATTERN.match(ts):
            errors.append(f"{prefix}[ts] 格式错误, 必须是 YYYY-MM-DD HH:MM:SS, 当前: {ts}")
        errors.extend(check_placeholders(ts, f"{prefix}ts"))

    # --- ai ---
    ai = record.get("ai")
    if not ai:
        errors.append(f"{prefix}[ai] 必填字段缺失或为空")
    elif not isinstance(ai, str):
        errors.append(f"{prefix}[ai] 必须是字符串")
    else:
        errors.extend(check_placeholders(ai, f"{prefix}ai"))

    # --- feature ---
    feature = record.get("feature")
    if not feature:
        errors.append(f"{prefix}[feature] 必填字段缺失或为空")
    elif not isinstance(feature, str):
        errors.append(f"{prefix}[feature] 必须是字符串")
    else:
        errors.extend(check_placeholders(feature, f"{prefix}feature"))

    # --- status ---
    status = record.get("status")
    if not status:
        errors.append(f"{prefix}[status] 必填字段缺失或为空")
    elif status not in VALID_STATUSES:
        errors.append(
            f"{prefix}[status] 无效值 '{status}', "
            f"允许值: {', '.join(sorted(VALID_STATUSES))}"
        )

    # --- summary ---
    summary = record.get("summary")
    if not summary:
        errors.append(f"{prefix}[summary] 必填字段缺失或为空")
    elif not isinstance(summary, str):
        errors.append(f"{prefix}[summary] 必须是字符串")
    else:
        errors.extend(check_placeholders(summary, f"{prefix}summary"))

    # --- work_status ---
    work_status = record.get("work_status")
    if work_status is not None:
        if not isinstance(work_status, list):
            errors.append(f"{prefix}[work_status] 必须是数组")
        else:
            for i, item in enumerate(work_status):
                if not isinstance(item, str):
                    errors.append(f"{prefix}[work_status[{i}]] 必须是字符串")
                else:
                    errors.extend(check_placeholders(item, f"{prefix}work_status[{i}]"))

    # --- files ---
    files = record.get("files")
    if not files:
        errors.append(f"{prefix}[files] 必填字段缺失或为空, 至少需要一项")
    elif not isinstance(files, list):
        errors.append(f"{prefix}[files] 必须是数组")
    else:
        if len(files) == 0:
            errors.append(f"{prefix}[files] 至少需要一项")
        for i, f in enumerate(files):
            if not isinstance(f, dict):
                errors.append(f"{prefix}[files[{i}]] 必须是对象")
                continue

            # path
            path = f.get("path")
            if not path:
                errors.append(f"{prefix}[files[{i}].path] 必填字段缺失或为空")
            elif isinstance(path, str):
                errors.extend(check_placeholders(path, f"{prefix}files[{i}].path"))

            # lines
            lines = f.get("lines")
            if not lines:
                errors.append(f"{prefix}[files[{i}].lines] 必填字段缺失或为空")
            elif isinstance(lines, str):
                errors.extend(check_placeholders(lines, f"{prefix}files[{i}].lines"))

            # edit
            edit = f.get("edit")
            if not edit:
                errors.append(f"{prefix}[files[{i}].edit] 必填字段缺失或为空")
            elif isinstance(edit, str):
                errors.extend(check_placeholders(edit, f"{prefix}files[{i}].edit"))

            # refs
            refs = f.get("refs")
            if refs is not None:
                if not isinstance(refs, list):
                    errors.append(f"{prefix}[files[{i}].refs] 必须是数组")
                else:
                    for j, ref in enumerate(refs):
                        if isinstance(ref, str):
                            errors.extend(
                                check_placeholders(ref, f"{prefix}files[{i}].refs[{j}]")
                            )

    return errors


def validate_file(filepath: str) -> int:
    """Validate all records in a JSONL file. Returns number of errors."""
    total_errors = 0
    line_num = 0

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            for line in fh:
                line_num += 1
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"  FAIL Line {line_num}: JSON 解析错误 — {e}")
                    total_errors += 1
                    continue

                errors = validate_record(record, line_num)
                if errors:
                    for err in errors:
                        print(f"  FAIL {err}")
                    total_errors += len(errors)
                else:
                    print(f"  OK   Line {line_num}")

    except FileNotFoundError:
        print(f"  FAIL 文件不存在: {filepath}")
        return 1

    return total_errors


def main():
    parser = argparse.ArgumentParser(
        description="校验 JSONL 工作日志记录是否符合 ai-collab-blackbox 规范"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("file", nargs="?", help="JSONL 文件路径")
    group.add_argument("--json", dest="json_str", help="单条 JSON 字符串")
    args = parser.parse_args()

    print("=== ai-collab-blackbox Validator ===\n")

    if args.json_str:
        try:
            record = json.loads(args.json_str)
        except json.JSONDecodeError as e:
            print(f"  FAIL JSON 解析错误: {e}")
            sys.exit(1)

        errors = validate_record(record)
        if errors:
            for err in errors:
                print(f"  FAIL {err}")
            print(f"\n校验失败: {len(errors)} 个错误")
            sys.exit(1)
        else:
            print("  OK   记录校验通过")
            sys.exit(0)
    else:
        print(f"校验文件: {args.file}\n")
        total = validate_file(args.file)
        if total > 0:
            print(f"\n校验失败: {total} 个错误")
            sys.exit(1)
        else:
            print(f"\n校验通过: 所有记录合规")
            sys.exit(0)


if __name__ == "__main__":
    main()
