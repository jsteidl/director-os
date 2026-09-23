from parser._files import get_scratch_file


def get_scratch() -> str:
    path = get_scratch_file()
    return path.read_text(encoding="utf-8") if path.exists() else ""


def save_scratch(text: str):
    get_scratch_file().write_text(text, encoding="utf-8")
