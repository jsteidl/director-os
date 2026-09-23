import re
from parser._files import get_log_file
from parser.tasks import get_tasks
from parser.dependencies import get_dependencies
from parser.risks import get_risks
from parser.someday import get_someday_items
from parser.accomplishments import get_accomplishments


def get_all_tags():
    tags = set()
    for obj in [*get_tasks(), *get_dependencies(), *get_risks(), *get_someday_items(), *get_accomplishments()]:
        tags.update(obj.tags)
    return sorted(tags, key=str.lower)


def get_tag_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for obj in [*get_tasks(), *get_dependencies(), *get_risks(), *get_someday_items(), *get_accomplishments()]:
        for tag in obj.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return counts


def _rewrite_tags_field(line: str, old_tag: str, new_tag: str | None) -> str:
    m = re.search(r"(\| Tags: )([^|\n]+)", line)
    if not m:
        return line
    tags = m.group(2).strip().split()
    if new_tag:
        tags = [new_tag if t == old_tag else t for t in tags]
    else:
        tags = [t for t in tags if t != old_tag]
    if not tags:
        return line.replace(m.group(0), "").rstrip()
    return line.replace(m.group(0), m.group(1) + " ".join(tags))


def rename_tag(old_tag: str, new_tag: str):
    path = get_log_file()
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    path.write_text("".join(_rewrite_tags_field(l, old_tag, new_tag) for l in lines), encoding="utf-8")


def delete_tag(tag: str):
    path = get_log_file()
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    path.write_text("".join(_rewrite_tags_field(l, tag, None) for l in lines), encoding="utf-8")
