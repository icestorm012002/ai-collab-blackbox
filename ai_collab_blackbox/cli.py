from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from .bundled_resources import PACKAGE_NAME, iter_reference_names, read_reference, read_text


def _target_skill_dir(project_root: Path) -> Path:
    return project_root / ".agents" / "skills" / PACKAGE_NAME


def _safe_print_text(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
        if not text.endswith("\n"):
            sys.stdout.buffer.write(b"\n")


def _copy_bundled_skill(target_dir: Path, force: bool = False) -> None:
    if target_dir.exists() and any(target_dir.iterdir()) and not force:
        raise FileExistsError(f"target already exists: {target_dir}")

    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "references").mkdir(parents=True, exist_ok=True)
    (target_dir / "scripts").mkdir(parents=True, exist_ok=True)

    for name in ("SKILL.md", "SKILL_zh.md", "README.md", "README_zh.md"):
        (target_dir / name).write_text(read_text(name), encoding="utf-8")

    for ref_name in iter_reference_names():
        (target_dir / "references" / ref_name).write_text(
            read_reference(ref_name),
            encoding="utf-8",
        )

    package_root = Path(__file__).resolve().parent.parent
    source_scripts = package_root / "scripts"
    for item in source_scripts.iterdir():
        if item.name == "__pycache__":
            continue
        dst = target_dir / "scripts" / item.name
        if item.is_dir():
            shutil.copytree(item, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dst)


def cmd_init(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root or os.getcwd()).resolve()
    target_dir = _target_skill_dir(project_root)
    _copy_bundled_skill(target_dir, force=args.force)
    print(target_dir)
    return 0


def cmd_where(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root or os.getcwd()).resolve()
    target_dir = _target_skill_dir(project_root)
    print(target_dir)
    return 0


def cmd_info(_: argparse.Namespace) -> int:
    print("name: ai-collab-blackbox")
    print("mode: global-cli + project-skill")
    print("project_install_path: .agents/skills/ai-collab-blackbox")
    print("commands: init, where, info, show-skill, write, validate, render")
    return 0


def cmd_show_skill(args: argparse.Namespace) -> int:
    name = "SKILL_zh.md" if args.lang == "zh" else "SKILL.md"
    _safe_print_text(read_text(name))
    return 0


def cmd_write(args: argparse.Namespace) -> int:
    from scripts.write_worklog import main as write_main

    sys.argv = [
        "write_worklog.py",
        "--project-root",
        args.project_root,
        "--file",
        args.file,
    ]
    if args.no_global:
        sys.argv.append("--no-global")
    write_main()
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    from scripts.validate_worklog import main as validate_main

    if args.json:
        sys.argv = ["validate_worklog.py", "--json", args.json]
    else:
        sys.argv = ["validate_worklog.py", args.file]
    validate_main()
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    from scripts.render_block import main as render_main

    sys.argv = ["render_block.py", args.file]
    if args.line:
        sys.argv.extend(["--line", str(args.line)])
    render_main()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-blackbox",
        description="Global CLI for deploying and using ai-collab-blackbox.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Install skill files into a target project.")
    init_parser.add_argument("--project-root", default=".", help="Target project root.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing target dir.")
    init_parser.set_defaults(handler=cmd_init)

    where_parser = subparsers.add_parser("where", help="Show target skill path for a project.")
    where_parser.add_argument("--project-root", default=".", help="Target project root.")
    where_parser.set_defaults(handler=cmd_where)

    info_parser = subparsers.add_parser("info", help="Show command and install mode info.")
    info_parser.set_defaults(handler=cmd_info)

    show_parser = subparsers.add_parser("show-skill", help="Print bundled SKILL.md content.")
    show_parser.add_argument("--lang", choices=("zh", "en"), default="zh", help="Skill language.")
    show_parser.set_defaults(handler=cmd_show_skill)

    write_parser = subparsers.add_parser("write", help="Write a worklog record.")
    write_parser.add_argument("--project-root", default=".", help="Project root directory.")
    write_parser.add_argument("--file", required=True, help="JSON file produced by AI.")
    write_parser.add_argument("--no-global", action="store_true", help="Do not write all_time.jsonl.")
    write_parser.set_defaults(handler=cmd_write)

    validate_parser = subparsers.add_parser("validate", help="Validate a JSON or JSONL record.")
    validate_group = validate_parser.add_mutually_exclusive_group(required=True)
    validate_group.add_argument("--json", help="Single JSON string.")
    validate_group.add_argument("file", nargs="?", help="JSONL or JSON file.")
    validate_parser.set_defaults(handler=cmd_validate)

    render_parser = subparsers.add_parser("render", help="Render block text from JSONL or JSON.")
    render_parser.add_argument("file", help="JSONL or JSON file.")
    render_parser.add_argument("--line", type=int, default=0, help="Render a specific JSONL line.")
    render_parser.set_defaults(handler=cmd_render)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.handler(args) or 0)
    except FileExistsError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("[FAIL] cancelled", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
