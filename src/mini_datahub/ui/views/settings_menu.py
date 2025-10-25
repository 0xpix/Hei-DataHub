"""
Settings menu to choose between different settings screens.
"""
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label


class SettingsMenuScreen(Screen):
    """Settings menu offering different configuration options."""

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("q", "cancel", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Label("⚙️ Settings  |  [italic]Configuration[/italic]", classes="title"),
            Container(
                Button("☁️ WebDAV (HeiBox)", id="btn-webdav-settings", variant="primary"),
                Label("[dim]Configure HeiBox/WebDAV credentials for cloud storage[/dim]"),
                Label(""),
                Button("← Back", id="btn-cancel", variant="default"),
                id="settings-menu-container",
            ),
        )
        yield Footer()

    @on(Button.Pressed, "#btn-webdav-settings")
    def on_webdav_settings_button(self) -> None:
        """Open WebDAV settings screen."""
        from mini_datahub.ui.views.settings import SettingsScreen
        self.app.push_screen(SettingsScreen())

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel_button(self) -> None:
        """Go back."""
        self.action_cancel()

    def action_cancel(self) -> None:
        """Cancel and go back."""
        self.app.pop_screen()
