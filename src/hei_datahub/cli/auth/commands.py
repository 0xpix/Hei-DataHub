"""Auth command handlers that return exit codes.

All handlers accept argparse args and return integer exit codes.
No sys.exit() calls - the entrypoint handles process termination.
"""


def handle_auth_setup(args) -> int:
    """Handle auth setup command.

    Returns:
        int: exit code from setup wizard
    """
    from hei_datahub.cli.auth.setup import run_setup_wizard

    exit_code = run_setup_wizard(
        url=args.url,
        username=args.username,
        token=args.token,
        password=args.password,
        library=getattr(args, 'library', None),
        store=args.store,
        no_validate=args.no_validate,
        overwrite=args.overwrite,
        timeout=args.timeout,
        non_interactive=args.non_interactive,
    )
    return exit_code


def handle_auth_status(args) -> int:
    """Handle auth status command.

    Returns:
        int: 0 if configured, 1 if not configured or error
    """
    from hei_datahub.infra.config_paths import get_config_path
    import sys

    config_path = get_config_path()

    if not config_path.exists():
        print("❌ No authentication configured.")
        print(f"   Config file not found: {config_path}")
        print("\nRun: hei-datahub auth setup")
        return 1

    try:
        # Python 3.11+ has tomllib built-in
        try:
            import tomllib as tomli
        except ImportError:
            import tomli

        with open(config_path, "rb") as f:
            config = tomli.load(f)

        auth_config = config.get("auth", {})

        if not auth_config:
            print("❌ No [auth] section in config")
            return 1

        print("🔐 WebDAV Authentication Status\n")
        print(f"Method:     {auth_config.get('method', 'unknown')}")
        print(f"URL:        {auth_config.get('url', 'unknown')}")
        print(f"Username:   {auth_config.get('username', '-')}")
        print(f"Storage:    {auth_config.get('stored_in', 'unknown')}")
        print(f"Key ID:     {auth_config.get('key_id', 'unknown')}")
        print(f"\nConfig:     {config_path}")

        return 0

    except Exception as e:
        print(f"❌ Error reading config: {e}", file=sys.stderr)
        return 1


def handle_auth_doctor(args) -> int:
    """Handle auth doctor diagnostic command.

    Returns:
        int: exit code from doctor
    """
    from hei_datahub.cli.auth.doctor import run_doctor

    exit_code = run_doctor(
        output_json=getattr(args, 'json', False),
        skip_write=getattr(args, 'no_write', False),
        timeout=getattr(args, 'timeout', 8)
    )
    return exit_code


def handle_auth_clear(args) -> int:
    """Handle auth clear command.

    Returns:
        int: exit code from clear operation
    """
    from hei_datahub.cli.auth.clear import run_clear

    exit_code = run_clear(
        force=args.force,
        clear_all=getattr(args, 'all', False)
    )
    return exit_code
