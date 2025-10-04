
This step-by-step tutorial will guide you through installing Hei-DataHub and verifying that everything works correctly.

---

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] **Python 3.9+** installed (`python --version`)
- [ ] **Git** installed (`git --version`)
- [ ] **Terminal** access
- [ ] **Internet connection** (for cloning repo)

---

## Step 1: Clone the Repository

Open your terminal and run:

```bash
# Clone from GitHub
git clone https://github.com/0xpix/Hei-DataHub.git

# Navigate into the directory
cd Hei-DataHub
```

**Verify:**

```bash
ls -la
```

**Expected output:**

```
drwxr-xr-x  data/
drwxr-xr-x  src/
drwxr-xr-x  scripts/
-rw-r--r--  pyproject.toml
-rw-r--r--  README.md
...
```

---

## Step 2: Install uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer. It's optional but highly recommended.

**Install uv:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify:**

```bash
uv --version
```

**Expected output:**

```
uv 0.x.x
```

**Skip this step if you prefer using `pip`.**

---

## Step 3: Create Virtual Environment

### Option A: Using uv (Recommended)

```bash
uv sync --dev
```

**What this does:**

- Creates `.venv/` directory
- Installs all dependencies from `pyproject.toml`
- Installs development dependencies (`pytest`, `ruff`, etc.)

**Expected output:**

```
Resolved X packages in Xms
Installed X packages in Xms
```

---

### Option B: Using pip

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install package
pip install -e .
```

**Expected output:**

```
Successfully installed mini-datahub-0.55.0-beta ...
```

---

## Step 4: Activate Virtual Environment

If you used **uv**, activate the environment:

```bash
source .venv/bin/activate
```

**Verify activation:**

Your prompt should change to show `(.venv)`:

```bash
(.venv) user@host:~/Hei-DataHub$
```

**Check Python location:**

```bash
which python
```

**Expected:** `/path/to/Hei-DataHub/.venv/bin/python`

---

## Step 5: Verify Installation

Run the verification script:

```bash
./scripts/verify_installation.sh
```

**What it checks:**

1. ✅ Python version (>= 3.9)
2. ✅ Virtual environment active
3. ✅ Package installed (`hei-datahub` command available)
4. ✅ Database initialization
5. ✅ Example datasets indexed

**Expected output:**

```
✓ Python version: 3.11.x
✓ Virtual environment: active
✓ Package installed: hei-datahub 0.55.0-beta
✓ Database: initialized
✓ Datasets indexed: 12 total
All checks passed!
```

---

## Step 6: Launch Hei-DataHub

Start the TUI:

```bash
hei-datahub
```

**Expected:** TUI opens with Home screen.

```
┌────────────────────────────────────────┐
│  HEI DATAHUB                           │
├────────────────────────────────────────┤
│  🔍 Search Datasets | Mode: Normal     │
│  ○ GitHub Not Connected                │
├────────────────────────────────────────┤
│  Type / to search...                   │
│  All Datasets (X total)                │
│  ┌──────────────────────────────────┐  │
│  │ ID   │ Name   │ Description      │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

**Exit:** Press ++q++ to quit.

---

## Step 7: Test Basic Functionality

### Search Test

1. Press ++slash++ to focus search
2. Type "test"
3. Press ++enter++ to move to results

**Expected:** Results table shows datasets matching "test".

---

### Details Test

1. Navigate to any dataset with ++j++ / ++k++
2. Press ++enter++ to open details

**Expected:** Details screen shows full metadata.

3. Press ++escape++ to go back

---

### Add Dataset Test

1. Press ++a++ to open Add Dataset form
2. Fill in required fields:
    - **Dataset Name:** "Test Dataset"
    - **Description:** "This is a test"
    - **Source:** "https://example.com"
    - **Storage Location:** "local"
3. Press ++ctrl+s++ to save

**Expected:**

- Form closes
- New dataset appears in search results

---

## Troubleshooting

### Command Not Found: `hei-datahub`

**Cause:** Virtual environment not activated or package not installed.

**Fix:**

```bash
# Activate venv
source .venv/bin/activate

# Reinstall package
pip install -e .
```

---

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'textual'`

**Fix:**

```bash
# Reinstall dependencies
pip install -e .
```

---

### Database Errors

**Error:** `sqlite3.OperationalError: unable to open database`

**Fix:**

```bash
# Remove corrupted database
rm db.sqlite

# Relaunch (will recreate database)
hei-datahub
```

---

### Permission Denied

**Error:** `Permission denied: './scripts/verify_installation.sh'`

**Fix:**

```bash
# Make script executable
chmod +x scripts/*.sh

# Run again
./scripts/verify_installation.sh
```

---

## Uninstallation

To remove Hei-DataHub:

```bash
# Deactivate virtual environment
deactivate

# Remove directory
cd ..
rm -rf Hei-DataHub
```

---

## Next Steps

Now that Hei-DataHub is installed:

1. **[Tutorial: Your First Dataset](02-first-dataset.md)** — Add a real dataset
2. **[Navigation Guide](../02-navigation.md)** — Learn keyboard shortcuts
3. **[Configuration](../12-config.md)** — Set up GitHub integration (optional)

---

## Getting Help

- **FAQ:** [Common installation issues](../90-faq.md#installation-issues)
- **Issues:** [Report bugs on GitHub](https://github.com/0xpix/Hei-DataHub/issues)
