"""Paths diagnostic command.

Handlers must return integer exit codes and avoid terminating the process.
"""

def handle_paths(args) -> int:
    """Handle paths diagnostic command.

    Returns:
        int: exit code (0 success)
    """
    from hei_datahub.infra import paths
    import os

    print("Hei-DataHub Paths Diagnostic")
    print("=" * 60)
    print()

    # Installation mode
    is_installed = paths._is_installed_package()
    is_dev = paths._is_dev_mode()

    print(f"Installation Mode:")
    if is_installed:
        print("  ✓ Installed package (standalone)")
    elif is_dev:
        print("  ✓ Development mode (repository)")
    else:
        print("  ⚠ Fallback mode")
    print()

    # XDG directories
    print(f"XDG Base Directories:")
    print(f"  XDG_CONFIG_HOME: {paths.XDG_CONFIG_HOME}")
    print(f"  XDG_DATA_HOME:   {paths.XDG_DATA_HOME}")
    print(f"  XDG_CACHE_HOME:  {paths.XDG_CACHE_HOME}")
    print(f"  XDG_STATE_HOME:  {paths.XDG_STATE_HOME}")
    print()

    # Application paths
    print(f"Application Paths:")
    print(f"  Config:    {paths.CONFIG_DIR}")
    print(f"    Exists:  {'✓' if paths.CONFIG_DIR.exists() else '✗'}")
    print(f"  Data:      {paths.DATA_DIR}")
    print(f"    Exists:  {'✓' if paths.DATA_DIR.exists() else '✗'}")
    if paths.DATA_DIR.exists():
        dataset_count = len(list(paths.DATA_DIR.iterdir()))
        print(f"    Datasets: {dataset_count}")
    print(f"  Cache:     {paths.CACHE_DIR}")
    print(f"    Exists:  {'✓' if paths.CACHE_DIR.exists() else '✗'}")
    print(f"  State:     {paths.STATE_DIR}")
    print(f"    Exists:  {'✓' if paths.STATE_DIR.exists() else '✗'}")
    print(f"  Logs:      {paths.LOG_DIR}")
    print(f"    Exists:  {'✓' if paths.LOG_DIR.exists() else '✗'}")
    print()

    # Important files
    print(f"Important Files:")
    print(f"  Database:  {paths.DB_PATH}")
    print(f"    Exists:  {'✓' if paths.DB_PATH.exists() else '✗'}")
    if paths.DB_PATH.exists():
        size_bytes = paths.DB_PATH.stat().st_size
        size_kb = size_bytes / 1024
        print(f"    Size:    {size_kb:.1f} KB")
    print(f"  Schema:    {paths.SCHEMA_JSON}")
    print(f"    Exists:  {'✓' if paths.SCHEMA_JSON.exists() else '✗'}")
    print(f"  Config:    {paths.CONFIG_FILE}")
    print(f"    Exists:  {'✓' if paths.CONFIG_FILE.exists() else '✗'}")
    print(f"  Keymap:    {paths.KEYMAP_FILE}")
    print(f"    Exists:  {'✓' if paths.KEYMAP_FILE.exists() else '✗'}")
    print()

    # Environment variables
    print(f"Environment Variables:")
    for var in ['XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME']:
        val = os.environ.get(var, '<not set>')
        print(f"  {var}: {val}")
    print()

    print("=" * 60)
    return 0
