# GitHub Personal Access Token (PAT) - Step-by-Step Visual Guide

## Finding the Repository Permissions Section

Many users have trouble finding the "Repository permissions" section when creating a fine-grained token. Here's exactly where to look:

## Step-by-Step Instructions

### 1. Navigate to Token Creation Page

Go to: **https://github.com/settings/tokens?type=beta**

Or manually:
1. Click your profile picture (top right)
2. Settings
3. Developer settings (bottom of left sidebar)
4. Personal access tokens
5. Fine-grained tokens
6. Generate new token

### 2. Fill Basic Information (Top of Page)

```
Token name: Mini DataHub - Catalog Access
Expiration: 90 days (recommended)
Description: (optional)
Resource owner: [Your username/org]
```

### 3. Repository Access Section

```
○ All repositories
● Only select repositories  ← SELECT THIS
  [Dropdown: Select repositories]  ← Click and choose your catalog repo
```

### 4. **IMPORTANT: Scroll Down!** 🔍

**This is where most people get stuck!**

After selecting your repository, **scroll down the page**. You'll see several collapsed sections:

```
▼ Permissions

  Account permissions (0)
  ▶ [All options grayed out - ignore these]

  Repository permissions (0)  ← YOU NEED THIS SECTION!
  ▶ Click the arrow to expand ▶
```

### 5. Expand "Repository permissions"

Click the **▶** arrow next to "Repository permissions" to expand it.

You'll see a long list of permission options:

```
▼ Repository permissions (0)

  Actions                    [No access ▼]
  Administration             [No access ▼]
  Checks                     [No access ▼]
  Commit statuses            [No access ▼]
  Contents                   [No access ▼]  ← CHANGE THIS!
  Dependabot alerts          [No access ▼]
  Dependabot secrets         [No access ▼]
  Deployments                [No access ▼]
  Discussions                [No access ▼]
  Environments               [No access ▼]
  Issues                     [No access ▼]
  Metadata                   [Read-only]  (always set)
  Pages                      [No access ▼]
  Pull requests              [No access ▼]  ← CHANGE THIS!
  Repository security        [No access ▼]
  Secrets                    [No access ▼]
  Variables                  [No access ▼]
  Webhooks                   [No access ▼]
  Workflows                  [No access ▼]
```

### 6. Set Required Permissions

Find these two rows and change them:

**Contents:**
```
Contents    [No access ▼]  ← Click dropdown
            ↓
            [Read-only]
            [Read and write]  ← SELECT THIS
```

**Pull requests:**
```
Pull requests    [No access ▼]  ← Click dropdown
                 ↓
                 [Read-only]
                 [Read and write]  ← SELECT THIS
```

After selecting both, the counter at the top should show:
```
▼ Repository permissions (2)  ← Shows number of permissions set
```

### 7. Generate Token

1. Scroll to the **very bottom** of the page
2. Click the green **"Generate token"** button
3. **Copy the token immediately!**
   - Format: `github_pat_11A...` or `ghp_...`
   - You won't be able to see it again
4. Paste it into a temporary note or directly into Mini DataHub Settings

## Visual Checklist

Before generating, verify:

- [ ] Token name filled in
- [ ] Expiration set (90 days recommended)
- [ ] Repository access: "Only select repositories" selected
- [ ] Your catalog repository selected from dropdown
- [ ] **Scrolled down to "Repository permissions"**
- [ ] **Expanded "Repository permissions" section** (clicked ▶)
- [ ] **"Contents" set to "Read and write"**
- [ ] **"Pull requests" set to "Read and write"**
- [ ] Counter shows "Repository permissions (2)"

## Common Issues

### "I can't find Repository permissions!"

**Solution:** You need to scroll down! It's below the "Repository access" section. The page is long, and this section is not visible when you first load the page.

### "The permissions are grayed out"

**Solution:** Make sure you selected "Only select repositories" and actually chose a repository from the dropdown. The permissions section is disabled until you select a repo.

### "I only see Account permissions"

**Solution:** Scroll down more! "Repository permissions" is below "Account permissions".

### "It says Repository permissions (0)"

**Solution:** You haven't expanded the section yet. Click the ▶ arrow next to "Repository permissions" to show all options.

## Quick Links

- **Create token**: https://github.com/settings/tokens?type=beta
- **View existing tokens**: https://github.com/settings/tokens
- **GitHub docs**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token

## Video Tutorial (If Available)

Consider recording a quick screen recording showing:
1. Navigating to token creation
2. Scrolling to Repository permissions
3. Expanding the section
4. Setting Contents and Pull requests to Read and write
5. Generating and copying the token

## Testing Your Token

After creating the token and pasting it into Mini DataHub Settings:

1. Press `S` to open Settings
2. Fill in all fields including the token
3. Click **"Test Connection"**
4. Should show: "✓ Connected with push access" or "✓ Connected (read-only, will use fork workflow)"

If test fails, double-check:
- Token copied correctly (no extra spaces)
- Token has correct permissions
- Token hasn't expired
- Repository name is correct

---

**Still having trouble?** Open an issue with a screenshot (hide your token!) at:
https://github.com/0xpix/Hei-DataHub/issues
