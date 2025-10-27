"""Keymap configuration commands.

Handlers return integer exit codes and avoid terminating the process.
"""
import yaml


def handle_keymap_export(args) -> int:
    """Handle keymap export command.

    Returns:
        int: 0 on success, 1 on error
    """
    from hei_datahub.services.config import get_config
    from hei_datahub.infra.config_paths import get_keybindings_export_path
    import sys

    config = get_config()
    keybindings = config.get_keybindings()

    output_path = get_keybindings_export_path(args.output)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump({"keybindings": keybindings}, f, default_flow_style=False)
        print(f"✓ Exported keybindings to: {output_path}")
        return 0
    except Exception as e:
        print(f"❌ Failed to export keybindings: {e}", file=sys.stderr)
        return 1


def handle_keymap_import(args) -> int:
    """Handle keymap import command.

    Returns:
        int: 0 on success, 1 on error
    """
    from hei_datahub.services.config import get_config
    import sys

    config = get_config()
    input_path = args.input

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        keybindings = data.get('keybindings', {})
        if not keybindings:
            print(f"⚠ No keybindings found in {input_path}")
            return 1

        # Validate and import
        config.update_keybindings(keybindings)
        print(f"✓ Imported keybindings from: {input_path}")
        print(f"✓ Applied {len(keybindings)} keybinding sets")
        return 0

    except Exception as e:
        print(f"❌ Failed to import keybindings: {str(e)}", file=sys.stderr)
        return 1
