
<p align="center">
  <img src="assets/png/Hei-datahub-logo-H.png" alt="Logo round" width="250"/>
</p>


<div align="center">

# Hei-DataHub

**A calm inventory experience in your terminal.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Release](https://img.shields.io/github/v/release/0xpix/Hei-DataHub)](https://github.com/0xpix/Hei-DataHub/releases)

[Website](https://hei-datahub.app) • [Documentation](https://hei-datahub.app/docs) • [Report Bug](https://github.com/0xpix/Hei-DataHub/issues)

</div>

---

## ✨ Overview

**Hei-DataHub** is a terminal-based inventory and dataset management tool designed to be fast, minimal, and "zen." It helps you organize and search through your datasets without leaving your keyboard.

## 📦 Installation
Visit the website to download your 

### macOS
Install via our Homebrew tap:
```bash
brew install 0xpix/tap/hei-datahub
```

### Linux (Arch Linux)
Available in the AUR:
```bash
yay -S hei-datahub
```

### Windows & Linux (Universal via `uv`)
If you have [`uv`](https://docs.astral.sh/uv/) installed:
```bash
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
```

### Manual Installation
Download the latest binaries from the [Download Page](https://hei-datahub.app/download).

## ⚡ Quick Start

1.  **Launch the application:**
    ```bash
    hei-datahub
    ```

2.  **Add your first dataset:**
    Press `a` (or your configured binding) to open the "Add Dataset" modal.

3.  **Search:**
    Press `/` to enter search mode.

## ⚙️ Configuration

Hei-DataHub looks for a configuration file in your standard config directory:

- **Linux:** `~/.config/hei-datahub/config.toml`
- **macOS:** `~/Library/Application Support/hei-datahub/config.toml`
- **Windows:** `%APPDATA%\hei-datahub\config.toml`

Example configuration:
```toml
[general]
theme = "dark"
editor = "nvim"

[paths]
data_root = "~/Datasets"
```

Configuration docs coming soon ...

## ⌨️ Keybindings

| Key | Action |
| :--- | :--- |
| `j` / `k` | Navigate list down/up |
| `/` | Search |
| `Enter` | View details |
| `Ctrl+A` | Add new dataset |
| `Ctrl+E` | Edit selected dataset |
| `Ctrl+P` | Show help menu |
| `esc/Ctrl+Q` | Quit |

## 🤝 Contributing

Contributions are welcome! Please look at the [issues](https://github.com/0xpix/Hei-DataHub/issues) to see how you can help.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

<p align="center">
  <strong>Built for research teams who want clean data organization without overhead</strong>
</p>
