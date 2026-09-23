import re
from parser._core import load_log, save_log, extract_tags
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


def rename_tag(old_tag, new_tag):
    path = get_log_file()
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"#" + re.escape(old_tag) + r"\b", f"#{new_tag}", content)
    path.write_text(content, encoding="utf-8")


def delete_tag(tag: str):
    path = get_log_file()
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"\s*#" + re.escape(tag) + r"\b", "", content)
    path.write_text(content, encoding="utf-8")
