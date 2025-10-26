# Release Notes Draft - v0.60-beta (Authentication Fixes)

## 🔐 Authentication & Configuration

This release addresses critical issues with the authentication setup and dataset creation workflow.

### Key Fixes

*   **Unified Authentication Storage**: The GUI "Auth Wizard" and the CLI `hei-datahub auth setup` command now use a consistent storage format for credentials and configuration. This resolves the issue where setting up auth in the GUI was not recognized by other parts of the application.
*   **"Auth Setup Required" Error Resolved**: Fixed a bug where the "Add Dataset" screen would incorrectly prompt users to run `hei-datahub auth setup` even after they had successfully configured authentication in the Settings.
*   **Dataset Upload Reliability**: Improved the dataset creation process (`dataset_add.py`) to robustly handle authentication errors. Users will now see specific error messages if their credentials are invalid or missing, rather than a generic failure or silent error.
*   **CLI Compatibility**: The CLI auth setup has been verified and aligned with the GUI wizard, ensuring that users can switch between tools without breaking their configuration.

### 🖥️ Desktop Integration

*   **Smarter Auto-Install**: The automatic desktop integration (icons, menu entry) is now disabled when running in development mode, when running from the repository root, or when the `HEI_DATAHUB_SKIP_DESKTOP_INSTALL` environment variable is set. This prevents accidental overwrites of stable desktop entries during testing.
*   **No Default Data Seeding**: The application no longer copies example datasets to the local machine on first run. This streamlines the initial setup and is ideal for cloud-only workflows.

### Technical Details

*   **Config Format**: The `config.toml` file now consistently includes `method`, `stored_in`, and `library` fields in the `[auth]` section.
*   **Credential Storage**: Credentials are stored in the system keyring using the standard `heibox:password:{username}@{host}` key format.
*   **Improved Prompts**: The setup wizard now clearly distinguishes between the user's SSO login password and the required **HeiBox WebDAV Password**, guiding users to find the correct credential in their HeiBox settings.
*   **Backward Compatibility**: The storage manager has been updated to gracefully handle older configuration formats where possible, though re-running the setup is recommended.

### Migration

Users who previously set up authentication in v0.60-beta (pre-fix) should re-run the authentication setup to ensure their configuration is updated to the correct format.

1.  **GUI**: Go to **Settings** -> **WebDAV Setup** and complete the wizard.
2.  **CLI**: Run `hei-datahub auth setup`.

See `DEV/0.60-beta/AUTH_MIGRATION_GUIDE.md` for more details.
