# Releasing Hei-DataHub

## Prerequisites for Automated Homebrew Updates

To enable the automatic update of the Homebrew tap upon release, the following secrets must be added to this repository:

1.  **Repository Settings**: Go to **Settings** > **Secrets and variables** > **Actions**.
2.  **Add New Repository Secret**: Click **New repository secret**.

### Required Secrets

| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `TAP_BOT_APP_ID` | `<App ID>` | The numeric App ID of the GitHub App bot. |
| `TAP_BOT_PRIVATE_KEY` | `<PEM Key>` | The full content of the private key `.pem` file. Include `-----BEGIN...` and `-----END...`. |

### GitHub App Configuration

The GitHub App used for this automation must have:

*   **Installation**: Installed on the repository `0xpix/homebrew-tap`.
*   **Permissions**: `Contents: Read & Write` on the installed repository.
