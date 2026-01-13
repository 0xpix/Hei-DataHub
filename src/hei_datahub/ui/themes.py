"""
Custom themes for Hei-DataHub.
"""
from textual.theme import Theme


# Custom light theme with good contrast
HEI_DATAHUB_LIGHT = Theme(
    name="hei-datahub-light",
    primary="#0066cc",       # Deep blue - primary actions
    secondary="#6c757d",     # Gray - secondary elements
    warning="#cc7700",       # Orange - warnings
    error="#cc3333",         # Red - errors
    success="#228b22",       # Forest green - success
    accent="#8b5cf6",        # Purple - accents
    foreground="#1a1a2e",    # Very dark blue-gray - text
    background="#f8f9fa",    # Light gray - main background
    surface="#ffffff",       # White - cards/panels
    panel="#e9ecef",         # Slightly darker - panel backgrounds
    boost="#dee2e6",         # Even darker - borders/dividers
    dark=False,
    luminosity_spread=0.12,
    text_alpha=1.0,          # Full opacity for crisp text
)

# Custom dark theme matching your brand
HEI_DATAHUB_DARK = Theme(
    name="hei-datahub-dark",
    primary="#89b4fa",       # Catppuccin blue
    secondary="#a6adc8",     # Subtext
    warning="#f9e2af",       # Yellow
    error="#f38ba8",         # Red/pink
    success="#a6e3a1",       # Green
    accent="#cba6f7",        # Mauve/purple
    foreground="#cdd6f4",    # Light text
    background="#1e1e2e",    # Base dark
    surface="#313244",       # Surface
    panel="#45475a",         # Overlay
    boost="#585b70",         # Surface2
    dark=True,
    luminosity_spread=0.15,
    text_alpha=0.95,
)


def register_custom_themes(app) -> None:
    """Register custom themes with the app."""
    app.register_theme(HEI_DATAHUB_LIGHT)
    app.register_theme(HEI_DATAHUB_DARK)
