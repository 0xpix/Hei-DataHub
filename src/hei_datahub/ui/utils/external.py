"""
Cross-platform external URL opener with clipboard fallback.

Provides a robust mechanism to open URLs in the user's default browser,
with fallbacks for packaged environments (PyInstaller, AppImage, pipx, etc.).
"""
import logging
import os
import shutil
import subprocess
import sys
from typing import Optional

logger = logging.getLogger(__name__)

# Enable verbose debug logging with HEI_DEBUG_UPDATER=1
_DEBUG = os.environ.get("HEI_DEBUG_UPDATER", "").strip() in ("1", "true", "yes")


def _debug(msg: str) -> None:
    """Log debug message, always log if HEI_DEBUG_UPDATER is set."""
    if _DEBUG:
        logger.warning(f"[DEBUG-URL] {msg}")
    else:
        logger.debug(msg)


def _try_webbrowser(url: str) -> bool:
    """
    Attempt to open URL via Python's webbrowser module.

    May fail on some packaged Linux installs due to readline symbol conflicts.
    """
    try:
        import webbrowser

        result = webbrowser.open(url, new=2)
        _debug(f"webbrowser.open returned: {result}")
        return bool(result)
    except Exception as e:
        _debug(f"webbrowser.open failed: {e}")
        return False


def _try_macos_open(url: str) -> bool:
    """macOS: use /usr/bin/open."""
    try:
        proc = subprocess.run(
            ["open", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=10,
            start_new_session=True,
        )
        ok = proc.returncode == 0
        _debug(f"macOS 'open' returned {proc.returncode}")
        if not ok:
            _debug(f"macOS 'open' stderr: {proc.stderr}")
        return ok
    except Exception as e:
        _debug(f"macOS 'open' exception: {e}")
        return False


def _try_linux_xdg_open(url: str) -> bool:
    """Linux: use xdg-open, fully detached from the current terminal.

    Inside a Textual TUI the terminal is in raw / alternate-screen mode,
    which can prevent xdg-open from working correctly. We solve this by
    double-forking so the child process has no connection to the current
    TTY at all.
    """
    xdg = shutil.which("xdg-open")
    if not xdg:
        _debug("xdg-open not found in PATH")
        return False

    env = os.environ.copy()

    try:
        # Double-fork: the intermediate child exits immediately, so the
        # grandchild is re-parented to init/systemd and has no controlling
        # terminal from Textual.
        pid = os.fork()
        if pid == 0:
            # --- First child ---
            try:
                os.setsid()  # new session, no controlling terminal
                # Second fork so the session leader exits and the
                # grandchild can never accidentally acquire a TTY.
                pid2 = os.fork()
                if pid2 == 0:
                    # --- Grandchild: exec xdg-open ---
                    # Close inherited fds from Textual
                    devnull = os.open(os.devnull, os.O_RDWR)
                    os.dup2(devnull, 0)
                    os.dup2(devnull, 1)
                    os.dup2(devnull, 2)
                    if devnull > 2:
                        os.close(devnull)
                    os.execve(xdg, [xdg, url], env)
                else:
                    os._exit(0)  # first child exits
            except Exception:
                os._exit(1)
        else:
            # --- Parent (Textual process) ---
            os.waitpid(pid, 0)  # reap the first child (instant)
            _debug(f"xdg-open double-forked (first child pid={pid})")
            return True
    except Exception as e:
        _debug(f"xdg-open double-fork exception: {e}")
        return False


def _try_windows_startfile(url: str) -> bool:
    """Windows: use os.startfile (only exists on Windows)."""
    try:
        os.startfile(url)  # type: ignore[attr-defined]
        _debug("os.startfile succeeded")
        return True
    except AttributeError:
        _debug("os.startfile not available (not Windows)")
        return False
    except Exception as e:
        _debug(f"os.startfile exception: {e}")
        return False


def _try_windows_start(url: str) -> bool:
    """Windows fallback: use 'start' shell command."""
    try:
        proc = subprocess.run(
            ["cmd", "/c", "start", "", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        ok = proc.returncode == 0
        _debug(f"Windows 'start' returned {proc.returncode}")
        return ok
    except Exception as e:
        _debug(f"Windows 'start' exception: {e}")
        return False


def open_external_url(url: str) -> bool:
    """
    Open a URL in the user's default browser, cross-platform.

    Strategy:
    1. Platform-specific native command (most reliable in packaged envs)
    2. webbrowser.open() as fallback

    Args:
        url: The URL to open.

    Returns:
        True if the URL was likely opened; False on all failures.
    """
    _debug(f"Opening URL: {url}")
    _debug(f"Platform: {sys.platform}")

    if sys.platform == "darwin":
        if _try_macos_open(url):
            return True
        _debug("macOS 'open' failed, trying webbrowser")
        return _try_webbrowser(url)

    if sys.platform == "win32":
        if _try_windows_startfile(url):
            return True
        if _try_windows_start(url):
            return True
        _debug("Windows native methods failed, trying webbrowser")
        return _try_webbrowser(url)

    # Linux / other Unix
    if _try_linux_xdg_open(url):
        return True
    _debug("xdg-open failed, trying webbrowser")
    return _try_webbrowser(url)


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard (best-effort, cross-platform).

    Args:
        text: Text to copy.

    Returns:
        True if copied successfully.
    """
    # Try pyperclip first (if available)
    try:
        import pyperclip

        pyperclip.copy(text)
        _debug("Copied to clipboard via pyperclip")
        return True
    except Exception:
        pass

    # Platform-specific fallbacks
    if sys.platform == "darwin":
        try:
            subprocess.run(
                ["pbcopy"],
                input=text.encode(),
                check=True,
                timeout=5,
            )
            return True
        except Exception:
            pass

    elif sys.platform == "win32":
        try:
            subprocess.run(
                ["clip"],
                input=text.encode(),
                check=True,
                timeout=5,
            )
            return True
        except Exception:
            pass

    else:
        # Linux: try xclip, then xsel, then wl-copy (Wayland)
        for cmd in [
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
            ["wl-copy"],
        ]:
            if shutil.which(cmd[0]):
                try:
                    subprocess.run(
                        cmd,
                        input=text.encode(),
                        check=True,
                        timeout=5,
                    )
                    return True
                except Exception:
                    continue

    _debug("All clipboard methods failed")
    return False
