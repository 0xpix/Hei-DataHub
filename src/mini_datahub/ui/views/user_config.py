"""
User configuration screen for theme, keybindings, and other settings.
"""
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Select,
)

from mini_datahub.services.config import get_config
from mini_datahub.ui.theme import THEMES


class UserConfigScreen(Screen):
    """User configuration screen for theme and other settings."""

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("q", "cancel", "Back"),
        Binding("ctrl+s", "save", "Save & Apply", show=True),
    ]

    def compose(self) -> ComposeResult:
        # Get available themes
        theme_options = [(name, name) for name in sorted(THEMES.keys())]

        yield Header()
        yield VerticalScroll(
            Label("⚙️ User Settings  |  [italic]Configure theme and preferences[/italic]", classes="title"),
            Container(
                Label("Theme:"),
                Select(theme_options, id="select-theme", allow_blank=False),
                Label("", id="theme-preview"),
                Label(""),
                Label("Keybindings:"),
                Label("[dim]Edit keybindings in config file, then click reload[/dim]"),
                Horizontal(
                    Button("🔄 Reload Keybindings", id="reload-keybindings-btn", variant="default"),
                    Button("📝 Open Config File", id="open-config-btn", variant="default"),
                ),
                Label(""),
                Horizontal(
                    Button("Apply & Save", id="save-btn", variant="primary"),
                    Button("Cancel", id="cancel-btn", variant="default"),
                ),
                Label("", id="status-message"),
                Label(
                    "\n[dim]Config location: ~/.config/hei-datahub/config.yaml[/dim]"
                ),
                id="user-config-container",
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load current settings."""
        config = get_config()
        current_theme = config.get_theme_name()

        # Set current theme in select
        theme_select = self.query_one("#select-theme", Select)
        theme_select.value = current_theme

        # Update preview
        self._update_theme_preview(current_theme)

    def _update_theme_preview(self, theme_name: str) -> None:
        """Update theme preview text."""
        preview_label = self.query_one("#theme-preview", Label)
        theme_colors = THEMES.get(theme_name, {})

        preview_text = f"\n[dim]Preview: Primary: {theme_colors.get('primary', 'N/A')}, "
        preview_text += f"Accent: {theme_colors.get('accent', 'N/A')}[/dim]"
        preview_label.update(preview_text)

    @on(Select.Changed, "#select-theme")
    def on_theme_changed(self, event: Select.Changed) -> None:
        """Handle theme selection change."""
        if event.value:
            self._update_theme_preview(str(event.value))

    @on(Button.Pressed, "#reload-keybindings-btn")
    def on_reload_keybindings_button(self) -> None:
        """Reload keybindings from config file."""
        try:
            self.app.reload_keybindings()
            status_label = self.query_one("#status-message", Label)
            status_label.update("[green]✓ Keybindings reloaded![/green]")
        except Exception as e:
            self.app.notify(f"Failed to reload keybindings: {str(e)}", severity="error", timeout=5)

    @on(Button.Pressed, "#open-config-btn")
    def on_open_config_button(self) -> None:
        """Open config file in default editor."""
        from mini_datahub.infra.config_paths import get_user_config_file
        import subprocess
        import os

        config_file = get_user_config_file()

        try:
            # Try to open with default editor based on environment
            editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))

            # Notify user
            self.app.notify(
                f"Opening config file in {editor}... (edit and save, then click 'Reload Keybindings')",
                timeout=8
            )

            # We can't directly open in the terminal from TUI without blocking,
            # so we'll just show the path
            self.app.notify(
                f"Config file location: {config_file}",
                timeout=10
            )

            status_label = self.query_one("#status-message", Label)
            status_label.update(f"[cyan]Config: {config_file}[/cyan]")

        except Exception as e:
            self.app.notify(f"Error: {str(e)}", severity="error", timeout=5)

    @on(Button.Pressed, "#save-btn")
    def on_save_button(self) -> None:
        """Save settings and apply immediately."""
        self.action_save()

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel_button(self) -> None:
        """Cancel and go back."""
        self.action_cancel()

    def action_save(self) -> None:
        """Save settings and apply them immediately without restart."""
        status_label = self.query_one("#status-message", Label)

        try:
            config = get_config()

            # Get new theme
            theme_select = self.query_one("#select-theme", Select)
            new_theme = str(theme_select.value)

            # Update config
            config.update_user_config({"theme.name": new_theme})

            # Apply theme immediately
            self.app.apply_theme(new_theme)

            status_label.update("[green]✓ Settings saved and applied![/green]")
            self.app.notify("Theme applied successfully! No restart needed.", timeout=3)

            # Close screen after a moment
            self.set_timer(1.5, self.action_cancel)

        except Exception as e:
            status_label.update(f"[red]Error saving: {str(e)}[/red]")
            self.app.notify(f"Save failed: {str(e)}", severity="error", timeout=5)

    def action_cancel(self) -> None:
        """Cancel and go back."""
        self.app.pop_screen()
