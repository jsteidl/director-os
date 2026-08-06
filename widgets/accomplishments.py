from textual.widgets import Static

from parser import get_accomplishments


class AccomplishmentsWidget(Static):

    def refresh_data(self):

        accomplishments = get_accomplishments()

        output = "\n".join(
            f"✓ {item.task}"
            for item in accomplishments[-10:]
        )

        self.update(output)

    def on_mount(self):
        self.refresh_data()