import re
import tomllib
from pathlib import Path


def _load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}


def _get_logs_path() -> Path:
    config = _load_config()
    logs_path = config.get("logs_path", "logs")
    p = Path(logs_path)
    return p if p.is_absolute() else Path(__file__).parent.parent / p


def get_terminal_size() -> tuple[int, int] | None:
    config = _load_config()
    size = config.get("terminal_size")
    if isinstance(size, list) and len(size) == 2:
        return (int(size[0]), int(size[1]))
    return None


def extract_tags(text):
    m = re.search(r"\| Tags: ([^|\n]+)", text)
    if m:
        return m.group(1).strip().split()
    return re.findall(r"#+(\w+)", text)


def strip_tags(text):
    if "| Tags:" in text:
        return re.sub(r"\s*\| Tags: [^|\n]+", "", text).strip()
    return re.sub(r"\s*#+\S+", "", text).strip()


def _clean(text: str) -> str:
    return text.replace("|", "").strip()


def load_log() -> str:
    from parser._files import get_log_file
    from parser._scaffold import rollover_log
    path = get_log_file()
    if not path.exists():
        rollover_log()
    return path.read_text(encoding="utf-8")


def save_log(content: str):
    from parser._files import get_log_file
    get_log_file().write_text(content, encoding="utf-8")
