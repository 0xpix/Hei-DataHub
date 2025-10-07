# Private Repository Access

> 🧱 Compatible with Hei-DataHub **v0.58.x-beta**

Since Hei-DataHub is hosted in a **private GitHub repository**, you need to authenticate before UV can install it. This guide covers both SSH and HTTPS token-based authentication.

---

## 🔐 Authentication Methods

| Method | Pros | Cons | Recommended For |
|--------|------|------|-----------------|
| **SSH** | Secure, no token management, works for all repos | Requires SSH key setup | Internal team use, developers |
| **HTTPS + Token** | Works anywhere, good for CI/CD | Need to manage tokens | Automation, restricted environments |

---

## Method 1: SSH Authentication (Recommended)

SSH is the most secure and convenient method for daily use.

### ✅ Prerequisites

1. You have a GitHub account with access to the repository
2. You're comfortable with basic command-line operations

### 📝 Step-by-Step Setup

#### 1. Check for Existing SSH Keys

```bash
ls -la ~/.ssh
```

Look for files like:
- `id_rsa` and `id_rsa.pub`
- `id_ed25519` and `id_ed25519.pub`

If you see these, you already have SSH keys. Skip to step 3.

#### 2. Generate a New SSH Key

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter to accept the default location (`~/.ssh/id_ed25519`).

**Optional:** Set a passphrase for extra security (or press Enter for no passphrase).

#### 3. Add SSH Key to SSH Agent

Start the SSH agent:

```bash
eval "$(ssh-agent -s)"
```

Add your key:

```bash
ssh-add ~/.ssh/id_ed25519
```

#### 4. Add SSH Key to GitHub

Copy your public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Or use this one-liner to copy to clipboard (Linux):

```bash
cat ~/.ssh/id_ed25519.pub | xclip -selection clipboard
```

**Then:**

1. Go to GitHub: [Settings → SSH and GPG keys](https://github.com/settings/keys)
2. Click **"New SSH key"**
3. Paste your public key
4. Give it a descriptive title (e.g., "Work Laptop")
5. Click **"Add SSH key"**

#### 5. Test the Connection

```bash
ssh -T git@github.com
```

You should see:

```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

### ✅ Install Hei-DataHub via SSH

Now you can install using SSH URLs:

```bash
# Ephemeral run
uvx "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub"

# Persistent install
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
```

---

## Method 2: HTTPS + Personal Access Token (PAT)

Use a GitHub Personal Access Token for authentication over HTTPS.

### 📝 Step-by-Step Setup

#### 1. Generate a GitHub Personal Access Token

1. Go to [GitHub → Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click **"Tokens (classic)"** or **"Fine-grained tokens"** (recommended)

**For Fine-Grained Tokens:**

1. Click **"Generate new token"**
2. Give it a name: `Hei-DataHub Read Access`
3. Set expiration (e.g., 90 days)
4. **Repository access:** Select "Only select repositories" → Choose `Hei-DataHub`
5. **Permissions:**
   - Contents: **Read-only** ✅
6. Click **"Generate token"**
7. **Copy the token immediately** (you won't see it again!)

**For Classic Tokens:**

1. Click **"Generate new token (classic)"**
2. Give it a note: `Hei-DataHub Read`
3. Select scopes:
   - `repo` (or just `repo:status` + `public_repo` if available)
4. Click **"Generate token"**
5. **Copy the token immediately**

#### 2. Store the Token Securely

**Linux/macOS:**

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export GH_PAT=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Reload your shell:

```bash
source ~/.bashrc  # or ~/.zshrc
```

**Windows (PowerShell):**

```powershell
$env:GH_PAT = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

To make it permanent, add to PowerShell profile:

```powershell
notepad $PROFILE
```

Add the line:

```powershell
$env:GH_PAT = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### 3. Verify Token is Set

```bash
echo $GH_PAT  # Linux/macOS
echo $env:GH_PAT  # Windows PowerShell
```

You should see your token.

### ✅ Install Hei-DataHub with Token

```bash
# Ephemeral run
uvx "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main#egg=hei-datahub"

# Persistent install
uv tool install --from "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main#egg=hei-datahub" hei-datahub
```

**Windows (PowerShell):**

```powershell
# Ephemeral run
uvx "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main#egg=hei-datahub"

# Persistent install
uv tool install --from "git+https://$($env:GH_PAT)@github.com/0xpix/Hei-DataHub@main#egg=hei-datahub" hei-datahub
```

---

## 🔍 Troubleshooting

### SSH: "Permission denied (publickey)"

**Cause:** GitHub can't find your SSH key.

**Solutions:**

1. Make sure your key is added to GitHub (step 4 above)
2. Check SSH agent is running:
   ```bash
   ssh-add -l
   ```
3. If empty, add your key again:
   ```bash
   ssh-add ~/.ssh/id_ed25519
   ```

### HTTPS: "Authentication failed"

**Cause:** Token is invalid, expired, or lacks permissions.

**Solutions:**

1. Verify token is set:
   ```bash
   echo $GH_PAT
   ```
2. Check token permissions on GitHub
3. Generate a new token if expired
4. Make sure you're using the correct repository URL

### "Repository not found"

**Cause:** You don't have access to the repository.

**Solutions:**

1. Ask the repository owner to grant you access
2. Verify the repository name is correct: `0xpix/Hei-DataHub`

### SSH: "Could not resolve hostname"

**Cause:** Network/firewall issue.

**Solutions:**

1. Test network:
   ```bash
   ping github.com
   ```
2. Try HTTPS + token method instead
3. Check corporate firewall/proxy settings

---

## 🔒 Security Best Practices

### SSH Keys

- ✅ Use Ed25519 keys (faster, more secure than RSA)
- ✅ Use a passphrase on your private key
- ✅ Keep your private key (`id_ed25519`) secret
- ✅ Only share your public key (`id_ed25519.pub`)

### Personal Access Tokens

- ✅ Use **fine-grained tokens** with minimal permissions
- ✅ Set **short expiration periods** (30-90 days)
- ✅ Store tokens in environment variables, not in code
- ✅ Revoke unused tokens immediately
- ❌ Never commit tokens to Git repositories

---

## 📚 Additional Resources

- [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [GitHub PAT Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [UV Documentation](https://github.com/astral-sh/uv)

---

## 📝 Quick Reference

**SSH Install:**
```bash
uv tool install --from "git+ssh://git@github.com/0xpix/Hei-DataHub.git@main#egg=hei-datahub" hei-datahub
```

**HTTPS Install:**
```bash
export GH_PAT=ghp_xxxxx
uv tool install --from "git+https://${GH_PAT}@github.com/0xpix/Hei-DataHub@main#egg=hei-datahub" hei-datahub
```

---

**Secure your access, secure your data!** 🔐
