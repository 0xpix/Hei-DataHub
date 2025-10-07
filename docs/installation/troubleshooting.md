# Troubleshooting Guide

> 🧱 Compatible with Hei-DataHub **v0.58.x-beta**

Having issues with Hei-DataHub installation or usage? This guide covers common problems and their solutions.

---

## 📑 Table of Contents

- [Installation Issues](#installation-issues)
- [Authentication Problems](#authentication-problems)
- [Runtime Errors](#runtime-errors)
- [Data & Configuration Issues](#data--configuration-issues)
- [Desktop Launcher Issues](#desktop-launcher-issues)
- [Performance Problems](#performance-problems)
- [Getting Help](#getting-help)

---

## Installation Issues

### "uv: command not found"

**Symptoms:**
```bash
bash: uv: command not found
```

**Causes:**
- UV not installed
- UV not in PATH

**Solutions:**

1. **Install UV:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Add to PATH:**
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Make permanent:**
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Verify:**
   ```bash
   uv --version
   ```

---

### "hei-datahub: command not found"

**Symptoms:**
```bash
bash: hei-datahub: command not found
```

**Causes:**
- Not installed via `uv tool install`
- Tool installation directory not in PATH

**Solutions:**

1. **Verify installation:**
   ```bash
   uv tool list
   ```

2. **Install if missing:**
   ```bash
   uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
   ```

3. **Add tools to PATH:**
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

4. **Check UV tool bin directory:**
   ```bash
   ls -la ~/.local/bin/ | grep hei-datahub
   ```

---

### Package Installation Fails

**Symptoms:**
```
ERROR: Failed to build hei-datahub
```

**Causes:**
- Missing build dependencies
- Python version mismatch
- Network issues

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.10+
   ```

2. **Install build dependencies (Debian/Ubuntu):**
   ```bash
   sudo apt install python3-dev build-essential
   ```

3. **Install build dependencies (Fedora/RHEL):**
   ```bash
   sudo dnf install python3-devel gcc
   ```

4. **Try verbose mode:**
   ```bash
   uv -v tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
   ```

---

## Authentication Problems

### SSH: "Permission denied (publickey)"

**Symptoms:**
```
git@github.com: Permission denied (publickey).
```

**Causes:**
- SSH key not added to GitHub
- SSH agent not running
- Wrong key being used

**Solutions:**

1. **Check SSH agent:**
   ```bash
   ssh-add -l
   ```

2. **Add your key:**
   ```bash
   ssh-add ~/.ssh/id_ed25519
   ```

3. **Test GitHub connection:**
   ```bash
   ssh -T git@github.com
   ```

4. **Verify key on GitHub:**
   - Go to [GitHub SSH Keys](https://github.com/settings/keys)
   - Make sure your public key is listed

5. **Debug SSH:**
   ```bash
   ssh -vT git@github.com
   ```

**See also:** [Private Repository Access](private-repo-access.md#method-1-ssh-authentication-recommended)

---

### HTTPS: "Authentication failed"

**Symptoms:**
```
fatal: Authentication failed
```

**Causes:**
- Token not set
- Token expired
- Token lacks permissions

**Solutions:**

1. **Verify token is set:**
   ```bash
   echo $GH_PAT
   ```

2. **Set token:**
   ```bash
   export GH_PAT=ghp_xxxxxxxxxxxxx
   ```

3. **Check token permissions on GitHub:**
   - Go to [GitHub Tokens](https://github.com/settings/tokens)
   - Verify `contents:read` permission
   - Check expiration date

4. **Generate new token if needed:**
   - See [Private Repository Access](private-repo-access.md#method-2-https--personal-access-token-pat)

---

### "Repository not found" / 404 Error

**Symptoms:**
```
ERROR: Repository not found: 0xpix/Hei-DataHub
```

**Causes:**
- No access to repository
- Wrong repository name
- Authentication issue

**Solutions:**

1. **Verify repository URL:**
   ```
   https://github.com/0xpix/Hei-DataHub
   ```

2. **Check your access:**
   - Ask repository owner to grant access
   - Verify you're logged into the correct GitHub account

3. **Test access:**
   ```bash
   # SSH
   ssh -T git@github.com
   
   # HTTPS
   curl -H "Authorization: token $GH_PAT" https://api.github.com/repos/0xpix/Hei-DataHub
   ```

---

## Runtime Errors

### "No module named 'mini_datahub'"

**Symptoms:**
```python
ModuleNotFoundError: No module named 'mini_datahub'
```

**Causes:**
- Installation incomplete
- Wrong Python environment

**Solutions:**

1. **Verify installation:**
   ```bash
   uv tool list
   python -c "import mini_datahub; print(mini_datahub.__version__)"
   ```

2. **Reinstall:**
   ```bash
   uv tool uninstall hei-datahub
   uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
   ```

---

### TUI Rendering Issues

**Symptoms:**
- Garbled text
- Missing colors
- Layout problems

**Causes:**
- Terminal doesn't support colors/Unicode
- TERM variable not set correctly

**Solutions:**

1. **Check terminal support:**
   ```bash
   echo $TERM
   ```

2. **Use a modern terminal:**
   - Linux: GNOME Terminal, Konsole, Alacritty
   - macOS: iTerm2, Terminal.app
   - Windows: Windows Terminal

3. **Set TERM variable:**
   ```bash
   export TERM=xterm-256color
   ```

4. **Test colors:**
   ```bash
   python -c "from textual.color import Color; print(Color.parse('red'))"
   ```

---

## Data & Configuration Issues

### "Data files not found" / Missing Assets

**Symptoms:**
```
FileNotFoundError: data/datasets/metadata.yaml not found
```

**Causes:**
- Package data not included in installation (pre-v0.58.0)
- Wrong working directory

**Solutions:**

1. **Check version:**
   ```bash
   hei-datahub --version
   ```
   
   Should be `0.58.0-beta` or later.

2. **Upgrade to v0.58.0-beta:**
   ```bash
   uv tool upgrade hei-datahub
   ```

3. **Verify package contents:**
   ```bash
   python -c "import mini_datahub; import os; print(os.path.dirname(mini_datahub.__file__))"
   ls -la $(python -c "import mini_datahub; import os; print(os.path.dirname(mini_datahub.__file__))")
   ```

4. **Check for data directory:**
   ```bash
   python -c "import mini_datahub.infra.paths as p; print(p.get_data_dir())"
   ```

---

### Database Errors

**Symptoms:**
```
sqlite3.OperationalError: no such table: datasets
```

**Causes:**
- Database not initialized
- Corrupted database

**Solutions:**

1. **Reindex:**
   ```bash
   hei-datahub reindex
   ```

2. **Delete and rebuild:**
   ```bash
   rm ~/.local/share/hei-datahub/db.sqlite
   hei-datahub reindex
   ```

3. **Check database location:**
   ```bash
   python -c "import mini_datahub.infra.paths as p; print(p.get_db_path())"
   ```

---

### Configuration Not Persisting

**Symptoms:**
- Settings reset after restart
- Config changes not saved

**Causes:**
- Permission issues
- Wrong config directory

**Solutions:**

1. **Check config location:**
   ```bash
   python -c "import mini_datahub.infra.paths as p; print(p.get_config_path())"
   ```

2. **Check permissions:**
   ```bash
   ls -la ~/.config/hei-datahub/
   ```

3. **Manually create directory:**
   ```bash
   mkdir -p ~/.config/hei-datahub
   chmod 755 ~/.config/hei-datahub
   ```

---

## Desktop Launcher Issues

### Launcher Doesn't Appear in Menu

**Symptoms:**
- Can't find Hei-DataHub in application launcher

**Causes:**
- Desktop database not updated
- `.desktop` file has errors

**Solutions:**

1. **Update desktop database:**
   ```bash
   update-desktop-database ~/.local/share/applications
   ```

2. **Check .desktop file:**
   ```bash
   desktop-file-validate ~/.local/share/applications/hei-datahub.desktop
   ```

3. **Restart desktop environment:**
   - Log out and log back in

4. **Check file permissions:**
   ```bash
   chmod 644 ~/.local/share/applications/hei-datahub.desktop
   ```

---

### Launcher Opens Then Closes Immediately

**Symptoms:**
- Click launcher → terminal opens → immediately closes

**Causes:**
- Error on startup
- `hei-datahub` not in PATH for desktop session

**Solutions:**

1. **Edit desktop entry to use full path:**
   ```bash
   nano ~/.local/share/applications/hei-datahub.desktop
   ```
   
   Change:
   ```ini
   Exec=hei-datahub
   ```
   
   To:
   ```ini
   Exec=/home/username/.local/bin/hei-datahub
   ```

2. **Test from terminal first:**
   ```bash
   hei-datahub
   ```

3. **Check logs:**
   ```bash
   hei-datahub 2>&1 | tee ~/hei-datahub.log
   ```

---

## Performance Problems

### Slow Search

**Symptoms:**
- Search takes several seconds
- UI freezes during search

**Causes:**
- Large number of datasets
- Database not optimized

**Solutions:**

1. **Reindex with optimization:**
   ```bash
   hei-datahub reindex
   ```

2. **Check database size:**
   ```bash
   du -h ~/.local/share/hei-datahub/db.sqlite
   ```

3. **Vacuum database:**
   ```bash
   sqlite3 ~/.local/share/hei-datahub/db.sqlite "VACUUM;"
   ```

---

### High Memory Usage

**Symptoms:**
- Application uses excessive RAM

**Causes:**
- Large datasets loaded in memory
- Memory leak (rare)

**Solutions:**

1. **Check version:**
   ```bash
   hei-datahub --version
   ```

2. **Restart application periodically**

3. **Monitor usage:**
   ```bash
   htop  # or ps aux | grep hei-datahub
   ```

---

## Getting Help

### Before Asking for Help

Collect this information:

1. **Version info:**
   ```bash
   hei-datahub --version-info
   ```

2. **Installation method:**
   - UV (SSH/token)
   - pip
   - Binary

3. **Operating system:**
   ```bash
   uname -a
   ```

4. **Python version:**
   ```bash
   python --version
   ```

5. **Error messages:**
   - Full error output
   - Relevant log files

### Where to Get Help

- **Documentation:** [docs.hei-datahub.dev](https://0xpix.github.io/Hei-DataHub/)
- **GitHub Issues:** [github.com/0xpix/Hei-DataHub/issues](https://github.com/0xpix/Hei-DataHub/issues)
- **Team Chat:** Ask in your organization's communication channel

### Creating a Good Bug Report

Include:

1. **Clear title:** "Installation fails on Ubuntu 22.04 with SSH"
2. **Steps to reproduce:** Numbered list
3. **Expected behavior:** What should happen
4. **Actual behavior:** What actually happens
5. **System info:** OS, Python version, etc.
6. **Logs:** Full error messages

**Template:**

```markdown
**Environment:**
- OS: Ubuntu 22.04
- Python: 3.10.12
- Hei-DataHub: 0.58.0-beta
- Installation method: UV (SSH)

**Steps to Reproduce:**
1. Run `uv tool install --from "git+ssh://..."`
2. Execute `hei-datahub`
3. Error appears

**Expected:** Application starts
**Actual:** Error message: "..."

**Error Output:**
```
[paste full error here]
```
```

---

## 🔧 Quick Diagnostic Commands

Run these to gather diagnostic info:

```bash
# System info
uname -a
python --version
uv --version

# Hei-DataHub info
hei-datahub --version-info
uv tool list | grep hei-datahub

# Paths
python -c "import mini_datahub; print(mini_datahub.__file__)"
python -c "import mini_datahub.infra.paths as p; print('DB:', p.get_db_path()); print('Config:', p.get_config_path())"

# Authentication
ssh -T git@github.com
echo $GH_PAT | cut -c1-10  # First 10 chars only

# Package contents
python -c "import pkg_resources; print(pkg_resources.get_distribution('hei-datahub').location)"
```

---

**Still stuck? Don't hesitate to ask for help!** 🤝
