"""
UI asset loading utilities.

This module provides functions to load UI assets (logos, stylesheets, help files)
from either user config paths or packaged defaults.
"""
import logging
from pathlib import Path
from typing import Optional
from importlib import resources

logger = logging.getLogger(__name__)


def get_logo_text(config) -> str:
    """
    Load logo text from config or use packaged default.

    Args:
        config: ConfigManager instance

    Returns:
        Logo text as string
    """
    logo_config = config.get_logo_config()
    logo_path = logo_config.get("path")

    # Try user path first if specified
    if logo_path:
        user_path = Path(logo_path).expanduser()
        if user_path.exists():
            try:
                with open(user_path, "r", encoding="utf-8") as f:
                    text = f.read()
                logger.info(f"Loaded logo from user path: {user_path}")
                return text
            except Exception as e:
                logger.warning(f"Failed to load logo from {user_path}: {e}, falling back to default")

    # Fall back to packaged default
    try:
        # Use importlib.resources for Python 3.9+ compatibility
        try:
            # Python 3.9+
            from importlib.resources import files
            logo_file = files("hei_datahub.ui.assets.ascii").joinpath("logo_default.txt")
            text = logo_file.read_text(encoding="utf-8")
        except (ImportError, AttributeError):
            # Fallback for older Python
            import pkg_resources
            text = pkg_resources.resource_string(
                "hei_datahub.ui.assets.ascii",
                "logo_default.txt"
            ).decode("utf-8")

        logger.debug("Loaded packaged default logo")
        return text
    except Exception as e:
        logger.error(f"Failed to load packaged logo: {e}")
        # Ultimate fallback to simple text
        return "HEI DATAHUB"


def _detect_version_codename():
    """
    Detect version and codename from the package.

    Returns:
        Tuple of (version, codename) as strings
    """
    try:
        from hei_datahub.version import __version__ as VERSION, CODENAME
        return str(VERSION or ""), str(CODENAME or "")
    except Exception:
        return "", ""


def format_logo(text: str, config) -> str:
    """
    Format logo with color and alignment from config.

    Args:
        text: Raw logo text
        config: ConfigManager instance

    Returns:
        Formatted logo text with Rich markup
    """
    logo_config = config.get_logo_config()
    color = logo_config.get("color", "cyan")
    align = logo_config.get("align", "center")
    padding_top = logo_config.get("padding_top", 0)
    padding_bottom = logo_config.get("padding_bottom", 1)

    # Add color markup - wrap entire block, not line by line
    # Add padding
    padding_top_lines = [""] * padding_top
    padding_bottom_lines = [""] * padding_bottom

    all_lines = padding_top_lines + [text] + padding_bottom_lines
    formatted = "\n".join(all_lines)

    # Wrap in color tags
    formatted = f"[bold {color}]{formatted}[/bold {color}]"

    # Add version tag if enabled
    if logo_config.get("show_version_tag", True):
        ver, code = _detect_version_codename()
        if ver or code:
            fmt = logo_config.get("version_format", "v{version} — {codename}")
            style = logo_config.get("version_style", None)
            tag = fmt.format(version=ver, codename=code).strip()

            if style:
                tag = f"[{style}]{tag}[/{style}]"

            # Calculate logo width (without Rich markup)
            lines = text.rstrip("\n").splitlines()
            width = max((len(line.expandtabs(4)) for line in lines), default=len(tag))

            # Right-align the version tag
            version_line = tag.rjust(width)

            # Append version line to formatted output
            formatted = formatted + "\n" + version_line

    return formatted


def get_logo_widget_text(config) -> str:
    """
    Get fully formatted logo text ready for Static widget.

    Args:
        config: ConfigManager instance

    Returns:
        Formatted logo text
    """
    try:
        raw_text = get_logo_text(config)
        return format_logo(raw_text, config)
    except Exception as e:
        logger.error(f"Error loading logo: {e}")
        return "[bold cyan]HEI DATAHUB"


def get_stylesheets(config) -> list[Path]:
    """
    Get list of stylesheet paths (user + packaged).

    Args:
        config: ConfigManager instance

    Returns:
        List of Path objects for TCSS files
    """
    stylesheets = []

    # Add packaged base styles (always included)
    try:
        from importlib.resources import files
        base_style = files("hei_datahub.ui.styles").joinpath("base.tcss")
        if base_style.exists():
            stylesheets.append(Path(str(base_style)))
    except Exception as e:
        logger.warning(f"Could not load packaged base styles: {e}")

    # Add user styles
    user_stylesheets = config.get_stylesheets()
    for stylesheet_path in user_stylesheets:
        path = Path(stylesheet_path).expanduser()
        if path.exists():
            stylesheets.append(path)
            logger.info(f"Added user stylesheet: {path}")
        else:
            logger.warning(f"User stylesheet not found: {path}")

    return stylesheets


def load_help_text(config) -> Optional[str]:
    """
    Load help text from custom file or return None to use built-in.

    Args:
        config: ConfigManager instance

    Returns:
        Help text or None
    """
    help_file = config.get_help_file_path()

    if not help_file:
        return None

    help_path = Path(help_file).expanduser()
    if not help_path.exists():
        logger.warning(f"Help file not found: {help_path}")
        return None

    try:
        with open(help_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to load help file: {e}")
        return None
