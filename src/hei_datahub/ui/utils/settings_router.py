"""
Settings router - decides whether to show wizard or settings screen.
"""
try:
    import tomllib as tomli
except ImportError:
    import tomli  # type:ignore


from hei_datahub.infra.config_paths import get_config_path


def open_settings_screen(app) -> None:
    """
    Open appropriate settings screen based on configuration state.

    If WebDAV is already configured, open the full settings screen.
    If not configured, open the guided wizard.
    """
    config_path = get_config_path()

    # Check if config exists and has auth section
    is_configured = False

    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                config = tomli.load(f)

            # Check if auth section exists with required fields
            auth_config = config.get("auth", {})
            if auth_config.get("url") and auth_config.get("username"):
                is_configured = True
        except Exception:
            pass

    # Import and push appropriate screen
    if is_configured:
        from hei_datahub.ui.views.settings import SettingsScreen
        app.push_screen(SettingsScreen())
    else:
        from hei_datahub.ui.widgets.settings_wizard import SettingsWizard
        app.push_screen(SettingsWizard())
