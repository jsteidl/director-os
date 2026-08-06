from textual.screen import ModalScreen
from textual.widgets import DataTable, Label
from textual.containers import Vertical


class HelpScreen(ModalScreen):

    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
        ("?", "app.pop_screen", "Close"),
    ]

    def compose(self):

        yield Vertical(

            Label("Keyboard Shortcuts"),

            DataTable(
                id="shortcuts",
                show_cursor=False,
            ),

        )

    def on_mount(self):

        table = self.query_one("#shortcuts", DataTable)

        table.add_columns("Key", "Action")

        seen = set()

        for screen in self.app.screen_stack:
            for binding in screen.BINDINGS:
                key = binding[0] if isinstance(binding, tuple) else binding.key
                description = binding[2] if isinstance(binding, tuple) else binding.description
                if key not in seen:
                    seen.add(key)
                    table.add_row(key, description)

        for binding in self.app.BINDINGS:
            key = binding[0] if isinstance(binding, tuple) else binding.key
            description = binding[2] if isinstance(binding, tuple) else binding.description
            if key not in seen:
                seen.add(key)
                table.add_row(key, description)
