# Development Setup

Detailed setup guide for different development environments.

## Prerequisites

### Required Tools

```bash
# Check if you have everything
python --version   # 3.11 or higher
git --version      # Any recent version
```

### Install uv (Package Manager)

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Verify
uv --version
```

## Installation Methods

### Method 1: Standard Development (Recommended)

```bash
# Clone repository
git clone https://github.com/0xpix/Hei-DataHub.git
cd Hei-DataHub

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install in editable mode
uv sync --dev

# Verify
hei-datahub --version
```

### Method 2: Development with All Extras

```bash
# Install with all optional dependencies
uv sync --all-extras

# This includes:
# - dev: Development tools (black, ruff, mypy)
# - test: Testing tools (pytest, coverage)
# - docs: Documentation tools (mkdocs, plugins)
```

### Method 3: Minimal Installation

```bash
# Only core dependencies
uv sync --no-dev
```

## IDE Configuration

### Visual Studio Code

#### 1. Install Extensions

Open Command Palette (`Ctrl+Shift+P`) and install:

- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Ruff** (charliermarsh.ruff)
- **Even Better TOML** (tamasfe.even-better-toml)

#### 2. Configure Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "editor.formatOnSave": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    },
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    ".ruff_cache": true,
    "*.egg-info": true
  }
}
```

#### 3. Create Tasks

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Application",
      "type": "shell",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "hei_datahub.cli.main"],
      "problemMatcher": []
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "${workspaceFolder}/.venv/bin/pytest",
      "problemMatcher": []
    },
    {
      "label": "Format Code",
      "type": "shell",
      "command": "${workspaceFolder}/.venv/bin/black",
      "args": ["src/", "tests/"],
      "problemMatcher": []
    }
  ]
}
```

#### 4. Create Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Hei-DataHub",
      "type": "python",
      "request": "launch",
      "module": "hei_datahub.cli.main",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Debug Current Test",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${file}",
        "-v"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

### PyCharm

#### 1. Open Project

```bash
# PyCharm will automatically detect pyproject.toml
pycharm-professional Hei-DataHub/
# or
pycharm-community Hei-DataHub/
```

#### 2. Configure Interpreter

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add Interpreter → Add Local Interpreter
3. Select "Existing environment"
4. Choose `.venv/bin/python`

#### 3. Enable Pytest

1. File → Settings → Tools → Python Integrated Tools
2. Default test runner: pytest
3. pytest target: tests directory

#### 4. Configure Formatting

1. File → Settings → Tools → File Watchers
2. Add Black formatter:
   - Program: `.venv/bin/black`
   - Arguments: `$FilePath$`
   - Working directory: `$ProjectFileDir$`

### Vim/Neovim

Add to your config:

```lua
-- Using lazy.nvim
{
  'neovim/nvim-lspconfig',
  config = function()
    require('lspconfig').pylsp.setup {
      settings = {
        pylsp = {
          plugins = {
            pycodestyle = { enabled = false },
            flake8 = { enabled = false },
            pylint = { enabled = false },
            ruff = { enabled = true },
          }
        }
      }
    }
  end
}
```

## Environment Variables

Create a `.env` file in the project root:

```bash
# Development settings
LOG_LEVEL=DEBUG
HEI_DATAHUB_CONFIG=~/.config/hei-datahub/dev-config.yaml
HEI_DATAHUB_DB=./dev-db.sqlite

# WebDAV credentials (optional, for sync features)
# Stored in system keyring - use `hei-datahub auth setup`
```

Load in your shell:

```bash
# Add to ~/.bashrc or ~/.zshrc
export $(cat .env | xargs)
```

## Git Configuration

### Set Up Commit Hooks (Pre-commit)

```bash
# Install pre-commit
uv add --dev pre-commit

# Install git hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

### Configure Git

```bash
# Set your identity
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Useful aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm commit
```

## Shell Configuration

### Bash/Zsh Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Hei-DataHub development aliases
alias hd='hei-datahub'
alias hd-dev='hei-datahub --verbose'
alias hd-test='pytest tests/'
alias hd-format='black src/ tests/ && isort src/ tests/'
alias hd-lint='ruff check src/ tests/'

# Quick navigation
alias cdh='cd ~/Github/Hei-DataHub'
```

## Database Setup

### Development Database

```bash
# Create separate dev database
export HEI_DATAHUB_DB=./dev-db.sqlite
hei-datahub  # Will create dev-db.sqlite
```

### Test Database

```bash
# Automatically handled by pytest fixtures
pytest  # Uses temporary test database
```

## Verification Checklist

After setup, verify everything works:

```bash
# 1. Python version
python --version  # Should be 3.11+

# 2. Virtual environment
which python  # Should point to .venv/bin/python

# 3. Package installed
hei-datahub --version  # Should show version

# 4. Tests pass
pytest  # Should pass all tests

# 5. Linting works
ruff check src/  # Should show no errors

# 6. Formatting works
black --check src/  # Should show "All done!"

# 7. App runs
hei-datahub  # Should start TUI
```

## Troubleshooting

### "uv command not found"

```bash
# Ensure uv is in PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or install with pip
pip install uv
```

### "Python version mismatch"

```bash
# Use pyenv to manage Python versions
curl https://pyenv.run | bash
pyenv install 3.11
pyenv local 3.11
```

### "Module not found" errors

```bash
# Reinstall in editable mode
uv sync --dev

# Or sync dependencies
uv sync
```

### IDE not finding modules

1. **VSCode**: `Ctrl+Shift+P` → "Python: Select Interpreter" → Choose `.venv/bin/python`
2. **PyCharm**: Settings → Project → Python Interpreter → Select `.venv/bin/python`

---

**Next**: [Common Tasks →](common-tasks.md)
