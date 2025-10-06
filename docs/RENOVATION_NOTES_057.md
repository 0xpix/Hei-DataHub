# User Documentation Renovation Notes - v0.57.0-beta

**Date:** October 6, 2025
**Version:** 0.57.0-beta "Renovation"
**Source:** `dev-docs/changelog.md`

---

## Executive Summary

This document tracks the renovation of User Documentation for **Hei-DataHub v0.57.0-beta**. This release focuses on comprehensive documentation overhaul, making all features accessible and understandable to users.

---

## Change Checklist from Changelog

### ✅ ADDED Features (v0.57.0-beta)

#### 1. Inline Editing System
- [ ] Document edit mode in Details screen
- [ ] Document editable fields (name, description, source, storage, format, size, type, project, dates)
- [ ] Document save shortcuts: `Ctrl+S` (save), `Esc` (cancel), `Ctrl+Z`/`Ctrl+Shift+Z` (undo/redo)
- [ ] Document atomic save workflow with rollback
- [ ] Document automatic reindexing after save
- [ ] Document validation behavior
- [ ] Document unsaved changes dialog

**Target Pages:**
- `docs/whats-new/0.57-beta.md` (NEW)
- `docs/how-to/edit-datasets.md` (NEW)
- `docs/reference/keybindings.md` (UPDATE)
- `docs/troubleshooting.md` (UPDATE)

---

#### 2. Field-Specific Search
- [ ] Document structured query syntax
- [ ] Document field filters: `source:`, `format:`, `tag:`, etc.
- [ ] Document operators: `>`, `<`, `>=`, `<=` for numeric/date fields
- [ ] Document quoted phrases: `"exact match"`
- [ ] Document fallback behavior for unknown fields
- [ ] Provide search examples

**Target Pages:**
- `docs/whats-new/0.56-beta.md`
- `docs/how-to/search-advanced.md` (NEW)
- `docs/reference/search-syntax.md` (NEW)
- Update existing `docs/20-tutorials/03-search-and-filters.md`

---

#### 3. Search Filter Badges
- [ ] Document visual filter indicators
- [ ] Show screenshot of active filters
- [ ] Explain how badges update in real-time

**Target Pages:**
- `docs/how-to/search-advanced.md`
- `docs/10-ui.md` (UPDATE)

---

#### 4. Auto-Publish Workflow
- [ ] Document automatic PR creation on save
- [ ] Document new vs. update dataset detection
- [ ] Document PR title generation
- [ ] Document GitHub integration requirement

**Target Pages:**
- `docs/whats-new/0.56-beta.md`
- `docs/how-to/publish-datasets.md` (UPDATE or NEW)
- `docs/troubleshooting.md` (add known issue about PR creation)

---

#### 5. Query Syntax Help
- [ ] Document `?` key to open help
- [ ] Document help overlay improvements
- [ ] Add screenshot of query syntax examples

**Target Pages:**
- `docs/02-navigation.md` (UPDATE)
- `docs/reference/keybindings.md` (UPDATE)

---

#### 6. Custom Keybindings
- [ ] Document config file location: `~/.config/hei-datahub/config.yaml`
- [ ] Document keybinding customization syntax
- [ ] Provide examples
- [ ] Note that changes require restart

**Target Pages:**
- `docs/whats-new/0.56-beta.md`
- `docs/12-config.md` (UPDATE)
- `docs/how-to/customize-keybindings.md` (NEW)

---

#### 7. Theme Support
- [ ] Document 12 built-in themes
- [ ] List theme names: Gruvbox, Monokai, Nord, Dracula, etc.
- [ ] Document theme configuration
- [ ] Note that changes require restart

**Target Pages:**
- `docs/whats-new/0.56-beta.md`
- `docs/12-config.md` (UPDATE)
- `docs/how-to/change-theme.md` (NEW)

---

#### 8. Config System
- [ ] Document XDG-compliant configuration
- [ ] Document inline documentation in config file
- [ ] Show example config structure

**Target Pages:**
- `docs/12-config.md` (MAJOR UPDATE)
- `docs/reference/configuration.md` (NEW or consolidate with 12-config.md)

---

#### 9. Action Registry
- [ ] Document centralized action system
- [ ] Explain how actions are registered and documented

**Target Pages:**
- Developer docs only (skip for user docs)

---

### ⚙️ CHANGED Behaviors (v0.56.0-beta)

1. **Search Engine Rebuilt**
   - [ ] Update search documentation
   - [ ] Explain structured query parsing
   - [ ] Note performance improvements (P50: 15-20ms)

2. **FTS5 Phrase Matching Improved**
   - [ ] Document exact-phrase search with quotes

3. **Inline Editing Refresh**
   - [ ] Note real-time metadata updates

4. **Storage System**
   - [ ] Mention atomic writes (technical, brief mention only)

5. **Auto-Publish Distinguishes New vs. Update**
   - [ ] Document different PR types

6. **Help Overlay Context-Aware**
   - [ ] Document improved help system

**Target Pages:**
- `docs/whats-new/0.56-beta.md`
- Various how-to pages

---

### 🐛 FIXED Issues (v0.56.0-beta)

1. FTS5 "no such column" error
2. PR publishing for existing datasets
3. Search crash on unknown field names
4. Empty and quoted query handling
5. Duplicate SQL executions
6. Display refresh after save
7. Type-casting and numeric filter issues

**Target Pages:**
- `docs/whats-new/0.56-beta.md` (brief mention)
- `docs/99-changelog.md` (already there)

---

### ⚠️ KNOWN ISSUES (v0.56.0-beta)

1. Keybinding and theme changes require restart
2. No keybinding conflict detection
3. Search field autocomplete planned for future
4. Edit form scrolling limited for large datasets
5. Nested array fields not editable yet
6. PR creation success but app shows failure/outbox
7. Edited dataset reverts after app restart
8. No scrolling in edit form on small screens
9. Branch not switched after PR publishing

**Target Pages:**
- `docs/troubleshooting.md` (ADD section)
- `docs/90-faq.md` (ADD common workarounds)

---

## Pages to Create

1. **`docs/whats-new/0.57-beta.md`** - Friendly summary of all changes
2. **`docs/how-to/edit-datasets.md`** - Step-by-step inline editing guide
3. **`docs/how-to/search-advanced.md`** - Advanced search techniques
4. **`docs/how-to/customize-keybindings.md`** - Keybinding customization
5. **`docs/how-to/change-theme.md`** - Theme selection guide
6. **`docs/reference/search-syntax.md`** - Complete search syntax reference
7. **`docs/reference/keybindings.md`** - Complete keybinding reference (or update existing)

---

## Pages to Update

1. **`docs/index.md`** - Add version banner for v0.56, link to What's New
2. **`docs/01-getting-started.md`** - Update prerequisites if needed
3. **`docs/02-navigation.md`** - Add new keybindings
4. **`docs/10-ui.md`** - Add search filter badges, update screenshots
5. **`docs/12-config.md`** - Major expansion for new config system
6. **`docs/20-tutorials/03-search-and-filters.md`** - Update with field-specific search
7. **`docs/90-faq.md`** - Add 5-10 common questions about new features
8. **`docs/99-changelog.md`** - Ensure in sync with dev-docs/changelog.md
9. **`docs/troubleshooting.md`** - Add known issues section

---

## Navigation Structure (Updated)

```yaml
nav:
  - Home: index.md
  - Getting Started:
    - Welcome: 00-welcome.md
    - Installation: 01-getting-started.md
    - Navigation: 02-navigation.md
    - The Basics: 03-the-basics.md
  - What's New:
    - 0.57-beta "Renovation": whats-new/0.57-beta.md
  - How-to Guides:
    - Edit Datasets: how-to/edit-datasets.md
    - Advanced Search: how-to/search-advanced.md
    - Publish Datasets: how-to/publish-datasets.md
    - Customize Keybindings: how-to/customize-keybindings.md
    - Change Theme: how-to/change-theme.md
  - Tutorials:
    - Installation: 20-tutorials/01-installation.md
    - Your First Dataset: 20-tutorials/02-first-dataset.md
    - Search & Filters: 20-tutorials/03-search-and-filters.md
  - Reference:
    - UI Guide: 10-ui.md
    - Data & SQL: 11-data-and-sql.md
    - Configuration: 12-config.md
    - Search Syntax: reference/search-syntax.md
    - Keybindings: reference/keybindings.md
  - Help:
    - FAQ: 90-faq.md
    - Troubleshooting: troubleshooting.md
    - Versioning: 98-versioning.md
    - Changelog: 99-changelog.md
```

---

## Quality Checks

- [ ] All internal links resolve
- [ ] All code examples are tested
- [ ] All screenshots are current
- [ ] Search index rebuilt
- [ ] No jargon without definitions
- [ ] Each how-to follows Goal→Steps→Example→Tips structure
- [ ] Callouts used appropriately (Note, Important, Warning)

---

## Deploy Safety

- [ ] GitHub Actions workflow preserves `/dev` folder
- [ ] Verify `clean-exclude: dev/**` is present if using Pages deploy action
- [ ] Test deploy doesn't overwrite developer docs

---

## Next Steps

1. ✅ Read changelog and create this plan
2. ✅ Create What's New page
3. ✅ Create new how-to guides
4. ✅ Update existing pages
5. ✅ Update navigation in mkdocs.yml
6. ⏳ Add callouts and screenshots (manual task - screenshots needed)
7. ⏳ Run quality checks (build and test)
8. ✅ Verify deploy configuration

---

## Notes

- Current version being documented is **0.57.0-beta**
- This is the "Renovation" release focusing on documentation
- Focus on making all features accessible through documentation
- Keep language simple and friendly
- Use step-by-step instructions with examples
- Add visual aids where helpful

---

## Completed Work Summary

### New Pages Created

1. **`docs/whats-new/0.56-beta.md`** ✅
   - Friendly overview of all v0.56 features
   - Explains inline editing, smart search, themes, keybindings
   - Links to detailed how-to guides
   - Lists known issues with workarounds

2. **`docs/how-to/edit-datasets.md`** ✅
   - Step-by-step inline editing guide
   - All editable fields documented
   - Keyboard shortcuts explained
   - Common tasks and troubleshooting

3. **`docs/how-to/search-advanced.md`** ✅
   - Field-specific search examples
   - Numeric and date operators
   - Visual filter badges explained
   - Common search patterns
   - Pro tips and limitations

4. **`docs/how-to/customize-keybindings.md`** ✅
   - Complete keybinding customization guide
   - Examples for Vim, Emacs, VS Code styles
   - All available actions listed
   - Key syntax reference

5. **`docs/how-to/change-theme.md`** ✅
   - All 12 themes documented
   - Screenshots descriptions for each theme
   - Full config examples
   - Terminal compatibility notes

6. **`docs/reference/search-syntax.md`** ✅
   - Complete query syntax reference
   - All fields and operators documented
   - Grammar specification
   - Performance notes

7. **`docs/troubleshooting.md`** ✅
   - All 8 known issues from v0.56 documented
   - Workarounds provided
   - Common problems and solutions
   - Debug logging instructions

### Pages Updated

1. **`docs/index.md`** ✅
   - Added version banner for v0.56
   - Updated feature list
   - Link to What's New
   - Reorganized documentation structure

2. **`docs/90-faq.md`** ✅
   - Added 8 new FAQ entries for v0.56 features
   - Updated limitations section
   - Removed outdated entries

3. **`docs/20-tutorials/03-search-and-filters.md`** ✅
   - Added field-specific search section
   - Numeric and date filter examples
   - Exact phrase search explained
   - Visual badges documented

4. **`mkdocs.yml`** ✅
   - Updated navigation structure
   - Added all new pages
   - Organized into logical sections
   - Updated site description

### Deploy Configuration

✅ **GitHub Actions verified safe:**
- User docs deploy to root: `/`
- Developer docs deploy to obfuscated path: `/x9k2m7n4p8q1`
- No overwrites between user and dev docs
- Both workflows build combined site correctly
