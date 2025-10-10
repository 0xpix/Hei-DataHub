# Binary Build Guide - Hei-DataHub

## Overview

The `build_desktop_binary.sh` script creates a standalone PyInstaller binary for Hei-DataHub that can be distributed as a single executable file.

## Requirements

- **uv** - Modern Python package manager (replaces pip)
- **Python 3.13+** with development headers
- **PyInstaller** - Automatically installed by the script

## Quick Start

```bash
# Build the binary
./scripts/build_desktop_binary.sh

# Test it
./dist/linux/hei-datahub --version
./dist/linux/hei-datahub
```

## What's Included

The binary packages all necessary files:

### Code & Dependencies
- All Python source code from `src/mini_datahub` and `src/hei_datahub`
- All Python dependencies (textual, pydantic, etc.)
- Python runtime (embedded in the binary)

### Data Files
- **SQL schemas**: `src/mini_datahub/infra/sql/*.sql`
- **CSS styles**: `src/mini_datahub/ui/styles/*.tcss`
- **Assets**: `src/mini_datahub/ui/assets/` (ASCII art, etc.)
- **Desktop assets**: `src/hei_datahub/assets/` (icons, desktop entry template)

## Script Changes from Default

### Original Issues
1. ❌ Used `pip install` - fails on externally-managed Python environments
2. ❌ Missing CSS/TCSS files - caused `StylesheetError` at runtime
3. ❌ Missing asset files - no ASCII art, broken UI

### Fixed with UV
```bash
# Old (broken on Arch/managed Python)
pip install pyinstaller

# New (works everywhere)
uv pip install pyinstaller
```

### Added Data Files
```bash
pyinstaller \
    --add-data "src/mini_datahub/infra/sql:mini_datahub/infra/sql" \
    --add-data "src/mini_datahub/ui/styles:mini_datahub/ui/styles" \        # CSS files
    --add-data "src/mini_datahub/ui/assets:mini_datahub/ui/assets" \        # ASCII art
    --add-data "src/hei_datahub/assets:hei_datahub/assets" \                # Desktop assets
    # ... other options
```

## Output

```
dist/
└── linux/
    └── hei-datahub      # 27MB standalone binary
```

## Binary Characteristics

### ✅ Advantages
- **Single file**: Easy to distribute
- **No Python required**: Embeds Python runtime
- **Fast startup**: Cached Python bytecode
- **Portable**: Works on any compatible Linux system

### ⚠️ Limitations
- **Linux-only**: Built for current platform (glibc version)
- **Large size**: ~27MB (includes Python runtime + dependencies)
- **Not cross-platform**: Need to build on each target OS
- **Requires compatible glibc**: Built binaries depend on system libraries

## Platform-Specific Builds

### For Windows
```bash
# Run on Windows with UV installed
.\scripts\build_desktop_binary.sh  # PowerShell/cmd

# Output: dist/windows/hei-datahub.exe
```

### For macOS
```bash
# Run on macOS with UV installed
./scripts/build_desktop_binary.sh

# Output: dist/macos/hei-datahub
```

## Distribution

### Option 1: Direct Binary
```bash
# Copy to user
cp dist/linux/hei-datahub /usr/local/bin/

# Or user directory
cp dist/linux/hei-datahub ~/.local/bin/
```

### Option 2: With Desktop Integration
```bash
# Build binary
./scripts/build_desktop_binary.sh

# Install desktop entry pointing to binary
# (Requires manual setup - see create_desktop_entry.sh)
```

### Option 3: Package in .deb/.rpm
```bash
# Create Debian package
fpm -s dir -t deb \
    --name hei-datahub \
    --version 0.58.2 \
    --architecture amd64 \
    dist/linux/hei-datahub=/usr/bin/hei-datahub

# Create RPM package
fpm -s dir -t rpm \
    --name hei-datahub \
    --version 0.58.2 \
    --architecture x86_64 \
    dist/linux/hei-datahub=/usr/bin/hei-datahub
```

## Troubleshooting

### "externally-managed-environment" Error
**Problem**: System Python is protected by PEP 668

**Solution**: Script now uses `uv` instead of `pip`

### "StylesheetError: unable to read CSS file"
**Problem**: CSS files not included in binary

**Solution**: Added `--add-data` for `ui/styles/*.tcss`

### "ASCII art not found"
**Problem**: Asset files not included in binary

**Solution**: Added `--add-data` for `ui/assets/ascii/*.txt`

### Binary Won't Run on Other Linux
**Problem**: glibc version mismatch

**Solution**: Build on oldest supported Linux version (e.g., Ubuntu 20.04 for broader compatibility)

### Large Binary Size
**Problem**: 27MB is too large

**Solutions**:
- Use `--exclude-module` to remove unused dependencies
- Use `pyinstaller --onedir` instead of `--onefile` (smaller but multiple files)
- Use compression: `upx dist/linux/hei-datahub` (requires upx)

## Development Workflow

### 1. Make Changes
```bash
# Edit code
vim src/mini_datahub/...

# Test normally
hei-datahub
```

### 2. Rebuild Binary
```bash
# Quick rebuild (uses cache)
./scripts/build_desktop_binary.sh

# Clean rebuild
rm -rf build dist
./scripts/build_desktop_binary.sh
```

### 3. Test Binary
```bash
# Version check
./dist/linux/hei-datahub --version

# Full test
./dist/linux/hei-datahub
```

### 4. Distribute
```bash
# Copy to test location
scp dist/linux/hei-datahub user@server:/usr/local/bin/

# Or create package
./scripts/create_package.sh  # (if exists)
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Build Binaries
on: [push, release]

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v1
      - run: ./scripts/build_desktop_binary.sh
      - uses: actions/upload-artifact@v3
        with:
          name: hei-datahub-linux
          path: dist/linux/hei-datahub

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v1
      - run: .\scripts\build_desktop_binary.sh
      - uses: actions/upload-artifact@v3
        with:
          name: hei-datahub-windows
          path: dist/windows/hei-datahub.exe
```

## Next Steps

1. **Test binary on clean system** without Python/UV installed
2. **Create installer packages** (.deb, .rpm, .msi)
3. **Set up automated builds** for all platforms
4. **Add code signing** for Windows/macOS
5. **Create update mechanism** for installed binaries

## Related Files

- `scripts/build_desktop_binary.sh` - Main build script
- `scripts/create_desktop_entry.sh` - Desktop integration
- `src/hei_datahub/desktop_install.py` - Runtime desktop assets installer
- `hei-datahub.spec` - PyInstaller configuration (auto-generated)
