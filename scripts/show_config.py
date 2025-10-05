#!/usr/bin/env python3
"""
Display current Hei-DataHub configuration.

This script shows the active configuration including theme, keybindings,
and other settings. Useful for verifying config changes.
"""
from pathlib import Path
from mini_datahub.services.config import get_config
from mini_datahub.infra.config_paths import get_user_config_file


def main():
    """Display current configuration."""
    config = get_config()
    config_file = get_user_config_file()

    print("=" * 60)
    print("Hei-DataHub Configuration")
    print("=" * 60)
    print(f"\nConfig file: {config_file}")
    print(f"File exists: {config_file.exists()}")

    print("\n" + "-" * 60)
    print("THEME")
    print("-" * 60)
    print(f"Name: {config.get('theme.name')}")
    overrides = config.get('theme.overrides', {})
    if overrides:
        print("Overrides:")
        for k, v in overrides.items():
            print(f"  {k}: {v}")

    print("\n" + "-" * 60)
    print("KEYBINDINGS")
    print("-" * 60)
    keybindings = config.get_keybindings()
    for action, keys in sorted(keybindings.items()):
        keys_str = ", ".join(keys)
        print(f"{action:20s} -> {keys_str}")

    print("\n" + "-" * 60)
    print("SEARCH")
    print("-" * 60)
    print(f"Debounce (ms):      {config.get('search.debounce_ms')}")
    print(f"Max results:        {config.get('search.max_results')}")
    print(f"Highlight enabled:  {config.get('search.highlight_enabled')}")

    print("\n" + "-" * 60)
    print("STARTUP")
    print("-" * 60)
    print(f"Check updates:      {config.get('startup.check_updates')}")
    print(f"Auto reindex:       {config.get('startup.auto_reindex')}")

    print("\n" + "-" * 60)
    print("TELEMETRY")
    print("-" * 60)
    print(f"Opt-in:             {config.get('telemetry.opt_in')}")

    print("\n" + "=" * 60)
    print("\nTo edit: nvim ~/.config/hei-datahub/config.yaml")
    print("=" * 60)


if __name__ == "__main__":
    main()
