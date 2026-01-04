"""TUI launch command.

Handlers should return integer exit codes and avoid terminating the process.
This module provides a handler that returns 0 on success and non-zero on error.
"""

def handle_tui(args) -> int:
    """Handle the default TUI launch.

    Returns:
        int: exit code (0 success, 1 error)
    """
    # Import here to avoid loading heavy UI dependencies for CLI commands
    try:
        # Import the TUI runner on demand
        from hei_datahub.infra.db import ensure_database
        from hei_datahub.ui.views.main import run_tui

        # Ensure database exists (workspace already initialized in main())
        ensure_database()

        # Launch TUI
        run_tui()
        return 0

    except ImportError as e:
        import sys
        print("❌ TUI module import error:", str(e), file=sys.stderr)
        print("Check your installation for v0.60+", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    except KeyboardInterrupt:
        # User interrupted; graceful exit
        print("\nExiting...")
        return 0
    except Exception as e:
        import sys
        print(f"Error launching TUI: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
