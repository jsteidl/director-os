from textual.widgets import Input


class TabCompleteMixin:
    """Apply the current suggestion on Tab instead of moving focus."""

    def on_key(self, event) -> None:
        if event.key == "tab":
            focused = self.focused
            if isinstance(focused, Input) and focused._suggestion:
                focused.value = focused._suggestion
                focused.cursor_position = len(focused.value)
                event.prevent_default()
