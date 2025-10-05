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
            Label("⚙️ Settings Menu  |  [italic]Choose a configuration option[/italic]", classes="title"),
            Container(
                Button("🎨 Theme & Preferences", id="btn-user-config", variant="primary"),
                Label("[dim]Configure theme, appearance, and general settings[/dim]"),
                Label(""),
                Button("🔗 GitHub Integration", id="btn-github-settings", variant="default"),
                Label("[dim]Configure GitHub credentials and PR automation[/dim]"),
                Label(""),
                Button("← Back", id="btn-cancel", variant="default"),
                id="settings-menu-container",
            ),
        )
        yield Footer()

    @on(Button.Pressed, "#btn-user-config")
    def on_user_config_button(self) -> None:
        """Open user config screen."""
        from mini_datahub.ui.views.user_config import UserConfigScreen
        self.app.push_screen(UserConfigScreen())

    @on(Button.Pressed, "#btn-github-settings")
    def on_github_settings_button(self) -> None:
        """Open GitHub settings screen."""
        from mini_datahub.ui.views.settings import SettingsScreen
        self.app.push_screen(SettingsScreen())

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel_button(self) -> None:
        """Go back."""
        self.action_cancel()

    def action_cancel(self) -> None:
        """Cancel and go back."""
        self.app.pop_screen()
