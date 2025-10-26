# 🎓 Learning Guide: Build Hei-DataHub from Scratch

## 📖 Complete Tutorial Index

This is your roadmap to understanding and rebuilding Hei-DataHub. Each page builds on the previous one.

---

## ✅ Completed Tutorials

### Welcome (30 min)
- ✅ [00. Overview & Learning Roadmap](00-overview.md)
- ✅ [01. What is Hei-DataHub?](01-what-is-hei-datahub.md)
- ✅ [01. How It Works (Architecture)](01-architecture.md)
- ✅ [02. Installing & Running Locally](02-setup.md)

### Build the TUI (2-3 hours)
- ✅ [TUI 01. Layout Basics](tui/01-layout-basics.md)
- ✅ [TUI 02. Creating Views & Widgets](tui/02-widgets.md)
- ✅ [TUI 03. Styling & Themes](tui/03-styling.md)
- 🚧 TUI 04. Keyboard Shortcuts & Events
- 🚧 TUI 05. Adding Your Own UI Screen

### Add Functionality (3-4 hours)
- 🚧 Logic 01. Linking UI to Data
- 🚧 Logic 02. Loading & Searching Data
- 🚧 Logic 03. Autocomplete & Filters
- 🚧 Logic 04. Background Sync
- 🚧 Logic 05. Auth & Cloud (HeiBox)

### Deep Dive (4-5 hours)
- 🚧 Deep 01. Directory Overview
- 🚧 Deep 02. Core Scripts Explained
- 🚧 Deep 03. Services & Modules
- 🚧 Deep 04. CLI Commands
- 🚧 Deep 05. Full Line-by-Line Walkthrough

### Advanced Topics (2-3 hours)
- 🚧 Advanced 01. Adding New Features
- 🚧 Advanced 02. Performance Tuning
- 🚧 Advanced 03. Debugging & Logs
- 🚧 Advanced 04. Theming & Branding

---

## 🎯 Quick Paths

### "I Just Want to Add a Feature"
1. Read [00. Overview](00-overview.md) (10 min)
2. Read [Deep 01. Directory Overview](deep/01-directory-structure.md) (20 min)
3. Read [Advanced 01. Adding New Features](advanced/01-extending.md) (30 min)

### "I'm Debugging an Issue"
1. Read [Advanced 03. Debugging](advanced/03-debugging.md) (20 min)
2. Reference [Deep 02. Auth Systems](deep/02-auth.md) as needed

### "I Want the Full Experience"
Follow the guide in order from top to bottom!

---

## 📚 How to Use This Guide

### 1. **Follow Sequentially**
Each tutorial assumes you've read the previous ones.

### 2. **Code Along**
- Install Hei-DataHub locally
- Open the files mentioned in each tutorial
- Run the examples
- Modify and experiment!

### 3. **Build Projects**
Each section ends with "Try It Yourself" exercises:
- Build a custom widget
- Add a new keybinding
- Create a custom theme
- Implement a new filter

---

## 🛠️ Prerequisites

Before starting, make sure you have:

- ✅ Python 3.10+ installed
- ✅ Git installed
- ✅ Basic Python knowledge (functions, classes, imports)
- ✅ Hei-DataHub cloned and running

**Setup:**
```bash
git clone https://github.com/0xpix/Hei-DataHub.git
cd Hei-DataHub
pip install uv
uv pip install -e .
hei-datahub
```

---

## 🧠 Learning Philosophy

### Traditional Docs Say:
> "The `SearchService` handles full-text search queries."

### This Guide Says:
> "Let's build the search feature from scratch. First, we create an SQLite database with FTS5. Then we connect it to the TUI. Here's how each line works..."

**We teach by building**, not just describing.

---

## 📊 Progress Tracking

Check off these milestones as you complete them:

### Phase 1: Understanding
- [ ] I can explain what Hei-DataHub does
- [ ] I understand the layered architecture
- [ ] I can run it locally and add a test dataset

### Phase 2: TUI Mastery
- [ ] I understand how Textual renders UI
- [ ] I can create a custom widget
- [ ] I can style widgets with TCSS
- [ ] I can add keyboard shortcuts

### Phase 3: Functionality
- [ ] I understand how UI calls Services
- [ ] I can query the SQLite database
- [ ] I understand how autocomplete works
- [ ] I understand background sync

### Phase 4: Deep Knowledge
- [ ] I can navigate the entire codebase
- [ ] I know what each directory contains
- [ ] I can explain each core script
- [ ] I can trace any feature from UI to DB

### Phase 5: Contribution Ready
- [ ] I can add a new feature
- [ ] I can optimize performance
- [ ] I can debug issues
- [ ] I can contribute to the project

---

## 🚀 Next Steps

Start your journey here:

**→ [00. Overview & Learning Roadmap](00-overview.md)**

---

## 💡 Tips for Success

1. **Don't rush** — Spend time understanding each concept
2. **Experiment** — Break things and fix them
3. **Take notes** — Draw diagrams, sketch flows
4. **Ask questions** — Open GitHub issues if stuck
5. **Contribute back** — Improve these docs!

---

## 📖 External Resources

- [Textual Official Docs](https://textual.textualize.io/)
- [SQLite FTS5 Docs](https://www.sqlite.org/fts5.html)
- [Pydantic Guide](https://docs.pydantic.dev/)
- [Python asyncio Tutorial](https://docs.python.org/3/library/asyncio.html)

---

**Ready to start? Let's build something amazing!** 🚀
