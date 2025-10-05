"""
Theme management for Textual TUI.

Supports multiple built-in themes and custom overrides.
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


# Built-in theme definitions
THEMES: Dict[str, Dict[str, str]] = {
    "gruvbox": {
        "primary": "#fb4934",
        "secondary": "#b8bb26",
        "accent": "#fabd2f",
        "background": "#282828",
        "surface": "#3c3836",
        "error": "#fb4934",
        "success": "#b8bb26",
        "warning": "#fabd2f",
        "panel": "#1d2021",
    },
    "dark": {
        "primary": "#61afef",
        "secondary": "#98c379",
        "accent": "#c678dd",
        "background": "#282c34",
        "surface": "#3e4451",
        "error": "#e06c75",
        "success": "#98c379",
        "warning": "#e5c07b",
        "panel": "#21252b",
    },
    "light": {
        "primary": "#0184bc",
        "secondary": "#50a14f",
        "accent": "#a626a4",
        "background": "#fafafa",
        "surface": "#f0f0f0",
        "error": "#e45649",
        "success": "#50a14f",
        "warning": "#c18401",
        "panel": "#ffffff",
    },
    "solarized": {
        "primary": "#268bd2",
        "secondary": "#859900",
        "accent": "#d33682",
        "background": "#002b36",
        "surface": "#073642",
        "error": "#dc322f",
        "success": "#859900",
        "warning": "#b58900",
        "panel": "#001e26",
    },
    "monokai": {
        "primary": "#66d9ef",
        "secondary": "#a6e22e",
        "accent": "#f92672",
        "background": "#272822",
        "surface": "#3e3d32",
        "error": "#f92672",
        "success": "#a6e22e",
        "warning": "#e6db74",
        "panel": "#1e1f1c",
    },
}


class ThemeManager:
    """
    Manage theme selection and application.
    """

    def __init__(self, theme_name: str = "gruvbox", overrides: Optional[Dict[str, str]] = None):
        """
        Initialize theme manager.

        Args:
            theme_name: Name of the theme to use
            overrides: Optional color overrides
        """
        self.theme_name = theme_name
        self.overrides = overrides or {}
        self._current_theme = self._load_theme(theme_name)

    def _load_theme(self, name: str) -> Dict[str, str]:
        """
        Load a theme by name.

        Args:
            name: Theme name

        Returns:
            Theme color dictionary
        """
        if name not in THEMES:
            logger.warning(f"Unknown theme '{name}', falling back to 'gruvbox'")
            name = "gruvbox"

        theme = THEMES[name].copy()

        # Apply overrides
        theme.update(self.overrides)

        return theme

    def get_color(self, key: str, default: str = "#ffffff") -> str:
        """
        Get a color from the current theme.

        Args:
            key: Color key (e.g., "primary", "background")
            default: Default color if key not found

        Returns:
            Color hex string
        """
        return self._current_theme.get(key, default)

    def switch_theme(self, theme_name: str, overrides: Optional[Dict[str, str]] = None) -> None:
        """
        Switch to a different theme.

        Args:
            theme_name: Name of the new theme
            overrides: Optional color overrides
        """
        self.theme_name = theme_name
        if overrides:
            self.overrides = overrides
        self._current_theme = self._load_theme(theme_name)
        logger.info(f"Switched to theme: {theme_name}")

    def get_textual_theme_name(self) -> str:
        """
        Get the Textual CSS theme name.

        Returns:
            Textual theme name ("dark", "light", or custom)
        """
        # Map our themes to Textual's built-in themes
        if self.theme_name == "light":
            return "textual-light"
        else:
            return "textual-dark"

    def get_css_variables(self) -> str:
        """
        Generate CSS variables for the theme.

        Returns:
            CSS string with custom properties
        """
        css_lines = []
        for key, value in self._current_theme.items():
            css_var = key.replace("_", "-")
            css_lines.append(f"--{css_var}: {value};")

        return "\n".join(css_lines)

    @staticmethod
    def get_available_themes() -> list[str]:
        """Get list of available theme names."""
        return list(THEMES.keys())


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        # Initialize with default theme
        from mini_datahub.services.config import get_config
        config = get_config()
        _theme_manager = ThemeManager(
            theme_name=config.get_theme_name(),
            overrides=config.get_theme_overrides()
        )
    return _theme_manager


def reload_theme() -> None:
    """Reload theme from config."""
    global _theme_manager
    from mini_datahub.services.config import get_config
    config = get_config()
    _theme_manager = ThemeManager(
        theme_name=config.get_theme_name(),
        overrides=config.get_theme_overrides()
    )
