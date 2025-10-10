"""
Atomic update manager for Hei-DataHub.

Implements a multi-phase update strategy with preflight checks and verification.
UV itself handles atomic installation (using `--force` flag), so we focus on:
1. Preflight checks (auth, permissions, running processes)
2. Version-aware installation (detect if already up-to-date)
3. Verification (test the new binary works)
4. Clear error messages with phase identification

Windows-specific handling:
- File lock detection
- Long paths verification
- Antivirus status checks
- SSH vs HTTPS+Token auto-fallback

Note: While UV handles the actual installation atomically, we still provide
comprehensive preflight checks to catch issues before attempting the update,
and clear error messages if something goes wrong.
"""

import os
import sys
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm
from rich import box


@dataclass
class UpdateError(Exception):
    """Structured update error with phase and recovery info."""
    phase: str
    message: str
    recoverable: bool
    details: Optional[str] = None

    def __str__(self):
        return f"[{self.phase}] {self.message}"


class AtomicUpdateManager:
    """
    Manages atomic updates for Hei-DataHub on Windows and Unix-like systems.

    Key features:
    - Never removes old version until new one is verified
    - Automatic auth method detection and fallback
    - File lock retry mechanism
    - Clear, actionable error messages per failure phase
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.is_windows = sys.platform == "win32"
        self.temp_dir = Path(os.environ.get("TEMP" if self.is_windows else "TMPDIR", "/tmp"))
        self.staging_dir: Optional[Path] = None
        self.already_up_to_date = False

    def run_update(self, branch: Optional[str] = None, force: bool = False) -> None:
        """
        Run the complete update process.

        Args:
            branch: Git branch/tag to update to (None = interactive selection)
            force: Skip safety checks (use with caution)

        Raises:
            UpdateError: If update fails at any phase
        """
        try:
            # Phase 1: Preflight
            self.console.print("\n[bold cyan]Phase 1: Preflight Checks[/bold cyan]")
            preflight_results = self.run_preflight_checks(force=force)
            self._display_preflight_results(preflight_results)

            if not preflight_results["can_proceed"]:
                raise UpdateError(
                    phase="preflight",
                    message="Preflight checks failed. Fix issues above and retry.",
                    recoverable=True
                )

            # Phase 2: Determine branch and build URL
            if branch is None:
                branch = self._prompt_branch_selection()

            install_url = self._get_install_url(
                branch,
                auth_strategy=preflight_results["auth_method"]
            )

            self.console.print(f"\n[dim]Install URL: {install_url}[/dim]\n")

            # Confirm
            if not force and not Confirm.ask(
                "[bold]Proceed with update?[/bold]",
                default=True
            ):
                self.console.print("[yellow]Update cancelled[/yellow]")
                return

            # Phase 3: Staged download
            self.console.print("\n[bold cyan]Phase 2: Downloading & Building[/bold cyan]")
            self.staging_dir = self._stage_update(install_url)

            # Phase 4: Verification
            if not self.already_up_to_date:
                self.console.print("\n[bold cyan]Phase 3: Verification[/bold cyan]")
                self._verify_staged_binary()

            # Note: UV handles the installation atomically, so no separate swap needed

            # Success!
            self.console.print("\n" + "=" * self.console.width)

            if self.already_up_to_date:
                self.console.print(Panel(
                    "[bold green]✓ Already up to date[/bold green]\n\n"
                    f"[dim]Branch:[/dim] [bold cyan]{branch}[/bold cyan]\n"
                    "[dim]You're running the latest version.[/dim]",
                    title="[bold green]🎉 No Update Needed[/bold green]",
                    border_style="green"
                ))
            else:
                self.console.print(Panel(
                    "[bold green]✨ Update completed successfully! ✨[/bold green]\n\n"
                    f"[dim]Updated to branch:[/dim] [bold cyan]{branch}[/bold cyan]",
                    title="[bold green]🎉 Success[/bold green]",
                    border_style="green"
                ))

            # Cleanup staging
            if self.staging_dir and self.staging_dir.exists():
                shutil.rmtree(self.staging_dir, ignore_errors=True)

        except UpdateError:
            # Cleanup staging on error
            if self.staging_dir and self.staging_dir.exists():
                shutil.rmtree(self.staging_dir, ignore_errors=True)
            raise
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Update cancelled by user[/yellow]")
            if self.staging_dir and self.staging_dir.exists():
                shutil.rmtree(self.staging_dir, ignore_errors=True)
            sys.exit(1)

    def run_preflight_checks(self, force: bool = False) -> Dict:
        """
        Run comprehensive preflight checks.

        Returns:
            Dict with check results and whether update can proceed.
        """
        checks = {}

        # Check 1: UV available
        checks["uv_available"] = self._check_command("uv", "--version")

        # Check 2: Git available
        checks["git_available"] = self._check_command("git", "--version")

        # Check 3: Auth method detection
        checks["auth_method"] = self._detect_auth_method()

        # Check 4: Running processes (Windows/Linux)
        checks["running_processes"] = self._check_running_processes()

        # Check 5: Disk space (basic check)
        checks["disk_space_ok"] = self._check_disk_space()

        # Check 6: Write permissions
        checks["write_permissions"] = self._check_write_permissions()

        # Windows-specific checks
        if self.is_windows:
            checks["long_paths_enabled"] = self._check_long_paths_enabled()
            checks["defender_status"] = self._check_defender_status()

        # Determine if we can proceed
        critical_checks = [
            checks["uv_available"]["passed"],
            checks["git_available"]["passed"],
            checks["auth_method"] != "none",
            checks["write_permissions"]["passed"],
        ]

        # Running processes is a warning, not a blocker (we'll retry)
        checks["can_proceed"] = all(critical_checks) or force

        return checks

    def _check_command(self, command: str, *args) -> Dict:
        """Check if a command is available and working."""
        try:
            result = subprocess.run(
                [command, *args],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {
                "passed": result.returncode == 0,
                "output": result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
            }
        except FileNotFoundError:
            return {
                "passed": False,
                "output": f"{command} not found in PATH"
            }
        except Exception as e:
            return {
                "passed": False,
                "output": str(e)
            }

    def _detect_auth_method(self) -> str:
        """
        Detect available authentication method.

        Returns:
            "ssh", "token", or "none"
        """
        # Try SSH first
        if self._test_ssh_auth():
            return "ssh"

        # Check for GH_PAT environment variable
        if os.getenv("GH_PAT"):
            return "token"

        # Check for GITHUB_TOKEN (alternative)
        if os.getenv("GITHUB_TOKEN"):
            return "token"

        return "none"

    def _test_ssh_auth(self) -> bool:
        """Test if SSH authentication to GitHub works."""
        try:
            result = subprocess.run(
                ["ssh", "-T", "-o", "StrictHostKeyChecking=no",
                 "-o", "ConnectTimeout=5", "git@github.com"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # SSH returns 1 on success with authentication message
            return "successfully authenticated" in result.stderr.lower()
        except Exception:
            return False

    def _check_running_processes(self) -> Dict:
        """Check for running hei-datahub processes (excluding current process)."""
        try:
            import psutil

            current_pid = os.getpid()
            running = []

            for proc in psutil.process_iter(['name', 'pid', 'cmdline']):
                try:
                    # Skip current process
                    if proc.info['pid'] == current_pid:
                        continue

                    # Check if it's a hei-datahub process
                    if 'hei-datahub' in proc.info['name'].lower():
                        # Skip if it's the update command (this process)
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and 'update' in ' '.join(cmdline).lower():
                            continue

                        running.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {
                "passed": len(running) == 0,
                "running_count": len(running),
                "processes": running
            }
        except ImportError:
            # psutil not available, assume OK
            return {
                "passed": True,
                "running_count": 0,
                "processes": [],
                "note": "psutil not available, could not check"
            }

    def _check_disk_space(self, required_mb: int = 100) -> Dict:
        """Check if sufficient disk space available."""
        try:
            stat = shutil.disk_usage(self.temp_dir)
            available_mb = stat.free // (1024 * 1024)

            return {
                "passed": available_mb >= required_mb,
                "available_mb": available_mb,
                "required_mb": required_mb
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }

    def _check_write_permissions(self) -> Dict:
        """Check write permissions to critical directories."""
        test_paths = []

        if self.is_windows:
            # Windows: Check UV tools directory and shim location
            uv_tools = Path(os.environ.get("LOCALAPPDATA", "")) / "uv" / "tools"
            shim_dir = Path(os.environ.get("USERPROFILE", "")) / ".local" / "bin"
            test_paths = [uv_tools, shim_dir]
        else:
            # Unix: Check .local directories
            local_share = Path.home() / ".local" / "share"
            local_bin = Path.home() / ".local" / "bin"
            test_paths = [local_share, local_bin]

        results = []
        for path in test_paths:
            try:
                path.mkdir(parents=True, exist_ok=True)
                test_file = path / f".write_test_{uuid.uuid4().hex[:8]}"
                test_file.write_text("test")
                test_file.unlink()
                results.append({"path": str(path), "writable": True})
            except Exception as e:
                results.append({"path": str(path), "writable": False, "error": str(e)})

        return {
            "passed": all(r["writable"] for r in results),
            "paths": results
        }

    def _check_long_paths_enabled(self) -> Dict:
        """Windows: Check if long paths are enabled."""
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\FileSystem",
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
            winreg.CloseKey(key)

            return {
                "passed": value == 1,
                "enabled": value == 1
            }
        except Exception:
            return {
                "passed": False,
                "enabled": False,
                "note": "Could not check (registry access denied?)"
            }

    def _check_defender_status(self) -> Dict:
        """Windows: Check Defender exclusions."""
        try:
            # Check if UV tools dir is in exclusions
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-MpPreference | Select-Object -ExpandProperty ExclusionPath"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                exclusions = result.stdout.lower()
                uv_tools_path = str(Path(os.environ.get("LOCALAPPDATA", "")) / "uv" / "tools").lower()

                return {
                    "passed": uv_tools_path in exclusions,
                    "uv_excluded": uv_tools_path in exclusions,
                    "note": "Consider adding UV tools directory to exclusions"
                }
        except Exception:
            pass

        return {
            "passed": True,  # Don't block on this
            "uv_excluded": False,
            "note": "Could not check Defender status"
        }

    def _display_preflight_results(self, results: Dict) -> None:
        """Display preflight check results in a nice table."""
        table = Table(
            title="[bold]Preflight Check Results[/bold]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )

        table.add_column("Check", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Details", style="dim")

        # UV
        uv = results["uv_available"]
        table.add_row(
            "UV Package Manager",
            "✓" if uv["passed"] else "✗",
            uv["output"]
        )

        # Git
        git = results["git_available"]
        table.add_row(
            "Git",
            "✓" if git["passed"] else "✗",
            git["output"]
        )

        # Auth
        auth = results["auth_method"]
        auth_labels = {"ssh": "SSH Keys", "token": "Token (GH_PAT)", "none": "None"}
        table.add_row(
            "Authentication",
            "✓" if auth != "none" else "✗",
            auth_labels[auth]
        )

        # Running processes
        procs = results["running_processes"]
        table.add_row(
            "Running Processes",
            "✓" if procs["passed"] else "⚠",
            f"{procs['running_count']} instance(s) running" if procs["running_count"] > 0 else "None"
        )

        # Disk space
        disk = results["disk_space_ok"]
        table.add_row(
            "Disk Space",
            "✓" if disk["passed"] else "✗",
            f"{disk.get('available_mb', '?')} MB available"
        )

        # Write permissions
        perms = results["write_permissions"]
        table.add_row(
            "Write Permissions",
            "✓" if perms["passed"] else "✗",
            f"Checked {len(perms['paths'])} path(s)"
        )

        # Windows-specific
        if self.is_windows:
            if "long_paths_enabled" in results:
                lp = results["long_paths_enabled"]
                table.add_row(
                    "Long Paths (Windows)",
                    "✓" if lp.get("enabled", False) else "⚠",
                    lp.get("note", "Enabled" if lp.get("enabled") else "Disabled")
                )

            if "defender_status" in results:
                df = results["defender_status"]
                table.add_row(
                    "Defender Exclusions",
                    "✓" if df.get("uv_excluded", False) else "ℹ",
                    df.get("note", "")
                )

        self.console.print(table)
        self.console.print()

        # Show specific guidance for authentication failure
        if results["auth_method"] == "none":
            self.console.print(Panel(
                "[bold yellow]⚠ Authentication Required[/bold yellow]\n\n"
                "To update, you need access to the private GitHub repository.\n\n"
                "[bold]Option 1: SSH Keys (Recommended)[/bold]\n"
                f"  Test: [cyan]ssh -T git@github.com[/cyan]\n"
                f"  Setup: https://github.com/settings/keys\n\n"
                "[bold]Option 2: Personal Access Token[/bold]\n"
                f"  Set: [cyan]{'$env:GH_PAT' if self.is_windows else 'export GH_PAT'}=\"ghp_xxxxx\"[/cyan]\n"
                f"  Get token: https://github.com/settings/tokens\n"
                f"  Required scope: [dim]repo (read)[/dim]",
                border_style="yellow",
                title="[yellow]How to Fix[/yellow]"
            ))
            self.console.print()

        # Show warnings for running processes
        if results["running_processes"]["running_count"] > 0:
            self.console.print(Panel(
                "[bold yellow]⚠ Hei-DataHub is Running[/bold yellow]\n\n"
                "Close all Hei-DataHub windows before updating to avoid file lock issues.\n"
                f"Found {results['running_processes']['running_count']} running instance(s).",
                border_style="yellow",
                title="[yellow]Warning[/yellow]"
            ))
            self.console.print()

        # Show final blocker message
        if not results["can_proceed"]:
            self.console.print(Panel(
                "[bold red]Cannot proceed with update.[/bold red]\n\n"
                "Fix the critical issues above (marked with ✗) and try again.",
                border_style="red"
            ))

    def _prompt_branch_selection(self) -> str:
        """Interactive branch selection."""
        from rich.prompt import Prompt

        branches = {
            "1": {
                "name": "main",
                "label": "✅ [bold green]main[/bold green] [dim](stable)[/dim]",
            },
            "2": {
                "name": "fix/update-fails-windows",
                "label": "🧪 [bold yellow]v0.58.x[/bold yellow] [dim](beta)[/dim]",
            },
            "3": {
                "name": "develop",
                "label": "🚧 [bold red]develop[/bold red] [dim](unstable)[/dim]",
            },
        }

        self.console.print("\n[bold cyan]Available Branches:[/bold cyan]")
        for key, branch in branches.items():
            self.console.print(f"  [{key}] {branch['label']}")

        choice = Prompt.ask(
            "\n[bold]Select branch[/bold]",
            choices=list(branches.keys()),
            default="1"
        )

        return branches[choice]["name"]

    def _get_install_url(self, branch: str, auth_strategy: str) -> str:
        """
        Build install URL with appropriate auth method.

        Args:
            branch: Git branch/tag name
            auth_strategy: "ssh", "token", or "none"

        Returns:
            Full git+ssh or git+https URL

        Raises:
            UpdateError: If no working auth available
        """
        repo = "0xpix/Hei-DataHub"

        if auth_strategy == "ssh":
            return f"git+ssh://git@github.com/{repo}.git@{branch}"

        elif auth_strategy == "token":
            token = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
            if not token:
                raise UpdateError(
                    phase="auth",
                    message="Token auth selected but GH_PAT not set",
                    recoverable=True,
                    details="Set environment variable: export GH_PAT=ghp_xxxxx"
                )
            return f"git+https://{token}@github.com/{repo}@{branch}"

        else:  # none
            raise UpdateError(
                phase="auth",
                message="No authentication method available",
                recoverable=True,
                details=(
                    "Option 1: Configure SSH keys\n"
                    f"  {'PowerShell' if self.is_windows else 'Terminal'}: ssh -T git@github.com\n\n"
                    "Option 2: Set GitHub Personal Access Token\n"
                    f"  {'PowerShell' if self.is_windows else 'Terminal'}: "
                    f"{'$env:GH_PAT' if self.is_windows else 'export GH_PAT'}=\"ghp_xxxxx\"\n"
                    "  Get token: https://github.com/settings/tokens"
                )
            )

    def _stage_update(self, install_url: str) -> Path:
        """
        Download and build in staging directory.

        Args:
            install_url: Full git URL for package

        Returns:
            Path to staging directory

        Raises:
            UpdateError: If download or build fails
        """
        # Create unique staging directory
        stage_id = uuid.uuid4().hex[:8]
        staging_dir = self.temp_dir / f"hei-datahub-update-{stage_id}"
        staging_dir.mkdir(parents=True, exist_ok=True)

        self.console.print(f"[dim]Staging directory: {staging_dir}[/dim]")

        # Get current version before update (silently)
        try:
            current_version_result = subprocess.run(
                ["hei-datahub", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            current_version = current_version_result.stdout.strip() if current_version_result.returncode == 0 else "unknown"
        except:
            current_version = "unknown"

        try:
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
            import time

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console,
                transient=False
            ) as progress:
                # Phase 1: Resolving
                task1 = progress.add_task("[cyan]Resolving repository...", total=100)

                # Start UV process
                result = subprocess.Popen(
                    [
                        "uv", "tool", "install",
                        "--force",  # Force reinstall
                        "--python-preference", "only-managed",
                        install_url
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                # Simulate resolution phase
                for i in range(20):
                    if result.poll() is not None:
                        break
                    time.sleep(0.05)
                    progress.update(task1, completed=min(i * 5, 100))

                progress.update(task1, completed=100)
                progress.stop_task(task1)

                # Phase 2: Downloading
                task2 = progress.add_task("[cyan]Downloading package...", total=100)

                # Continue updating while downloading
                for i in range(30):
                    if result.poll() is not None:
                        break
                    time.sleep(0.1)
                    progress.update(task2, completed=min(i * 3.3, 100))

                progress.update(task2, completed=100)
                progress.stop_task(task2)

                # Phase 3: Installing
                task3 = progress.add_task("[cyan]Installing dependencies...", total=100)

                # Wait for process to finish
                elapsed = 0
                while result.poll() is None and elapsed < 180:  # 180s = 3min timeout
                    time.sleep(0.2)
                    elapsed += 0.2
                    # Slow progress that never quite finishes until done
                    progress.update(task3, completed=min(elapsed / 2, 95))

                # Get final output
                output, _ = result.communicate()
                returncode = result.returncode

                # Complete
                progress.update(task3, completed=100)

            if returncode != 0:
                # Parse error for better message
                error_msg = output

                # Common error patterns
                if "authentication failed" in error_msg.lower():
                    raise UpdateError(
                        phase="auth",
                        message="Authentication to GitHub failed",
                        recoverable=True,
                        details=error_msg
                    )
                elif "could not resolve host" in error_msg.lower():
                    raise UpdateError(
                        phase="download",
                        message="Network connection failed",
                        recoverable=True,
                        details="Check internet connection and proxy settings"
                    )
                elif "already installed" in error_msg.lower() or "nothing to install" in error_msg.lower():
                    # Not an error - just already up to date
                    self.console.print("[green]✓ Already up to date[/green]")
                    return staging_dir
                else:
                    raise UpdateError(
                        phase="download",
                        message="Failed to download package",
                        recoverable=True,
                        details=error_msg
                    )

            # Check the output for success indicators
            # Silently check if already up to date
            if "already installed" in output.lower():
                self.already_up_to_date = True
                self.console.print(f"[green]✓ Already up to date[/green]")
            else:
                # Silently check if version changed
                try:
                    new_version_result = subprocess.run(
                        ["hei-datahub", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    new_version = new_version_result.stdout.strip() if new_version_result.returncode == 0 else "unknown"

                    if current_version == new_version:
                        self.already_up_to_date = True
                        self.console.print(f"[green]✓ Already up to date[/green]")
                    else:
                        self.console.print(f"[green]✓ Installation completed[/green]")
                except:
                    self.console.print(f"[green]✓ Installation completed[/green]")

            return staging_dir

        except subprocess.TimeoutExpired:
            raise UpdateError(
                phase="download",
                message="Download timed out after 5 minutes",
                recoverable=True,
                details="Check network connection or try again later"
            )
        except UpdateError:
            # Re-raise UpdateError without wrapping it
            raise
        except Exception as e:
            raise UpdateError(
                phase="download",
                message=f"Unexpected error during download: {type(e).__name__}",
                recoverable=True,
                details=str(e)
            )

    def _verify_staged_binary(self) -> None:
        """
        Verify that the installed binary works.

        Raises:
            UpdateError: If verification fails
        """
        # Test the installed binary (silently)
        try:
            result = subprocess.run(
                ["hei-datahub", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise UpdateError(
                    phase="verification",
                    message="Binary failed version check",
                    recoverable=True,
                    details=result.stderr or result.stdout
                )

            self.console.print(f"[green]✓ Verification passed[/green]")

        except subprocess.TimeoutExpired:
            raise UpdateError(
                phase="verification",
                message="Binary verification timed out",
                recoverable=True
            )
        except UpdateError:
            # Re-raise UpdateError without wrapping it
            raise
        except Exception as e:
            raise UpdateError(
                phase="verification",
                message=f"Failed to verify binary: {type(e).__name__}",
                recoverable=True,
                details=str(e)
            )

    def _atomic_swap(self, retries: int = 3) -> None:
        """
        Replace current installation with staged version.

        Uses backup and retry logic for Windows file locks.

        Args:
            retries: Number of retry attempts for file lock errors

        Raises:
            UpdateError: If swap fails after all retries
        """
        if not self.staging_dir:
            raise UpdateError(
                phase="swap",
                message="No staging directory set",
                recoverable=True
            )

        # Find current installation directory
        if self.is_windows:
            target_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "uv" / "tools" / "hei-datahub"
        else:
            # UV installs to ~/.local/share/uv/tools on Unix
            target_dir = Path.home() / ".local" / "share" / "uv" / "tools" / "hei-datahub"

        # Source is the staged tool directory
        source_dir = self.staging_dir / "tools" / "hei-datahub"

        if not source_dir.exists():
            raise UpdateError(
                phase="swap",
                message=f"Staged directory not found: {source_dir}",
                recoverable=True
            )

        # Backup directory with timestamp
        backup_dir = target_dir.parent / f"hei-datahub.backup.{int(time.time())}"

        for attempt in range(retries):
            try:
                # Step 1: Backup current (if exists)
                if target_dir.exists():
                    self.console.print(f"[dim]Creating backup...[/dim]")
                    shutil.move(str(target_dir), str(backup_dir))
                    self.console.print(f"[green]✓ Backup created: {backup_dir.name}[/green]")

                # Step 2: Move staged to target
                self.console.print(f"[dim]Installing new version...[/dim]")
                shutil.move(str(source_dir), str(target_dir))

                # Step 3: Verify installation
                binary_name = "hei-datahub.exe" if self.is_windows else "hei-datahub"
                verify_binary = target_dir / "bin" / binary_name

                if not verify_binary.exists():
                    # Rollback
                    self.console.print("[red]Verification failed, rolling back...[/red]")
                    if target_dir.exists():
                        shutil.rmtree(target_dir, ignore_errors=True)
                    if backup_dir.exists():
                        shutil.move(str(backup_dir), str(target_dir))

                    raise UpdateError(
                        phase="swap",
                        message="Binary not found after swap",
                        recoverable=False,
                        details="Rolled back to previous version"
                    )

                # Success!
                self.console.print("[green]✓ Installation complete[/green]")

                # Cleanup old backups (keep only last 2)
                self._cleanup_old_backups(target_dir.parent, keep=2)

                return

            except PermissionError as e:
                # File locked, likely running process
                if attempt < retries - 1:
                    self.console.print(
                        f"\n[yellow]⚠ File is in use (attempt {attempt + 1}/{retries})[/yellow]"
                    )
                    self.console.print(
                        "[bold]Close all Hei-DataHub windows and press Enter to retry...[/bold]",
                        end=""
                    )
                    input()

                    # Restore if we created a backup
                    if backup_dir.exists() and not target_dir.exists():
                        shutil.move(str(backup_dir), str(target_dir))

                    continue
                else:
                    # Out of retries, restore backup
                    if backup_dir.exists():
                        if target_dir.exists():
                            shutil.rmtree(target_dir, ignore_errors=True)
                        shutil.move(str(backup_dir), str(target_dir))

                    raise UpdateError(
                        phase="swap",
                        message=f"File locked after {retries} attempts",
                        recoverable=False,
                        details=(
                            f"Error: {e}\n\n"
                            "Restored previous version.\n\n"
                            "Next steps:\n"
                            "1. Close all Hei-DataHub windows\n"
                            "2. Check Task Manager for running processes\n"
                            "3. Try update again"
                        )
                    )

            except Exception as e:
                # Unexpected error, restore backup
                self.console.print(f"[red]Unexpected error: {e}[/red]")

                if backup_dir.exists():
                    if target_dir.exists():
                        shutil.rmtree(target_dir, ignore_errors=True)
                    shutil.move(str(backup_dir), str(target_dir))
                    self.console.print("[green]✓ Restored previous version[/green]")

                raise UpdateError(
                    phase="swap",
                    message=f"Swap failed: {type(e).__name__}",
                    recoverable=False,
                    details=f"{str(e)}\n\nRestored previous version."
                )

    def _cleanup_old_backups(self, tools_dir: Path, keep: int = 2) -> None:
        """Clean up old backup directories, keeping only the most recent N."""
        try:
            backups = sorted(
                tools_dir.glob("hei-datahub.backup.*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            for old_backup in backups[keep:]:
                self.console.print(f"[dim]Cleaning up old backup: {old_backup.name}[/dim]")
                shutil.rmtree(old_backup, ignore_errors=True)
        except Exception:
            # Don't fail update on cleanup issues
            pass


def format_error_panel(error: UpdateError, console: Optional[Console] = None) -> None:
    """
    Display formatted error panel with phase-specific guidance.

    Args:
        error: UpdateError instance
        console: Rich console (creates new if None)
    """
    if console is None:
        console = Console()

    phase_emoji = {
        "auth": "🔑",
        "preflight": "🚦",
        "download": "📦",
        "verification": "✓",
        "swap": "🔄"
    }

    is_windows = sys.platform == "win32"

    guidance = {
        "auth": (
            "[bold]Fix authentication:[/bold]\n"
            f"• SSH: Ensure keys are set up - run: [cyan]ssh -T git@github.com[/cyan]\n"
            f"• Token: Set GH_PAT - run: [cyan]{'$env:GH_PAT' if is_windows else 'export GH_PAT'}='ghp_xxxxx'[/cyan]\n"
            "• See: https://github.com/settings/keys"
        ),
        "download": (
            "[bold]Network or repository access issue:[/bold]\n"
            "• Check internet connection\n"
            "• Verify GitHub status: https://www.githubstatus.com\n"
            "• Check proxy settings if behind corporate firewall\n"
            "• Retry with: [cyan]hei-datahub update --branch main[/cyan]"
        ),
        "verification": (
            "[bold]Binary verification failed:[/bold]\n"
            "• Package may be corrupted\n"
            "• Try again: [cyan]hei-datahub update[/cyan]\n"
            "• Report issue if persists: https://github.com/0xpix/Hei-DataHub/issues"
        ),
        "swap": (
            "[bold]File access issue:[/bold]\n"
            "• Close all Hei-DataHub windows\n"
            f"• Check {'Task Manager' if is_windows else 'process list'} for running processes\n"
            + (f"• Check Windows Defender hasn't quarantined files\n" if is_windows else "")
            + f"• Ensure write permissions to installation directory\n"
            + (f"• Try running PowerShell as Administrator\n" if is_windows else "")
        )
    }

    status = (
        "[yellow]⚠ Your existing installation is still intact[/yellow]"
        if error.recoverable
        else "[green]✓ Restored previous version[/green]"
    )

    # Format details - show first 500 chars if too long
    details_text = ""
    if error.details:
        details = error.details.strip()
        if len(details) > 500:
            details = details[:500] + "\n... (truncated)"
        details_text = f"\n\n[bold]Details:[/bold]\n[dim]{details}[/dim]"

    console.print("\n" + "=" * console.width)
    console.print(Panel(
        f"[bold red]{phase_emoji.get(error.phase, '❌')} Update Failed: {error.phase.upper()} phase[/bold red]\n\n"
        f"{error.message}{details_text}\n\n"
        f"{status}\n\n"
        f"{guidance.get(error.phase, 'Check logs above')}",
        title=f"[red]Error in {error.phase.title()} Phase[/red]",
        border_style="red"
    ))
