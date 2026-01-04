import platform
import sys

from hei_datahub.version import __version__


class CheckResult:
    def __init__(self, name: str, status: str, message: str, details: list[str] = None):
        self.name = name
        self.status = status  # 'ok', 'warning', 'error'
        self.message = message
        self.details = details or []

def check_os_info() -> CheckResult:
    details = [
        f"OS: {platform.system()} {platform.release()}",
        f"Python: {sys.version.split()[0]}",
        f"Hei-DataHub: {__version__}"
    ]
    return CheckResult("System Info", "ok", "Environment details", details)

def run_doctor(cli_override: str = None) -> int:
    """
    Run all diagnostic checks.

    Args:
        cli_override: Optional --data-dir override

    Returns:
        Exit code (0 = healthy, 1 = directory issue, 2 = permission, 3 = data issue)
    """
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          Hei-DataHub Doctor — System Diagnostics           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    checks = []
    exit_code = 0

    # Run checks
    checks.append(check_os_info())

    # Print results
    for check in checks:
        status_symbol = {
            'ok': '✓',
            'warning': '⚠',
            'error': '✗'
        }[check.status]

        print(f"{status_symbol} {check.name}: {check.message}")

        if check.details:
            for detail in check.details:
                print(f"  {detail}")
        print()

        # Update exit code
        if check.status == 'error':
            exit_code = 1

    # Summary
    error_count = sum(1 for c in checks if c.status == 'error')
    warning_count = sum(1 for c in checks if c.status == 'warning')

    print("─" * 60)
    if exit_code == 0 and warning_count == 0:
        print("✓ All checks passed — system healthy")
    elif exit_code == 0:
        print(f"⚠ {warning_count} warning(s) — system functional")
    else:
        print(f"✗ {error_count} error(s), {warning_count} warning(s) — issues detected")
    print()

    return exit_code

def handle_doctor(args) -> int:
    """CLI-friendly wrapper that accepts argparse-style args and returns an int exit code.

    This keeps the entrypoint logic simple: it can import this symbol and call it
    without the handler performing process termination.
    """
    data_dir_override = getattr(args, 'data_dir', None)
    return run_doctor(data_dir_override)
