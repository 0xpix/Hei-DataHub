from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option

class ThemePalette(ModalScreen[None]):
    """A palette for selecting and applying themes."""

    CSS = """
    ThemePalette {
        align: center middle;
        background: rgba(0, 0, 0, 0.6);
    }

    #theme-palette-container {
        width: 60;
        height: 20;
        background: #1e1e2e;
        border: wide #89b4fa;
        padding: 1;
    }

    #theme-input {
        border: none;
        background: #313244;
        color: #cdd6f4;
        width: 100%;
        margin-bottom: 1;
        dock: top;
    }

    #theme-list {
        height: 1fr;
        border: none;
        background: #1e1e2e;
        color: #cdd6f4;
        scrollbar-gutter: stable;
    }

    #theme-list > .option-list--option {
        color: #cdd6f4;
    }

    #theme-list > .option-list--option-highlighted {
        background: #45475a;
        color: #f5e0dc;
    }

    OptionList:focus {
        border: none;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("down", "cursor_down", "Next", show=False),
        Binding("up", "cursor_up", "Previous", show=False),
        Binding("enter", "select_theme", "Select", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="theme-palette-container"):
            yield Input(placeholder="> Select theme...", id="theme-input")
            yield OptionList(id="theme-list")

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self._load_themes()

    def action_cursor_down(self) -> None:
        self.query_one(OptionList).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(OptionList).action_cursor_up()

    def _load_themes(self) -> None:
        """Load available themes."""
        self.themes = []

        # Get actual available themes from the App registry
        if hasattr(self.app, "available_themes"):
            # available_themes is dict[str, Theme] or similar
            available = self.app.available_themes
            # We only show themes that are actually registered to avoid crashes
            self.themes = sorted(list(available.keys()) if isinstance(available, dict) else list(available))
        else:
            # Fallback for older Textual versions or if property missing
            self.themes = ["textual-dark", "textual-light"]

        # Filter out problematic or ugly themes
        filtered_out = ("textual-ansi", "ansi", "css", "basic")
        self.themes = [t for t in self.themes if t not in filtered_out]

        self._update_list(self.themes)

    def _update_list(self, themes) -> None:
        option_list = self.query_one(OptionList)
        option_list.clear_options()

        if not themes:
            option_list.add_option(Option(prompt="No themes found", disabled=True))
            return

        # Get current theme to mark it
        current_theme = self.app.theme if hasattr(self.app, "theme") else None

        for theme in themes:
            if theme == current_theme:
                option_list.add_option(Option(prompt=f"● {theme}", id=theme))
            else:
                option_list.add_option(Option(prompt=f"  {theme}", id=theme))

        option_list.highlighted = 0

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        if not query:
            self._update_list(self.themes)
            return

        filtered = [t for t in self.themes if query in t.lower()]
        self._update_list(filtered)

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key when Input is focused."""
        self.action_select_theme()

    @on(OptionList.OptionHighlighted)
    def on_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        theme = event.option_id
        if theme:
            # Live preview - apply theme immediately without closing
            # Wrap in try/except to prevent crashes if theme is somehow invalid
            try:
                if hasattr(self.app, "apply_theme"):
                    # We can't easily use apply_theme for preview as it might be heavy or persistent
                    # Just setting app.theme is standard for Textual
                    self.app.theme = theme
                else:
                    self.app.theme = theme
            except Exception:
                # If preview fails, just ignore it. Don't crash the UI.
                pass

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        theme = event.option_id
        if theme:
            self._save_and_apply_theme(theme)

    def action_close(self) -> None:
        self.dismiss()

    def action_select_theme(self) -> None:
        """Select the currently highlighted theme."""
        option_list = self.query_one(OptionList)
        idx = option_list.highlighted
        if idx is not None:
            try:
                option = option_list.get_option_at_index(idx)
                if option and option.id and not option.disabled:
                    self._save_and_apply_theme(option.id)
            except Exception:
                pass

    def _save_and_apply_theme(self, theme: str) -> None:
        """Save theme to config and apply it."""
        # 1. Save explicitly to config FIRST (before dismiss)
        try:
            from hei_datahub.services.config import get_config
            config_manager = get_config()

            # Force update the theme name in the user config object
            config_manager._user_config.theme.name = theme

            # Save it to disk immediately
            config_manager._save_user_config(config_manager._user_config)

            self.app.notify(f"Theme '{theme}' saved", timeout=2)
        except Exception as e:
            self.app.notify(f"Failed to save theme: {e}", severity="error")

        # 2. Dismiss the modal
        self.dismiss()

        # 3. Apply theme (after dismiss so it's visible on the main screen)
        self.app.theme = theme
