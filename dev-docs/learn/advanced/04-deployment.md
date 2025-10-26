# Advanced: Deployment and Packaging

**Learning Goal**: Package and deploy Hei-DataHub for different platforms.

By the end of this page, you'll:
- Package as Python wheel
- Create standalone binaries
- Build Docker images
- Create platform installers
- Set up CI/CD pipelines
- Publish releases

---

## Python Packaging

### 1. Project Structure

```
hei-datahub/
├── pyproject.toml         # Package metadata
├── MANIFEST.in            # Include non-Python files
├── README.md              # Project description
├── LICENSE                # License file
├── src/
│   └── mini_datahub/      # Source code
│       ├── __init__.py
│       ├── __main__.py    # Entry point
│       └── ...
└── tests/                 # Tests
```

---

### 2. pyproject.toml

**File:** `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "hei-datahub"
version = "0.60.0"
description = "A TUI for managing and searching research datasets"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
requires-python = ">=3.10"
keywords = ["tui", "dataset", "search", "webdav"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering",
]

dependencies = [
    "textual>=0.85.0",
    "pydantic>=2.0.0",
    "PyYAML>=6.0",
    "keyring>=24.0.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.scripts]
hei-datahub = "mini_datahub.__main__:main"
hei = "mini_datahub.__main__:main"

[project.urls]
Homepage = "https://github.com/yourusername/hei-datahub"
Documentation = "https://hei-datahub.readthedocs.io"
Repository = "https://github.com/yourusername/hei-datahub"
"Bug Tracker" = "https://github.com/yourusername/hei-datahub/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
mini_datahub = ["*.tcss", "*.yaml"]
```

---

### 3. Build Package

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# This creates:
# dist/hei_datahub-0.60.0-py3-none-any.whl  (wheel)
# dist/hei-datahub-0.60.0.tar.gz             (source)
```

---

### 4. Test Package Locally

```bash
# Create virtual environment
python -m venv test-env
source test-env/bin/activate

# Install from wheel
pip install dist/hei_datahub-0.60.0-py3-none-any.whl

# Test CLI
hei-datahub --version

# Deactivate
deactivate
```

---

### 5. Publish to PyPI

```bash
# Test on PyPI Test (optional)
twine upload --repository testpypi dist/*

# Install from test PyPI
pip install --index-url https://test.pypi.org/simple/ hei-datahub

# Publish to PyPI
twine upload dist/*

# Now anyone can install:
pip install hei-datahub
```

---

## Standalone Binaries

### 1. Using PyInstaller

**Install:**

```bash
pip install pyinstaller
```

**Create spec file:**

**File:** `build.spec`

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/mini_datahub/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/mini_datahub/ui/styles', 'mini_datahub/ui/styles'),
        ('src/mini_datahub/config', 'mini_datahub/config'),
    ],
    hiddenimports=[
        'textual',
        'pydantic',
        'keyring.backends.SecretService',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='hei-datahub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

**Build:**

```bash
pyinstaller build.spec

# Binary created at:
# dist/hei-datahub
```

---

### 2. Build Script

**File:** `scripts/build_desktop_binary.sh`

```bash
#!/usr/bin/env bash
#
# Build standalone binary for current platform.
#

set -e

echo "🔨 Building Hei-DataHub binary..."

# Clean previous builds
rm -rf build/ dist/

# Build with PyInstaller
pyinstaller build.spec

# Test binary
echo "✅ Testing binary..."
./dist/hei-datahub --version

echo "✅ Binary created: dist/hei-datahub"
echo ""
echo "Install to system:"
echo "  sudo cp dist/hei-datahub /usr/local/bin/"
```

**Run:**

```bash
chmod +x scripts/build_desktop_binary.sh
./scripts/build_desktop_binary.sh
```

---

### 3. Multi-Platform Builds

**GitHub Actions workflow:**

**File:** `.github/workflows/build-binaries.yml`

```yaml
name: Build Binaries

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyinstaller
          pip install -r requirements.txt

      - name: Build binary
        run: pyinstaller build.spec

      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: hei-datahub-${{ matrix.os }}
          path: dist/hei-datahub*
```

---

## Docker Images

### 1. Dockerfile

**File:** `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir .

# Create data directory
RUN mkdir -p /data

# Set environment variables
ENV HEI_DATAHUB_DATA_DIR=/data
ENV PYTHONUNBUFFERED=1

# Entry point
ENTRYPOINT ["hei-datahub"]
CMD ["--help"]
```

**Build:**

```bash
docker build -t hei-datahub:latest .

# Run
docker run -it --rm \
  -v $(pwd)/data:/data \
  hei-datahub:latest
```

---

### 2. Docker Compose

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  hei-datahub:
    image: hei-datahub:latest
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./data:/data
      - ./config:/root/.config/hei-datahub
    environment:
      - HEI_DATAHUB_DATA_DIR=/data
    stdin_open: true
    tty: true
```

**Run:**

```bash
docker-compose up -d
docker-compose exec hei-datahub bash
```

---

### 3. Multi-Stage Build (Smaller Image)

```dockerfile
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --user .

# Runtime stage
FROM python:3.11-slim

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY src/ /app/src/

# Set PATH
ENV PATH=/root/.local/bin:$PATH
ENV HEI_DATAHUB_DATA_DIR=/data

WORKDIR /data

ENTRYPOINT ["hei-datahub"]
```

---

## Platform Installers

### 1. Debian Package (.deb)

**Install fpm:**

```bash
gem install fpm
```

**Create package:**

```bash
#!/usr/bin/env bash
# Build .deb package

fpm -s dir -t deb \
  --name hei-datahub \
  --version 0.60.0 \
  --architecture amd64 \
  --description "TUI for managing research datasets" \
  --url "https://github.com/yourusername/hei-datahub" \
  --maintainer "Your Name <your.email@example.com>" \
  --license MIT \
  --depends "python3 >= 3.10" \
  dist/hei-datahub=/usr/local/bin/hei-datahub

# Install:
# sudo dpkg -i hei-datahub_0.60.0_amd64.deb
```

---

### 2. RPM Package (.rpm)

```bash
fpm -s dir -t rpm \
  --name hei-datahub \
  --version 0.60.0 \
  --architecture x86_64 \
  --description "TUI for managing research datasets" \
  --url "https://github.com/yourusername/hei-datahub" \
  --maintainer "Your Name <your.email@example.com>" \
  --license MIT \
  --depends "python3 >= 3.10" \
  dist/hei-datahub=/usr/local/bin/hei-datahub

# Install:
# sudo rpm -i hei-datahub-0.60.0-1.x86_64.rpm
```

---

### 3. macOS Installer (.dmg)

**Using create-dmg:**

```bash
# Install create-dmg
brew install create-dmg

# Create .app bundle
mkdir -p Hei-DataHub.app/Contents/MacOS
cp dist/hei-datahub Hei-DataHub.app/Contents/MacOS/

# Create Info.plist
cat > Hei-DataHub.app/Contents/Info.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>hei-datahub</string>
  <key>CFBundleIdentifier</key>
  <string>io.github.yourusername.hei-datahub</string>
  <key>CFBundleName</key>
  <string>Hei-DataHub</string>
  <key>CFBundleVersion</key>
  <string>0.60.0</string>
</dict>
</plist>
EOF

# Create DMG
create-dmg \
  --volname "Hei-DataHub 0.60.0" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --app-drop-link 600 185 \
  Hei-DataHub-0.60.0.dmg \
  Hei-DataHub.app
```

---

## CI/CD Pipeline

### 1. GitHub Actions - Test

**File:** `.github/workflows/test.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .[dev]

      - name: Run tests
        run: |
          pytest tests/ --cov=mini_datahub --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

### 2. GitHub Actions - Release

**File:** `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  pypi:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*

  binaries:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyinstaller
          pip install -e .

      - name: Build binary
        run: pyinstaller build.spec

      - name: Upload to release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/hei-datahub*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

### 3. GitLab CI/CD

**File:** `.gitlab-ci.yml`

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -e .[dev]
    - pytest tests/ --cov=mini_datahub
  coverage: '/TOTAL.*\s+(\d+%)$/'

build-package:
  stage: build
  image: python:3.11
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/
  only:
    - tags

deploy-pypi:
  stage: deploy
  image: python:3.11
  script:
    - pip install twine
    - twine upload dist/*
  only:
    - tags
  variables:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: $PYPI_TOKEN
```

---

## Version Management

### 1. Semantic Versioning

```
MAJOR.MINOR.PATCH

Examples:
- 0.60.0 → 0.60.1  (bug fix)
- 0.60.1 → 0.61.0  (new feature)
- 0.61.0 → 1.0.0   (breaking change)
```

---

### 2. Version File

**File:** `src/mini_datahub/version.py`

```python
"""
Version information.
"""
__version__ = "0.60.0"
__app_name__ = "Hei-DataHub"
```

**Update automatically:**

```bash
#!/usr/bin/env bash
# scripts/bump_version.sh

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

# Update version.py
echo "__version__ = \"$VERSION\"" > src/mini_datahub/version.py
echo "__app_name__ = \"Hei-DataHub\"" >> src/mini_datahub/version.py

# Update pyproject.toml
sed -i "s/version = .*/version = \"$VERSION\"/" pyproject.toml

# Commit
git add src/mini_datahub/version.py pyproject.toml
git commit -m "Bump version to $VERSION"
git tag "v$VERSION"

echo "✅ Version bumped to $VERSION"
echo "Push with: git push && git push --tags"
```

---

## Release Checklist

### Pre-Release

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Git tag created

---

### Build

- [ ] Python wheel built
- [ ] Standalone binaries created (Linux/Mac/Windows)
- [ ] Docker image built
- [ ] Platform installers created (optional)

---

### Publish

- [ ] Package uploaded to PyPI
- [ ] GitHub release created with binaries
- [ ] Docker image pushed to registry
- [ ] Documentation deployed
- [ ] Announcement posted

---

### Post-Release

- [ ] Monitor issue tracker
- [ ] Update version to next dev version
- [ ] Plan next release

---

## Distribution Channels

### PyPI

```bash
pip install hei-datahub
```

**Advantages:** Easy to install, version management
**Disadvantages:** Requires Python, dependencies

---

### Standalone Binary

```bash
curl -L https://github.com/user/hei-datahub/releases/latest/download/hei-datahub -o hei-datahub
chmod +x hei-datahub
sudo mv hei-datahub /usr/local/bin/
```

**Advantages:** No Python required, single file
**Disadvantages:** Large file size, platform-specific

---

### Docker Hub

```bash
docker pull yourusername/hei-datahub:latest
docker run -it --rm -v $(pwd)/data:/data yourusername/hei-datahub
```

**Advantages:** Isolated environment, reproducible
**Disadvantages:** Requires Docker

---

### Package Managers

```bash
# Homebrew (macOS)
brew install hei-datahub

# APT (Debian/Ubuntu)
sudo apt install hei-datahub

# DNF (Fedora)
sudo dnf install hei-datahub
```

**Advantages:** Native package management
**Disadvantages:** Requires package repository setup

---

## What You've Learned

✅ **Python packaging** — pyproject.toml, build, PyPI
✅ **Standalone binaries** — PyInstaller, multi-platform builds
✅ **Docker images** — Dockerfile, multi-stage builds
✅ **Platform installers** — .deb, .rpm, .dmg
✅ **CI/CD pipelines** — GitHub Actions, GitLab CI
✅ **Version management** — Semantic versioning, automation
✅ **Release process** — Checklists, distribution channels

---

## Congratulations! 🎉

You've completed the **Hei-DataHub Learning Guide**!

You now know how to:
- Build TUI applications with Textual
- Implement search with SQLite FTS5
- Follow Clean Architecture patterns
- Extend and customize features
- Optimize performance
- Debug effectively
- Package and deploy

---

## What's Next?

**Contribute to Hei-DataHub:**
- Pick an issue from GitHub
- Implement a feature you want
- Submit a pull request

**Build Your Own Project:**
- Apply these patterns to your own TUI app
- Share your learnings with the community

**Keep Learning:**
- Explore Textual's advanced features
- Dive deeper into SQLite optimization
- Learn more about WebDAV protocol

---

## Further Reading

- [Python Packaging Guide](https://packaging.python.org/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
