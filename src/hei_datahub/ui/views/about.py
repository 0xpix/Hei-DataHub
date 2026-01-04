"""
About screen showing project information, logo, and story.

Redesigned with a minimalistic, retro-inspired aesthetic for terminal elegance.
"""
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from hei_datahub.services.config import get_config
from hei_datahub.ui.assets.loader import get_logo_widget_text


class AboutScreen(Screen):
    """About screen with project information and logo."""

    BINDINGS = [
        Binding("escape", "back", "Back", key_display="esc"),
        Binding("j", "scroll_down", "Scroll Down", show=False),
        Binding("k", "scroll_up", "Scroll Up", show=False),
        Binding("d", "page_down", "Page Down", show=False),
        Binding("u", "page_up", "Page Up", show=False),
        Binding("g", "handle_g", "Top", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
    ]

    CSS_PATH = "../styles/about.tcss"

    def __init__(self, *args, **kwargs):
        """Initialize the screen."""
        super().__init__(*args, **kwargs)
        self._g_pressed = False

    def compose(self) -> ComposeResult:
        """Compose the about screen layout."""
        from hei_datahub.version import __version__

        # Load logo from config
        get_logo_widget_text(get_config())

        yield Header()

        with ScrollableContainer(id="about-container"):
            # Main card container
            with Container(id="about-card"):
                # Logo and version header
                # yield Static(logo_text, id="logo")
                yield Static(f"Hei-datahub - v{__version__}", id="version-badge")

                # Separator
                yield Static("─" * 70, id="header-separator", classes="separator")

                # Tagline
                yield Static(
                    "A cloud-first TUI for data cataloging and research collaboration.",
                    id="tagline"
                )

                # Separator
                yield Static("─" * 70, id="features-separator", classes="separator")

                # Compact content sections
                with Vertical(id="content-section"):

                    yield Static("[b #d4a574]Story[/b #d4a574]", classes="section-title")
                    yield Static(
                        "It began as a simple [b]Excel sheet inventory[/b]. "
                        "It was just boring, I wanted something fast, private, and fun to use—inside the terminal.\n"
                        "So Hei-DataHub was born: a TUI that keeps data in your hands, syncs to Heibox for the team, and makes finding things instant. The goal is simple: less friction, more science.",
                        classes="section-content"
                    )

                    yield Static("[b #d4a574]What is Hei-DataHub?[/b #d4a574]", classes="section-title")
                    yield Static(
                        "A terminal user interface designed for researchers and data scientists to "
                        "catalog, organize, and manage datasets efficiently. Combines YAML metadata, "
                        "SQLite full-text search, and seamless cloud integration.\n",
                        classes="section-content"
                    )

                    yield Static("[b #d4a574]Github $ Docs[/b #d4a574]", classes="section-title")
                    yield Static(
                        "GitHub: [link]https://github.com/0xpix/Hei-DataHub[/link]\n"
                        "Docs: [link]https://0xpix.github.io/Hei-DataHub/[/link]\n",
                        classes="section-content"
                    )

                # Footer hint
                yield Static("Made with 󰋑 by PIX", id="footer-hint")

        yield Footer()

    def action_back(self) -> None:
        """Return to previous screen."""
        self.app.pop_screen()

    def action_handle_g(self) -> None:
        """Handle 'g' key for gg sequence (Vim-style)."""
        if self._g_pressed:
            # Second g pressed - scroll to top
            container = self.query_one("#about-container", ScrollableContainer)
            container.scroll_home(animate=True)
            self._g_pressed = False
        else:
            # First g pressed - wait for second g
            self._g_pressed = True
            # Reset after 1 second if second g is not pressed
            self.set_timer(1.0, lambda: setattr(self, '_g_pressed', False))

    def action_scroll_down(self) -> None:
        """Scroll down one line (Vim j)."""
        self._g_pressed = False  # Reset g sequence
        container = self.query_one("#about-container", ScrollableContainer)
        container.scroll_down(animate=False)

    def action_scroll_up(self) -> None:
        """Scroll up one line (Vim k)."""
        self._g_pressed = False  # Reset g sequence
        container = self.query_one("#about-container", ScrollableContainer)
        container.scroll_up(animate=False)

    def action_page_down(self) -> None:
        """Scroll down one page (Vim d)."""
        self._g_pressed = False  # Reset g sequence
        container = self.query_one("#about-container", ScrollableContainer)
        container.scroll_page_down()

    def action_page_up(self) -> None:
        """Scroll up one page (Vim u)."""
        self._g_pressed = False  # Reset g sequence
        container = self.query_one("#about-container", ScrollableContainer)
        container.scroll_page_up()

    def action_scroll_end(self) -> None:
        """Scroll to bottom (Vim G)."""
        self._g_pressed = False  # Reset g sequence
        container = self.query_one("#about-container", ScrollableContainer)
        container.scroll_end(animate=True)
