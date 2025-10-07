# Windows Installation Notes

> 🧱 Compatible with Hei-DataHub **v0.58.x-beta**

This guide covers Windows-specific installation steps and common issues for Hei-DataHub.

---

## 📦 Installing UV on Windows

### Using PowerShell (Recommended)

Open **PowerShell** (as Administrator if needed):

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

UV will be installed to: `%USERPROFILE%\.local\bin\uv.exe`

### Adding UV to PATH

If UV isn't automatically added to your PATH:

1. Open **Settings** → **System** → **About** → **Advanced system settings**
2. Click **Environment Variables**
3. Under **User variables**, find **Path**
4. Click **Edit** → **New**
5. Add: `%USERPROFILE%\.local\bin`
6. Click **OK** on all dialogs
7. **Restart PowerShell** for changes to take effect

### Verify Installation

```powershell
uv --version
```

You should see: `uv 0.x.x`

---

## 🚀 Installing Hei-DataHub on Windows

### Method 1: Using HTTPS + Token (Recommended for Windows)

#### Step 1: Get a GitHub Personal Access Token

See [Private Repository Access](private-repo-access.md) for detailed instructions.

#### Step 2: Set Token in PowerShell

```powershell
$env:GH_PAT = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

To make it permanent, add to PowerShell profile:

```powershell
# Open profile
notepad $PROFILE

# Add this line
$env:GH_PAT = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### Step 3: Install Hei-DataHub

**Ephemeral run:**
```powershell
uvx "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main"
```

**Persistent install:**
```powershell
uv tool install "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main"
```

#### Step 4: Run Hei-DataHub

```powershell
hei-datahub
```

---

### Method 2: Using SSH

SSH on Windows requires additional setup but is more convenient long-term.

#### Prerequisites

Install Git for Windows (includes SSH): [https://git-scm.com/download/win](https://git-scm.com/download/win)

#### Step 1: Generate SSH Key

Open **Git Bash** (installed with Git for Windows):

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter to accept defaults.

#### Step 2: Start SSH Agent

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

#### Step 3: Add SSH Key to GitHub

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the output and add it to GitHub: [Settings → SSH Keys](https://github.com/settings/keys)

#### Step 4: Test Connection

```bash
ssh -T git@github.com
```

You should see: `Hi username! You've successfully authenticated...`

#### Step 5: Install Hei-DataHub

Back in **PowerShell**:

```powershell
uv tool install "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main"
```

---

## 🎨 Windows Terminal Tips

### Better Terminal Experience

1. Install **Windows Terminal** from Microsoft Store (recommended)
2. Use **PowerShell 7** instead of Windows PowerShell 5.1:
   ```powershell
   winget install Microsoft.PowerShell
   ```

### Persistent Environment Variables

To make `GH_PAT` permanent:

**Method A: PowerShell Profile**
```powershell
notepad $PROFILE
# Add: $env:GH_PAT = "ghp_xxxxx"
```

**Method B: System Environment Variables**
1. Open **Settings** → **System** → **About** → **Advanced system settings**
2. Click **Environment Variables**
3. Under **User variables**, click **New**
4. Variable name: `GH_PAT`
5. Variable value: `ghp_xxxxxxxxxxxxx`
6. Click **OK**
7. Restart PowerShell

---

## 🔍 Troubleshooting

### "uv: command not found"

**Cause:** UV not in PATH.

**Solution:**
1. Restart PowerShell
2. Verify UV location:
   ```powershell
   Get-ChildItem "$env:USERPROFILE\.local\bin\uv.exe"
   ```
3. Add to PATH manually (see above)

### "The system cannot execute the specified program"

**Cause:** Python not installed or not in PATH.

**Solution:**
1. Install Python from [python.org](https://www.python.org/downloads/)
2. During installation, check **"Add Python to PATH"**
3. Restart PowerShell

### "git+https://: No such file or directory"

**Cause:** Token not interpolated correctly.

**Solution:**
Use double quotes instead of single quotes:
```powershell
uvx "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main"
```

### "Authentication failed"

**Cause:** Token invalid or not set.

**Solution:**
1. Verify token:
   ```powershell
   echo $env:GH_PAT
   ```
2. Regenerate token on GitHub if needed
3. Make sure token has `contents:read` permission

### Permission Errors During Installation

**Cause:** Need administrator privileges.

**Solution:**
Right-click PowerShell → **Run as Administrator**

### Terminal Doesn't Support Colors/TUI

**Cause:** Old Windows Terminal or cmd.exe.

**Solution:**
Use **Windows Terminal** from Microsoft Store.

---

## 🖥️ Desktop Shortcuts (Windows)

Since Hei-DataHub is a terminal application, you can create a desktop shortcut:

### Method 1: PowerShell Shortcut

1. Right-click Desktop → **New** → **Shortcut**
2. Location:
   ```
   powershell.exe -NoExit -Command "hei-datahub"
   ```
3. Name: `Hei-DataHub`
4. Click **Finish**

### Method 2: Windows Terminal Shortcut

If you have Windows Terminal:

1. Right-click Desktop → **New** → **Shortcut**
2. Location:
   ```
   wt.exe -p "PowerShell" cmd /k hei-datahub
   ```
3. Name: `Hei-DataHub`
4. Click **Finish**

---

## 📋 Windows Command Reference

| Task | Command |
|------|---------|
| Install UV | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Set token | `$env:GH_PAT = "ghp_xxxxx"` |
| Install (ephemeral) | `uvx "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main"` |
| Install (persistent) | `uv tool install "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main" hei-datahub` |
| Run | `hei-datahub` |
| Update | `uv tool upgrade hei-datahub` |
| Uninstall | `uv tool uninstall hei-datahub` |

---

## 🎯 One-Liner Setup (PowerShell)

```powershell
# Set your token first
$env:GH_PAT = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Then run this
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"; `
  & "$env:USERPROFILE\.local\bin\uv.exe" tool install --from "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main" hei-datahub; `
  hei-datahub --version
```

---

## 💡 Tips for Windows Users

1. **Use Windows Terminal** for the best experience
2. **Enable UTF-8** in PowerShell profile:
   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   ```
3. **Pin to Taskbar:** Drag your desktop shortcut to the taskbar
4. **Set default terminal:** Windows Terminal → Settings → Startup → Default profile

---

## 📚 Additional Resources

- [UV Installation](https://github.com/astral-sh/uv)
- [Git for Windows](https://git-scm.com/download/win)
- [Windows Terminal](https://aka.ms/terminal)
- [PowerShell 7](https://aka.ms/powershell)

---

**Windows + Hei-DataHub = 💙** Happy organizing!
