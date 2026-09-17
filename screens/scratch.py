import re
from textual.screen import ModalScreen
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Label, TextArea, Markdown
from textual.app import ComposeResult
from textual.binding import Binding

from parser import get_scratch, save_scratch

_CHECKBOX = re.compile(r'^(\s*)-\s\[([ x])\]\s(.+)$', re.MULTILINE)


class ScratchPadScreen(ModalScreen):

    BINDINGS = [
        Binding("e", "edit", "Edit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("j", "cursor_down", "Next", show=False),
        Binding("k", "cursor_up", "Prev", show=False),
        Binding("space", "toggle_check", "Toggle", show=False),
        Binding("p", "promote", "Promote", show=False),
        Binding("escape", "cancel", "Close"),
    ]

    CSS = """
    ScratchPadScreen {
        align: center middle;
    }
    #scratch-outer {
        width: 80%;
        height: 80%;
        border: solid $accent;
        background: $surface;
    }
    #scratch-title {
        height: 1;
        padding: 0 1;
        background: $accent-darken-2;
        color: $background;
        text-style: bold;
    }
    TextArea {
        height: 1fr;
    }
    #scratch-view {
        height: 1fr;
        padding: 0 1;
    }
    #scratch-hint {
        height: 1;
        padding: 0 1;
        color: $text-muted;
    }
    """

    def __init__(self):
        super().__init__()
        self._editing = False
        self._cursor = 0

    @staticmethod
    def _to_md(text: str, cursor: int = -1) -> str:
        lines = text.splitlines()
        cb_idx = 0
        out = []
        for line in lines:
            m = _CHECKBOX.match(line)
            if m:
                indent, state, item = m.group(1), m.group(2), m.group(3)
                marker = "[x]" if state == "x" else "[ ]"
                prefix = "**›** " if cb_idx == cursor else ""
                out.append(f"{indent}- {marker} {prefix}{item}")
                cb_idx += 1
            else:
                out.append(re.sub(r'^(\s*)[-*] ', r'\1• ', line))
        text = "\n".join(out)
        return re.sub(r'(?<!\n)\n(?!\n)', '  \n', text)

    def _checkbox_count(self) -> int:
        return len(_CHECKBOX.findall(self.query_one("#scratch-area", TextArea).text))

    def compose(self) -> ComposeResult:
        content = get_scratch()
        yield Vertical(
            Label("", id="scratch-title"),
            ScrollableContainer(Markdown("", id="scratch-md"), id="scratch-view"),
            TextArea(content, id="scratch-area"),
            Label("[dim]scratch.md · j/k select · space toggle · p promote · e edit[/dim]", id="scratch-hint"),
            id="scratch-outer",
        )

    def on_mount(self):
        self._set_mode(editing=False)

    def _set_mode(self, editing: bool):
        self._editing = editing
        view = self.query_one("#scratch-view", ScrollableContainer)
        area = self.query_one("#scratch-area", TextArea)
        title = self.query_one("#scratch-title", Label)
        if editing:
            view.display = False
            area.display = True
            area.focus()
            title.update("Scratch Pad  [dim]ctrl+s to save · esc to close[/dim]")
        else:
            area.display = False
            view.display = True
            self.set_focus(None)
            self._render_md()
            title.update("Scratch Pad  [dim]e to edit · esc to close[/dim]")

    def _render_md(self):
        text = self.query_one("#scratch-area", TextArea).text
        self.query_one("#scratch-md", Markdown).update(self._to_md(text, self._cursor))

    def action_edit(self):
        if not self._editing:
            self._set_mode(editing=True)

    def action_save(self):
        if self._editing:
            text = self.query_one("#scratch-area", TextArea).text
            save_scratch(text)
            self._set_mode(editing=False)

    def action_cursor_down(self):
        if not self._editing:
            self._cursor = min(self._cursor + 1, max(self._checkbox_count() - 1, 0))
            self._render_md()

    def action_cursor_up(self):
        if not self._editing:
            self._cursor = max(self._cursor - 1, 0)
            self._render_md()

    def action_toggle_check(self):
        if self._editing:
            return
        area = self.query_one("#scratch-area", TextArea)
        text = area.text
        matches = list(_CHECKBOX.finditer(text))
        if not matches or self._cursor >= len(matches):
            return
        m = matches[self._cursor]
        new = m.group(0).replace("[ ]", "[x]", 1) if m.group(2) == " " else m.group(0).replace("[x]", "[ ]", 1)
        area.load_text(text[:m.start()] + new + text[m.end():])
        save_scratch(area.text)
        self._render_md()

    def action_promote(self):
        if self._editing:
            return
        area = self.query_one("#scratch-area", TextArea)
        text = area.text
        matches = list(_CHECKBOX.finditer(text))
        if not matches or self._cursor >= len(matches):
            return
        m = matches[self._cursor]
        item_text = m.group(3)
        from screens.add_task import AddTaskScreen
        def on_add(result):
            if result:
                task, priority, due_date, tags = result
                from parser import add_task
                add_task(task, tags, due_date, priority)
                new_text = text[:m.start()] + text[m.end():].lstrip('\n')
                area.load_text(new_text)
                save_scratch(area.text)
                self._cursor = min(self._cursor, max(self._checkbox_count() - 1, 0))
                self._render_md()
                self.app.notify(f"Task added: {task}")
        self.app.push_screen(AddTaskScreen(title=item_text), on_add)

    def action_cancel(self):
        self.dismiss(False)
