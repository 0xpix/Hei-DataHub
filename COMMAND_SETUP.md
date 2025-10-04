# Running `hei-datahub` Without `uv run`

The `hei-datahub` command is now configured and available! Here are your options:

## 🚀 Quick Setup (30 seconds)

**Most users should do this:**

```bash
cd /home/pix/Github/Hei-DataHub
source .venv/bin/activate
hei-datahub
```

That's it! While the virtual environment is activated, you can run `hei-datahub` from anywhere.

---

## All Available Options

## ✅ Option 1: Activate the Virtual Environment (Recommended)

```bash
# Activate the virtual environment
source .venv/bin/activate

# Now you can run directly:
hei-datahub
hei-datahub --version
hei-datahub reindex

# When done, deactivate:
deactivate
```

## ✅ Option 2: Add to PATH for Current Session

```bash
# Add .venv/bin to your PATH temporarily
export PATH="/home/pix/Github/Hei-DataHub/.venv/bin:$PATH"

# Now you can run from anywhere:
hei-datahub
```

## ✅ Option 3: Create a Shell Alias (Persistent)

Add this to your `~/.zshrc`:

```bash
# Hei-DataHub alias
alias hei-datahub='/home/pix/Github/Hei-DataHub/.venv/bin/hei-datahub'
```

Then reload your shell:
```bash
source ~/.zshrc
```

## ✅ Option 4: Use the Makefile

The Makefile has been updated to use `hei-datahub`:

```bash
make run       # Launch the TUI
make reindex   # Rebuild search index
```

## ✅ Option 5: Run Directly from .venv/bin

```bash
# From the project directory
./.venv/bin/hei-datahub

# Or with absolute path from anywhere
/home/pix/Github/Hei-DataHub/.venv/bin/hei-datahub
```

## ✅ Option 6: Use the Convenience Script

A `hei-datahub.sh` wrapper script has been created:

```bash
# From the project directory
./hei-datahub.sh

# Or make it globally available by creating a symlink:
mkdir -p ~/.local/bin
ln -sf /home/pix/Github/Hei-DataHub/hei-datahub.sh ~/.local/bin/hei-datahub

# Then run from anywhere (if ~/.local/bin is in your PATH):
hei-datahub
```

## Quick Start (Recommended)

For the easiest experience, just activate the virtual environment:

```bash
cd /home/pix/Github/Hei-DataHub
source .venv/bin/activate
hei-datahub
```

## Verification

Both commands are available:
- ✅ `hei-datahub` - Main command (your preference)
- ✅ `mini-datahub` - Alternative command (still works)

```bash
# Test it works
source .venv/bin/activate
hei-datahub --version
# Output: mini-datahub v0.40-beta
```

## Configuration Files Updated

1. **pyproject.toml** - Added `hei-datahub` as an additional entry point
2. **Makefile** - Updated to use `hei-datahub` by default

Both commands (`hei-datahub` and `mini-datahub`) point to the same application and work identically.
