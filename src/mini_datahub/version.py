"""
Version information for mini-datahub.

This module reads version data directly from version.yaml at runtime.
For version updates, simply edit version.yaml - no sync step needed!
"""
import yaml
from pathlib import Path
from typing import Tuple


def _load_version_data() -> dict:
    """
    Load version data from version.yaml.

    Returns:
        Dictionary with version metadata
    """
    # Try package directory first (works in both dev and installed)
    version_file = Path(__file__).parent / "version.yaml"

    # Fallback: try project root (for dev mode)
    if not version_file.exists():
        version_file = Path(__file__).parent.parent.parent / "version.yaml"

    # Last resort: use defaults if file not found
    if not version_file.exists():
        return {
            "version": "0.0.0-dev",
            "codename": "Unknown",
            "release_date": "Unknown",
            "compatibility": "Unknown",
            "notes": "",
            "app_name": "Hei-DataHub",
            "github_repo": "0xpix/Hei-DataHub",
        }

    try:
        with open(version_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        # Return defaults on any error
        return {
            "version": "0.0.0-dev",
            "codename": "Unknown",
            "release_date": "Unknown",
            "compatibility": "Unknown",
            "notes": "",
            "app_name": "Hei-DataHub",
            "github_repo": "0xpix/Hei-DataHub",
        }


# Load version data once at module import
_VERSION_DATA = _load_version_data()


def _parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse version string into tuple."""
    parts = version_str.split("-")[0].split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0, 0)


# Version Components
__version__ = _VERSION_DATA.get("version", "0.0.0-dev")
__version_info__ = _parse_version(__version__) + (_VERSION_DATA.get("version", "").split("-")[1] if "-" in _VERSION_DATA.get("version", "") else "",)

# Application Metadata
__app_name__ = _VERSION_DATA.get("app_name", "Hei-DataHub")
__license__ = _VERSION_DATA.get("license", "MIT")
__description__ = "A local-first TUI for managing datasets with consistent metadata"

# Build Information
_version_parts = __version__.split("-")[0].split(".")
BUILD_NUMBER = "".join(f"{int(p):02d}" for p in _version_parts[:3])
RELEASE_DATE = _VERSION_DATA.get("release_date", "Unknown")
CODENAME = _VERSION_DATA.get("codename", "Unknown")
COMPATIBILITY = _VERSION_DATA.get("compatibility", "Unknown")
RELEASE_NOTES = _VERSION_DATA.get("notes", "")

# Repository Information
GITHUB_REPO = _VERSION_DATA.get("github_repo", "0xpix/Hei-DataHub")
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"
ISSUES_URL = f"{GITHUB_URL}/issues"
DOCS_URL = "https://0xpix.github.io/Hei-DataHub"

# Update Check Configuration
UPDATE_CHECK_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
UPDATE_CHECK_INTERVAL = 86400  # 24 hours in seconds


def get_version_string(include_build: bool = False) -> str:
    """Get the version string with optional build number."""
    version = __version__
    if include_build:
        version = f"{version} (build {BUILD_NUMBER})"
    return version


def get_version_info() -> dict:
    """Get comprehensive version information as a dictionary."""
    import sys
    return {
        "version": __version__,
        "version_tuple": __version_info__,
        "app_name": __app_name__,
        "build_number": BUILD_NUMBER,
        "release_date": RELEASE_DATE,
        "codename": CODENAME,
        "compatibility": COMPATIBILITY,
        "release_notes": RELEASE_NOTES,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_implementation": sys.implementation.name,
        "github_repo": GITHUB_REPO,
        "github_url": GITHUB_URL,
        "docs_url": DOCS_URL,
    }


def print_version_info(verbose: bool = False) -> None:
    """Print version information to stdout with beautiful formatting."""
    try:
        from rich.console import Console
        from pathlib import Path
        import sys
        import platform

        console = Console()

        # Load dog ASCII art
        dog_path = Path(__file__).parent / "ui" / "assets" / "ascii" / "dog.txt"
        if dog_path.exists():
            dog_lines = dog_path.read_text().splitlines()
        else:
            dog_lines = ["[ASCII art not found]"]

        # Prepare info lines based on verbosity
        if verbose:
            info_lines = [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                f"[bold cyan]{__app_name__}[/bold cyan]",
                "",
                f"[bold]Version:[/bold] [green]{__version__}[/green]",
                f"[bold]Codename:[/bold] [yellow]{CODENAME}[/yellow]",
                f"[bold]Build:[/bold] {BUILD_NUMBER}",
                f"[bold]Release Date:[/bold] {RELEASE_DATE}",
                "",
                f"[bold]Python:[/bold] {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                f"[bold]Platform:[/bold] {platform.system()} {platform.machine()}",
                "",
                f"[bold]Repository:[/bold]",
                f"  [link={GITHUB_URL}]{GITHUB_URL}[/link]",
                f"[bold]Documentation:[/bold]",
                f"  [link={DOCS_URL}]{DOCS_URL}[/link]",
            ]
        else:
            info_lines = [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                f"[bold cyan]{__app_name__}[/bold cyan]",
                "",
                f"[bold]Version:[/bold] [green]{__version__}[/green]",
                f"[bold]Codename:[/bold] [yellow]{CODENAME}[/yellow]",
                "",
                f"[dim]Use --version-info for details[/dim]",
            ]

        # Calculate max width of dog ASCII (for padding)
        dog_width = max(len(line) for line in dog_lines) if dog_lines else 0

        # Build side-by-side display: dog on left, info on right
        console.print()
        for i in range(max(len(dog_lines), len(info_lines))):
            # Get dog line (left side)
            dog_line = dog_lines[i] if i < len(dog_lines) else ""

            # Get info line (right side)
            info_line = info_lines[i] if i < len(info_lines) else ""

            # Print dog in dim cyan + spacing + info
            # Using markup=True to handle Rich formatting in info_line
            console.print(f"[dim cyan]{dog_line.ljust(dog_width)}[/dim cyan]  {info_line}", highlight=False)

        console.print()

    except ImportError:
        # Fallback to simple text if Rich is not available
        print(f"{__app_name__} {__version__}")
        if verbose:
            print(f"Build: {BUILD_NUMBER}")
            print(f"Release Date: {RELEASE_DATE}")
            print(f"Codename: {CODENAME}")
            print(f"Compatibility: {COMPATIBILITY}")
            print(f"Repository: {GITHUB_URL}")
            print(f"Documentation: {DOCS_URL}")
            import sys
            print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ({sys.implementation.name})")


__all__ = [
    "__version__",
    "__version_info__",
    "__app_name__",
    "__license__",
    "__description__",
    "BUILD_NUMBER",
    "RELEASE_DATE",
    "CODENAME",
    "COMPATIBILITY",
    "RELEASE_NOTES",
    "GITHUB_REPO",
    "GITHUB_URL",
    "ISSUES_URL",
    "DOCS_URL",
    "UPDATE_CHECK_URL",
    "UPDATE_CHECK_INTERVAL",
    "get_version_string",
    "get_version_info",
    "print_version_info",
]
