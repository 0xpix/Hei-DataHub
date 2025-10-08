"""
Doctor command for Hei-DataHub diagnostics.

Provides comprehensive health checks and actionable diagnostics.
Exit codes:
- 0: healthy
- 1: directory missing/uncreatable
- 2: permission error
- 3: data present but unreadable/invalid
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple

from mini_datahub.infra.platform_paths import (
    resolve_data_directory,
    format_path_for_display,
    get_os_type,
    detect_legacy_linux_path,
    sanitize_windows_filename
)


class DoctorCheck:
    """Result of a doctor diagnostic check."""
    def __init__(self, name: str, status: str, message: str, details: List[str] = None):
        self.name = name
        self.status = status  # 'ok', 'warning', 'error'
        self.message = message
        self.details = details or []


def check_os_info() -> DoctorCheck:
    """Check OS and runtime information."""
    os_type = get_os_type()
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    details = [
        f"OS: {os_type} ({os.name})",
        f"Python: {py_version}",
        f"Platform: {sys.platform}"
    ]

    return DoctorCheck(
        "System Information",
        "ok",
        f"Running on {os_type}",
        details
    )


def check_data_directory(cli_override: str = None) -> Tuple[DoctorCheck, Path, str]:
    """
    Check data directory resolution and access.

    Returns:
        Tuple of (DoctorCheck, resolved_path, reason)
    """
    # Resolve directory
    data_dir, reason = resolve_data_directory(cli_override)

    details = [
        format_path_for_display(data_dir, reason)
    ]

    # Check if directory exists
    if not data_dir.exists():
        # Try to create it
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            details.append("✓ Created directory successfully")
            status = "ok"
            message = "Data directory created"
        except PermissionError:
            details.append("✗ Permission denied - cannot create directory")
            return (
                DoctorCheck("Data Directory", "error", "Permission error", details),
                data_dir,
                reason
            )
        except Exception as e:
            details.append(f"✗ Failed to create: {e}")
            return (
                DoctorCheck("Data Directory", "error", "Cannot create directory", details),
                data_dir,
                reason
            )
    else:
        details.append("✓ Directory exists")
        status = "ok"
        message = "Data directory accessible"

    # Check read/write permissions
    try:
        # Test read
        list(data_dir.iterdir())
        details.append("✓ Read access")

        # Test write
        test_file = data_dir / ".hei-datahub-test"
        test_file.write_text("test")
        test_file.unlink()
        details.append("✓ Write access")

    except PermissionError:
        details.append("✗ Permission denied - cannot read/write")
        return (
            DoctorCheck("Data Directory", "error", "Permission error", details),
            data_dir,
            reason
        )
    except Exception as e:
        details.append(f"⚠ Access test failed: {e}")
        status = "warning"
        message = "Directory accessible but tests failed"

    return (
        DoctorCheck("Data Directory", status, message, details),
        data_dir,
        reason
    )


def check_datasets(data_dir: Path) -> DoctorCheck:
    """Check dataset availability and health."""
    datasets_dir = data_dir / "datasets"

    if not datasets_dir.exists():
        return DoctorCheck(
            "Datasets",
            "warning",
            "No datasets directory",
            ["Directory not found - will be created on first run"]
        )

    try:
        dataset_items = list(datasets_dir.iterdir())
        dataset_count = len([d for d in dataset_items if d.is_dir()])

        if dataset_count == 0:
            return DoctorCheck(
                "Datasets",
                "ok",
                "No datasets (empty)",
                ["0 datasets found - add datasets to get started"]
            )

        # List first 10 datasets
        dataset_names = sorted([d.name for d in dataset_items if d.is_dir()])
        details = [f"Found {dataset_count} dataset(s):"]

        for name in dataset_names[:10]:
            # Check for metadata file
            metadata_path = datasets_dir / name / "metadata.yaml"
            if metadata_path.exists():
                details.append(f"  ✓ {name}")
            else:
                details.append(f"  ⚠ {name} (no metadata.yaml)")

        if len(dataset_names) > 10:
            details.append(f"  ... and {len(dataset_names) - 10} more")

        return DoctorCheck(
            "Datasets",
            "ok",
            f"{dataset_count} dataset(s) available",
            details
        )

    except PermissionError:
        return DoctorCheck(
            "Datasets",
            "error",
            "Cannot read datasets directory",
            ["Permission denied"]
        )
    except Exception as e:
        return DoctorCheck(
            "Datasets",
            "error",
            "Error reading datasets",
            [str(e)]
        )


def check_database(data_dir: Path) -> DoctorCheck:
    """Check database file."""
    db_path = data_dir / "db.sqlite"

    if not db_path.exists():
        return DoctorCheck(
            "Database",
            "ok",
            "Not initialized",
            ["Database will be created on first run"]
        )

    try:
        # Check file size
        size_bytes = db_path.stat().st_size
        size_kb = size_bytes / 1024

        # Try to open it
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if datasets table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='datasets_store'"
        )
        has_table = cursor.fetchone() is not None

        if has_table:
            # Count datasets
            cursor.execute("SELECT COUNT(*) FROM datasets_store")
            count = cursor.fetchone()[0]
            conn.close()

            return DoctorCheck(
                "Database",
                "ok",
                f"Initialized ({size_kb:.1f} KB)",
                [f"{count} indexed dataset(s)"]
            )
        else:
            conn.close()
            return DoctorCheck(
                "Database",
                "warning",
                "Database exists but not initialized",
                [f"Size: {size_kb:.1f} KB", "Run 'hei-datahub reindex' to initialize"]
            )

    except Exception as e:
        return DoctorCheck(
            "Database",
            "error",
            "Cannot read database",
            [str(e)]
        )


def check_migration(data_dir: Path) -> DoctorCheck:
    """Check for legacy paths requiring migration."""
    # Only relevant for Windows/macOS
    os_type = get_os_type()
    if os_type == 'linux':
        return DoctorCheck(
            "Migration",
            "ok",
            "Not applicable (Linux)",
            []
        )

    legacy_path = detect_legacy_linux_path()
    if legacy_path:
        return DoctorCheck(
            "Migration",
            "warning",
            "Legacy Linux-style path detected",
            [
                f"Found: {legacy_path}",
                f"Current: {data_dir}",
                "",
                "To migrate your data:",
                f"1. Copy datasets: cp -r {legacy_path}/datasets/* {data_dir}/datasets/",
                f"2. Run: hei-datahub reindex",
                f"3. Remove old: rm -rf {legacy_path}"
            ]
        )

    return DoctorCheck(
        "Migration",
        "ok",
        "No legacy paths detected",
        []
    )


def check_windows_sanitation(data_dir: Path) -> DoctorCheck:
    """Check for Windows filename issues."""
    os_type = get_os_type()
    if os_type != 'windows':
        return DoctorCheck(
            "Filename Sanitation",
            "ok",
            "Not applicable (not Windows)",
            []
        )

    datasets_dir = data_dir / "datasets"
    if not datasets_dir.exists():
        return DoctorCheck(
            "Filename Sanitation",
            "ok",
            "No datasets to check",
            []
        )

    issues = []
    try:
        for item in datasets_dir.iterdir():
            if item.is_dir():
                sanitized = sanitize_windows_filename(item.name)
                if sanitized != item.name:
                    issues.append(f"{item.name} → {sanitized}")

        if issues:
            details = ["Found names requiring sanitation:"] + issues
            return DoctorCheck(
                "Filename Sanitation",
                "warning",
                f"{len(issues)} name(s) need sanitation",
                details
            )
        else:
            return DoctorCheck(
                "Filename Sanitation",
                "ok",
                "All filenames are Windows-safe",
                []
            )
    except Exception as e:
        return DoctorCheck(
            "Filename Sanitation",
            "error",
            "Cannot check filenames",
            [str(e)]
        )


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

    data_check, data_dir, reason = check_data_directory(cli_override)
    checks.append(data_check)

    # Only run dependent checks if data directory is accessible
    if data_check.status != 'error':
        checks.append(check_datasets(data_dir))
        checks.append(check_database(data_dir))
        checks.append(check_migration(data_dir))
        checks.append(check_windows_sanitation(data_dir))

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
            if 'permission' in check.message.lower():
                exit_code = max(exit_code, 2)
            elif check.name == "Data Directory":
                exit_code = max(exit_code, 1)
            else:
                exit_code = max(exit_code, 3)

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

    # Helpful tips
    if exit_code > 0:
        print("Suggestions:")
        if exit_code == 1:
            print("  • Check that the data directory path is valid")
            print("  • Try using --data-dir to specify a custom location")
        elif exit_code == 2:
            print("  • Check file system permissions")
            print("  • Try running with appropriate access rights")
        elif exit_code == 3:
            print("  • Run 'hei-datahub reindex' to rebuild the database")
            print("  • Check dataset metadata.yaml files for errors")
        print()

    return exit_code
