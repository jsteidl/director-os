#!/usr/bin/env python3
"""
backfill_tags.py — bulk tag/project assignment across all log files

Usage examples:

  # Assign project to all matching lines
  python backfill_tags.py --match "store insights" --project store_insights

  # Add tags to matching lines
  python backfill_tags.py --match "snowflake" --add-tags vendor

  # Remove a tag from matching lines
  python backfill_tags.py --match "mce" --remove-tags active

  # Scoped rename: rename tag only on lines matching pattern
  python backfill_tags.py --match "mce" --replace-tag active deployment

  # Combine operations
  python backfill_tags.py --match "looker" --project bi_discovery --add-tags vendor --remove-tags active

  # Preview without writing
  python backfill_tags.py --match "store insights" --project store_insights --dry-run

  # Case-sensitive match
  python backfill_tags.py --match "MCE" --project mce --case-sensitive

  # Limit to a specific object type
  python backfill_tags.py --match "snowflake" --add-tags vendor --only tasks
  python backfill_tags.py --match "snowflake" --add-tags vendor --only accomplishments
  python backfill_tags.py --match "snowflake" --add-tags vendor --only deps
  python backfill_tags.py --match "snowflake" --add-tags vendor --only risks
  python backfill_tags.py --match "snowflake" --add-tags vendor --only someday
"""

import re
import sys
import argparse
from pathlib import Path


def _get_logs_path() -> Path:
    import tomllib
    config_path = Path(__file__).parent / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        p = Path(config.get("logs_path", "logs"))
    else:
        p = Path("logs")
    return p if p.is_absolute() else Path(__file__).parent / p


def _get_tags(line: str) -> list[str]:
    m = re.search(r"\| Tags: ([^|\n]+)", line)
    return m.group(1).strip().split() if m else []


def _set_tags(line: str, tags: list[str]) -> str:
    if not tags:
        return re.sub(r"\s*\| Tags: [^|\n]+", "", line).rstrip()
    tag_str = " ".join(tags)
    if "| Tags:" in line:
        return re.sub(r"\| Tags: [^|\n]+", f"| Tags: {tag_str}", line).rstrip()
    return line.rstrip() + f" | Tags: {tag_str}"


def _get_project(line: str) -> str | None:
    m = re.search(r"\| Project: ([^|\n]+)", line)
    return m.group(1).strip() if m else None


def _set_project(line: str, project: str) -> str:
    if "| Project:" in line:
        return re.sub(r"\| Project: [^|\n]+", f"| Project: {project}", line).rstrip()
    # Insert before Tags if present, otherwise append
    if "| Tags:" in line:
        return re.sub(r"\| Tags:", f"| Project: {project} | Tags:", line).rstrip()
    return line.rstrip() + f" | Project: {project}"


# Line matchers for each object type
LINE_PATTERNS = {
    "tasks":          re.compile(r"^- \[ \] "),
    "accomplishments": re.compile(r"^- Task: "),
    "deps":           re.compile(r"^- .+ \| Owner: .+ \| Since:"),
    "risks":          re.compile(r"^- .+ \| (Severity|Owner): "),
    "someday":        re.compile(r"^- .+ \| Owner: .+ \| Since:"),
}

# deps and someday share the same pattern — disambiguate by section
SECTION_MAP = {
    "tasks":          "### High-Priority",
    "deps":           "### Waiting On",
    "risks":          "### Risks",
    "someday":        "### Someday/Future",
    "accomplishments": "### Accomplishments",
}


def _current_section(line_idx: int, lines: list[str]) -> str:
    for i in range(line_idx, -1, -1):
        stripped = lines[i].strip()
        if stripped.startswith("### "):
            return stripped
    return ""


def process_file(path: Path, args, dry_run: bool) -> int:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    changes = 0

    flags = 0 if args.case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(args.match), flags)

    only = args.only  # None or one of tasks/accomplishments/deps/risks/someday

    new_lines = []
    for i, line in enumerate(lines):
        stripped = line.rstrip("\r\n")

        # Determine object type from section context
        section = _current_section(i, [l.rstrip("\r\n") for l in lines])
        obj_type = None
        for t, sec_header in SECTION_MAP.items():
            if section == sec_header:
                obj_type = t
                break

        # Skip if filtering by type
        if only and obj_type != only:
            new_lines.append(line)
            continue

        # Must be a data line for the detected type
        if obj_type and LINE_PATTERNS.get(obj_type, re.compile(r"(?!x)x")).match(stripped):
            if pattern.search(stripped):
                original = stripped
                modified = stripped

                # Assign project
                if args.project and not _get_project(modified):
                    modified = _set_project(modified, args.project)

                # Add tags
                if args.add_tags:
                    tags = _get_tags(modified)
                    for t in args.add_tags:
                        if t not in tags:
                            tags.append(t)
                    modified = _set_tags(modified, tags)

                # Remove tags
                if args.remove_tags:
                    tags = _get_tags(modified)
                    tags = [t for t in tags if t not in args.remove_tags]
                    modified = _set_tags(modified, tags)

                # Scoped replace tag
                if args.replace_tag:
                    old_tag, new_tag = args.replace_tag
                    tags = _get_tags(modified)
                    if old_tag in tags:
                        tags = [new_tag if t == old_tag else t for t in tags]
                        modified = _set_tags(modified, tags)

                if modified != original:
                    changes += 1
                    ending = line[len(stripped):]
                    line = modified + ending
                    if dry_run:
                        print(f"  [{path.name}]")
                        print(f"  - {original}")
                        print(f"  + {modified}")
                        print()

        new_lines.append(line)

    if not dry_run and changes:
        path.write_text("".join(new_lines), encoding="utf-8")

    return changes


def main():
    parser = argparse.ArgumentParser(description="Bulk tag/project backfill across all log files")
    parser.add_argument("--match", required=True, help="Pattern to match lines (case-insensitive by default)")
    parser.add_argument("--project", help="Assign this project to matching lines (only if no project set)")
    parser.add_argument("--add-tags", nargs="+", metavar="TAG", help="Add these tags to matching lines")
    parser.add_argument("--remove-tags", nargs="+", metavar="TAG", help="Remove these tags from matching lines")
    parser.add_argument("--replace-tag", nargs=2, metavar=("OLD", "NEW"), help="Replace a tag on matching lines only")
    parser.add_argument("--only", choices=["tasks", "accomplishments", "deps", "risks", "someday"],
                        help="Limit to a specific object type")
    parser.add_argument("--case-sensitive", action="store_true", help="Case-sensitive match")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    if not any([args.project, args.add_tags, args.remove_tags, args.replace_tag]):
        print("Error: at least one of --project, --add-tags, --remove-tags, --replace-tag is required")
        sys.exit(1)

    logs_path = _get_logs_path()
    log_files = sorted(logs_path.glob("*-Director-Log.md"))

    if not log_files:
        print(f"No log files found in {logs_path}")
        sys.exit(1)

    if args.dry_run:
        print(f"DRY RUN — match: '{args.match}' across {len(log_files)} file(s)\n")

    total = 0
    for path in log_files:
        count = process_file(path, args, args.dry_run)
        if count and not args.dry_run:
            print(f"  {path.name}: {count} line(s) updated")
        total += count

    if args.dry_run:
        print(f"{'No changes' if not total else f'{total} line(s) would be updated'}")
    else:
        print(f"\nDone. {total} line(s) updated across {len(log_files)} file(s).")


if __name__ == "__main__":
    main()
