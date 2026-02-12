"""
About screen showing project information, logo, and story.

Redesigned with a minimalistic, retro-inspired aesthetic for terminal elegance.
"""
import webbrowser

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Header, Label, Static

from hei_datahub.services.config import get_config
from hei_datahub.ui.assets.loader import get_logo_widget_text
from hei_datahub.ui.widgets.contextual_footer import ContextualFooter


GITHUB_URL = "https://github.com/0xpix/Hei-DataHub"
DOCS_URL = "https://docs.hei-datahub.app"


class OpenFooter(Static):
    """Footer shown during open-link mode."""

    DEFAULT_CSS = """
    OpenFooter {
        dock: bottom;
        width: 100%;
        height: 2;
        background: $surface;
        color: $text;
        border-top: wide $accent;
        padding: 0 1;
        display: none;
        text-align: center;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label(
            "[bold reverse #60a5fa] OPEN [/]  "
            "[bold]g[/]:GitHub  "
            "[bold]d[/]:Docs  "
            "[bold]Esc[/]:cancel",
            markup=True,
        )


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
        self._open_mode = False
        self._open_auto_cancel_timer = None

    def compose(self) -> ComposeResult:
        """Compose the about screen layout."""
        from hei_datahub.version import __version__

        # Load logo from config
        get_logo_widget_text(get_config())

        with ScrollableContainer(id="about-container"):
            with Container(id="about-card"):

                yield Static(f"Hei-DataHub  v{__version__}", id="version-badge")
                yield Static("─" * 60, classes="separator")

                # Origin
                yield Static("[b #d4a574]The Origin[/b #d4a574]", classes="section-title")
                yield Static(
                    "Hei-DataHub started with a simple frustration: dataset tracking "
                    "had turned into a mess of Excel files, broken links, and tools "
                    "that slowed research down instead of supporting it.\n\n"
                    "Finding the right dataset often means interrupting colleagues, "
                    "digging through old emails, or searching across scattered folders. "
                    "The data exists—but never where or when you need it.\n\n"
                    "Hei-DataHub brings everything into one place. A fast, local inventory "
                    "that lets you find the right dataset in a split second—without "
                    "messages, meetings, or context switching.",
                    classes="section-content"
                )

                yield Static("─" * 60, classes="separator")

                # Philosophy - compact pillars
                yield Static("[b #d4a574]Philosophy[/b #d4a574]", classes="section-title")

                with Vertical(id="philosophy-grid"):
                    yield Static(
                        "  [b #a78bfa]Privacy First[/b #a78bfa]      Your data belongs to you.\n"
                        "  [b #a78bfa]Speed Matters[/b #a78bfa]      Fuzzy search. Instant results.\n"
                        "  [b #a78bfa]Simplicity[/b #a78bfa]         One thing, done well.\n"
                        "  [b #a78bfa]Open Source[/b #a78bfa]        Transparent and hackable.",
                        classes="section-content philosophy-items"
                    )

                yield Static("─" * 60, classes="separator")

                # Links
                yield Static("[b #d4a574]Links[/b #d4a574]", classes="section-title")
                yield Static(
                    "  GitHub  [link]https://github.com/0xpix/Hei-DataHub[/link]\n"
                    "  Docs    [link]https://docs.hei-datahub.app[/link]",
                    classes="section-content"
                )

                yield Static("", classes="spacer")
                yield Static("Made with 󰋑 by PIX", id="footer-hint")

        footer = ContextualFooter()
        footer.set_context("about")
        yield footer
        yield OpenFooter()

    def on_key(self, event: events.Key) -> None:
        """Handle key presses for open-link mode."""
        # Open mode active — waiting for g or d
        if self._open_mode:
            if self._open_auto_cancel_timer:
                self._open_auto_cancel_timer.stop()

            if event.key == "escape":
                self._exit_open_mode()
                event.stop()
                return

            key = event.key.lower() if len(event.key) == 1 else event.key

            if key == "g":
                webbrowser.open(GITHUB_URL)
                self.app.notify(f"Opened GitHub")
                self._exit_open_mode()
                event.stop()
            elif key == "d":
                webbrowser.open(DOCS_URL)
                self.app.notify(f"Opened Docs")
                self._exit_open_mode()
                event.stop()
            else:
                self.app.notify("Open cancelled", severity="warning")
                self._exit_open_mode()
                event.stop()
            return

        # Normal mode — 'o' enters open mode
        if event.key == "o":
            self._enter_open_mode()
            event.stop()

    def _enter_open_mode(self) -> None:
        """Activate open-link mode."""
        self._open_mode = True
        self.query_one(ContextualFooter).styles.display = "none"
        self.query_one(OpenFooter).styles.display = "block"
        self._open_auto_cancel_timer = self.set_timer(5.0, self._exit_open_mode)

    def _exit_open_mode(self) -> None:
        """Deactivate open-link mode."""
        self._open_mode = False
        if self._open_auto_cancel_timer:
            self._open_auto_cancel_timer.stop()
        try:
            self.query_one(OpenFooter).styles.display = "none"
            self.query_one(ContextualFooter).styles.display = "block"
        except Exception:
            pass

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
