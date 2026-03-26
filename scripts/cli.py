import argparse
import sys
import os
import shutil
import urllib.request

def init_project():
    print("Initializing ai-collab-blackbox in the current project...")
    cwd = os.getcwd()
    target_dir = os.path.join(cwd, ".agents", "skills", "ai-collab-blackbox")
    
    if os.path.exists(target_dir):
        print(f"[WARN] Target directory {target_dir} already exists. Skipping init.")
        return

    # To support both pip install -e . and normal git clones
    pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_skill_file = os.path.join(pkg_root, 'SKILL.md')
    is_development_install = os.path.exists(target_skill_file)

    os.makedirs(target_dir, exist_ok=True)

    if is_development_install:
        # Copy the entire skill to the local project
        to_copy = ['SKILL.md', 'SKILL_zh.md', 'README.md', 'README_zh.md', 'references', 'scripts']
        for item in to_copy:
            src = os.path.join(pkg_root, item)
            dst = os.path.join(target_dir, item)
            if os.path.exists(src):
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        print(f"[SUCCESS] Copied complete local scaffolding to {target_dir}")
    else:
        print("[INFO] Fetching latest skill rules from GitHub for local reference...")
        try:
            with urllib.request.urlopen("https://raw.githubusercontent.com/icestorm012002/ai-collab-blackbox/main/SKILL.md") as response:
                skill_content = response.read().decode('utf-8')
            with open(os.path.join(target_dir, 'SKILL.md'), 'w', encoding='utf-8') as f:
                f.write(skill_content)
            print(f"[SUCCESS] Scaffolding created in {target_dir}")
        except Exception as e:
            print(f"[FAIL] Unable to fetch from GitHub: {e}")
            print(f"[INFO] Please manually copy SKILL.md to {target_dir} to complete initialization.")

    print("\nAI can now locally read the SKILL in this project and directly run `ai-blackbox write` globally!")

def write_cmd(args):
    from scripts.write_worklog import main as write_main
    # Override sys.argv to emulate standard script execution
    sys.argv = ["write_worklog.py", "--project-root", args.project_root, "--file", args.file]
    if args.no_global:
        sys.argv.append("--no-global")
    write_main()

def validate_cmd(args):
    from scripts.validate_worklog import main as validate_main
    sys.argv = ["validate_worklog.py", args.file]
    validate_main()

def render_cmd(args):
    from scripts.render_block import main as render_main
    sys.argv = ["render_block.py", args.file]
    render_main()

def main():
    parser = argparse.ArgumentParser(
        prog="ai-blackbox",
        description="A1 Coder: ai-collab-blackbox global CLI."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # init
    parser_init = subparsers.add_parser("init", help="Initialize the local .agents/skills/ai-collab-blackbox environment in current project.")
    
    # write
    parser_write = subparsers.add_parser("write", help="Write a work log from a temporary JSON file to the project logs.")
    parser_write.add_argument("--project-root", default=".", help="Project root directory (default: current directory)")
    parser_write.add_argument("--file", required=True, help="Temporary JSON file produced by AI")
    parser_write.add_argument("--no-global", action="store_true", help="Do not write to all_time.jsonl")
    
    # validate
    parser_validate = subparsers.add_parser("validate", help="Validate a JSON record format.")
    parser_validate.add_argument("file", help="JSONL or JSON file to validate")
    
    # render
    parser_render = subparsers.add_parser("render", help="Render a JSONL or JSON file into block log format.")
    parser_render.add_argument("file", help="JSONL or JSON file to render")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_project()
    elif args.command == "write":
        write_cmd(args)
    elif args.command == "validate":
        validate_cmd(args)
    elif args.command == "render":
        render_cmd(args)

if __name__ == "__main__":
    main()
