# Hei-DataHub Tutorial Documentation

!!! tip "🎓 Step-by-Step Learning Guide"
    **Learn how to build Hei-DataHub from scratch!** This comprehensive tutorial teaches you everything you need to know about building a TUI application with Textual, SQLite FTS5 search, and WebDAV cloud sync.

!!! info "Tutorial Documentation Site"
    **You are viewing the tutorial documentation.** This site contains step-by-step guides for learning how Hei-DataHub works.

    - Looking for user documentation? → [**User Manual**](https://0xpix.github.io/Hei-DataHub)
    - Looking for API reference? → [**Developer Docs**](https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1)

!!! info "Version Compatibility"
    **Tutorial for v0.60.0-beta "Clean-up"**
    Compatible with app releases v0.60.x
    Updated: October 28, 2025

---

## Welcome to the Tutorial! 👩‍💻👨‍💻

This **hands-on learning guide** will teach you how to build Hei-DataHub from the ground up. By the end, you'll understand:

- 🎨 **Building Terminal UIs** with Textual framework
- 🔍 **Full-text search** with SQLite FTS5
- ☁️ **Cloud sync** with WebDAV integration
- ⚡ **Performance optimization** for instant search
- 🎯 **Clean architecture** for maintainable code
- ⌨️ **Vim-style keybindings** and user experience

**No prior TUI experience required!** We start from basics and build up.

---

## 🎯 Learning Path

### Phase 1: Understanding the Basics (2-3 hours)

Start here to get the big picture:

1. [**What is Hei-DataHub?**](01-what-is-hei-datahub.md)
   - The problem it solves
   - Key features and design goals
   - User workflow walkthrough

2. [**How It Works (Architecture)**](01-architecture.md)
   - System architecture overview
   - Data flow diagrams
   - Component interaction

3. [**Installing & Running Locally**](02-setup.md)
   - Development environment setup
   - Running from source
   - Project structure tour

---

### Phase 2: Build the TUI (4-6 hours)

Learn how to create beautiful terminal interfaces:

1. [**Layout Basics**](tui/01-layout-basics.md)
   - Textual framework introduction
   - Containers and widgets
   - Responsive layouts

2. [**Creating Views & Widgets**](tui/02-widgets.md)
   - Screen components
   - Custom widgets
   - State management

3. [**Styling & Themes**](tui/03-styling.md)
   - TCSS styling language
   - Theme system
   - Color schemes and retro design

4. [**Keyboard Shortcuts & Events**](tui/04-keybindings.md)
   - Event handling in Textual
   - Vim-style navigation
   - Action system

5. [**Adding Your Own Screen**](tui/05-custom-view.md)
   - Create a new screen from scratch
   - Integrate with the app
   - Best practices

---

### Phase 3: Add Functionality (4-6 hours)

Connect the UI to real data and logic:

1. [**Linking UI to Data**](logic/01-ui-actions.md)
   - Action handlers
   - Data flow from UI to backend
   - Error handling

2. [**Database Operations**](logic/02-database.md)
   - SQLite integration
   - FTS5 full-text search
   - Query optimization

3. [**Autocomplete Logic**](logic/03-autocomplete.md)
   - Smart suggestions
   - Ranking algorithms
   - Context-aware completion

4. [**Cloud Sync**](logic/04-cloud-sync.md)
   - WebDAV integration
   - Background synchronization
   - Conflict resolution

5. [**CLI Integration**](logic/05-cli-integration.md)
   - Argument parsing
   - Command structure
   - TUI vs CLI modes

---

### Phase 4: Deep Dive (4-6 hours)

Master advanced topics:

1. [**Directory Structure**](deep/01-directory-structure.md)
   - Project organization
   - Module responsibilities
   - Import patterns

2. [**Auth Systems**](deep/02-auth.md)
   - Credential management
   - Keyring integration
   - Security best practices

3. [**Configuration**](deep/03-config.md)
   - TOML configuration
   - Environment variables
   - User preferences

4. [**Indexing**](deep/04-indexing.md)
   - FTS5 index management
   - Incremental updates
   - Performance tuning

5. [**Testing**](deep/05-testing.md)
   - Unit tests
   - Integration tests
   - TUI testing strategies

---

## 🚀 Quick Start Paths

Choose your journey based on your interests:

<div class="grid cards" markdown>

-   **🎨 UI/UX Developer**

    Focus on building beautiful terminal interfaces

    **Path:** Basics → [TUI Track](#phase-2-build-the-tui-4-6-hours) → Styling → Keybindings

-   **⚡ Backend Engineer**

    Focus on data, search, and performance

    **Path:** Basics → Architecture → [Logic Track](#phase-3-add-functionality-4-6-hours) → Database → Indexing

-   **☁️ Cloud Integration**

    Focus on WebDAV sync and authentication

    **Path:** Basics → Architecture → Cloud Sync → Auth Systems

-   **🎓 Complete Course**

    Learn everything from scratch

    **Path:** All phases in order (14-20 hours total)

</div>

---

## 💡 What You'll Build

By following this tutorial, you'll understand how to build:

✅ A **full-featured TUI application** with Textual
✅ **Lightning-fast search** (<80ms) with SQLite FTS5
✅ **Cloud synchronization** with WebDAV
✅ **Secure credential management** with system keyring
✅ **Smart autocomplete** with ranking algorithms
✅ **Vim-style keybindings** for power users
✅ **Multiple themes** with custom styling
✅ **Comprehensive CLI** interface

---

## 📚 Prerequisites

**Required:**
- Python 3.10+ knowledge
- Basic terminal/command line usage
- Git basics

**Helpful but not required:**
- Experience with any TUI framework
- SQLite or database knowledge
- REST API/WebDAV concepts

---

## 🛠️ Development Environment

Before starting, make sure you have:

```bash
# Required tools
python --version   # 3.10 or higher
git --version      # Any recent version
uv --version       # Fast Python package manager (optional)

# Clone the repository
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub

# Install dependencies
pip install -e ".[dev]"

# Run the app
hei-datahub
```

**See [Installing & Running Locally](02-setup.md) for detailed setup instructions.**

---

## 📖 How to Use This Tutorial

### Learning Tips

1. **Follow in order** — Each section builds on previous concepts
2. **Code along** — Type examples yourself, don't just read
3. **Experiment** — Modify code and see what happens
4. **Take breaks** — Complex topics are easier in chunks
5. **Ask questions** — Open discussions on GitHub

### Navigation Tips

- Use **sidebar navigation** to jump between sections
- Press **`:`** then type **`:user`** to go to user docs
- Press **`:`** then type **`:dev`** to go to dev docs
- Use **`j/k`** to scroll, **`gg/G`** for top/bottom
- Press **`/`** to search the docs

---

## 🎯 Learning Outcomes

After completing this tutorial, you will be able to:

- ✅ Build complex TUI applications with Textual
- ✅ Implement full-text search with SQLite FTS5
- ✅ Integrate cloud storage with WebDAV
- ✅ Design clean, maintainable Python architectures
- ✅ Optimize for performance (<300ms startup, <80ms search)
- ✅ Contribute to the Hei-DataHub project

---

## 🔗 Additional Resources

- **User Documentation:** [Hei-DataHub Manual](https://0xpix.github.io/Hei-DataHub)
- **Developer Reference:** [API Docs](https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1)
- **GitHub Repository:** [0xpix/Hei-DataHub](https://github.com/0xpix/Hei-DataHub)
- **Textual Framework:** [textual.textualize.io](https://textual.textualize.io/)
- **SQLite FTS5:** [sqlite.org/fts5.html](https://www.sqlite.org/fts5.html)

---

## 🤝 Get Help & Contribute

- **Questions?** → [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
- **Found a bug?** → [Report Issue](https://github.com/0xpix/Hei-DataHub/issues)
- **Tutorial unclear?** → [Suggest improvement](https://github.com/0xpix/Hei-DataHub/issues)

---

## 🎓 Ready to Start?

Begin your journey here:

**→ [What is Hei-DataHub?](01-what-is-hei-datahub.md)**

Or jump directly to:
- [Architecture Overview](01-architecture.md)
- [Setup Guide](02-setup.md)
- [Building the TUI](tui/01-layout-basics.md)

---

**Happy learning!** 🚀


---

## Welcome, Developer! 👩‍💻👨‍💻

This is the **comprehensive tutorial guide** for Hei-DataHub. Whether you're:

- 🎓 **Learning how to build** a TUI app with Textual → [**Start the Learning Guide**](00-overview.md)
- 🔧 **Contributing code** to the project
- 🏗️ **Understanding the architecture** before diving in
- 🐛 **Debugging an issue** deep in the stack
- 🚀 **Extending functionality** with plugins or adapters
- 📦 **Building releases** and managing CI/CD
- 📚 **Maintaining this docs site** itself

...you're in the right place.

---

## 🎓 New to the Project?

**Start with the Learning Guide** — a step-by-step tutorial that teaches you how to build Hei-DataHub from scratch:

- [**Learning Guide Home**](00-overview.md) — Master index and roadmap
- [**What is Hei-DataHub?**](01-what-is-hei-datahub.md) — Problem, solution, and overview
- [**How It Works (Architecture)**](01-architecture.md) — System design deep dive
- [**Installing & Running Locally**](02-setup.md) — Get it running in 5 minutes
- [**Building the TUI**](tui/01-layout-basics.md) — Create beautiful terminal interfaces
- [**Adding Functionality**](logic/01-ui-actions.md) — Connect UI to backend logic

**Estimated time:** 2-3 hours for core concepts, 12-16 hours for full mastery.

---

## 🚀 Quick Start Paths

Choose your journey based on your interests:

<div class="grid cards" markdown>

-   **� UI/UX Developer**

    Focus on building beautiful terminal interfaces

    **Path:** Basics → [TUI Track](#phase-2-build-the-tui-4-6-hours) → Styling → Keybindings

-   **⚡ Backend Engineer**

    Focus on data, search, and performance

    **Path:** Basics → Architecture → [Logic Track](#phase-3-add-functionality-4-6-hours) → Database → Indexing

-   **☁️ Cloud Integration**

    Focus on WebDAV sync and authentication

    **Path:** Basics → Architecture → Cloud Sync → Auth Systems

-   **🎓 Complete Course**

    Learn everything from scratch

    **Path:** All phases in order (14-20 hours total)

</div>

---

## 💡 What You'll Build

By following this tutorial, you'll understand how to build:

✅ A **full-featured TUI application** with Textual
✅ **Lightning-fast search** (<80ms) with SQLite FTS5
✅ **Cloud synchronization** with WebDAV
✅ **Secure credential management** with system keyring
✅ **Smart autocomplete** with ranking algorithms
✅ **Vim-style keybindings** for power users
✅ **Multiple themes** with custom styling
✅ **Comprehensive CLI** interface

---

## 📚 Prerequisites

**Required:**
- Python 3.10+ knowledge
- Basic terminal/command line usage
- Git basics

**Helpful but not required:**
- Experience with any TUI framework
- SQLite or database knowledge
- REST API/WebDAV concepts

---

## 🛠️ Development Environment

Before starting, make sure you have:

```bash
# Required tools
python --version   # 3.10 or higher
git --version      # Any recent version
uv --version       # Fast Python package manager (optional)

# Clone the repository
git clone git@github.com:0xpix/Hei-DataHub.git
cd Hei-DataHub

# Install dependencies
pip install -e ".[dev]"

# Run the app
hei-datahub
```

**See [Installing & Running Locally](02-setup.md) for detailed setup instructions.**

---

## 📖 How to Use This Tutorial

### Learning Tips

1. **Follow in order** — Each section builds on previous concepts
2. **Code along** — Type examples yourself, don't just read
3. **Experiment** — Modify code and see what happens
4. **Take breaks** — Complex topics are easier in chunks
5. **Ask questions** — Open discussions on GitHub

### Navigation Tips

- Use **sidebar navigation** to jump between sections
- Press **`:`** then type **`:user`** to go to user docs
- Press **`:`** then type **`:dev`** to go to dev docs
- Use **`j/k`** to scroll, **`gg/G`** for top/bottom
- Press **`/`** to search the docs

---

## 🎯 Learning Outcomes

After completing this tutorial, you will be able to:

- ✅ Build complex TUI applications with Textual
- ✅ Implement full-text search with SQLite FTS5
- ✅ Integrate cloud storage with WebDAV
- ✅ Design clean, maintainable Python architectures
- ✅ Optimize for performance (<300ms startup, <80ms search)
- ✅ Contribute to the Hei-DataHub project

---

## 🔗 Additional Resources

- **User Documentation:** [Hei-DataHub Manual](https://0xpix.github.io/Hei-DataHub)
- **Developer Reference:** [API Docs](https://0xpix.github.io/Hei-DataHub/x9k2m7n4p8q1)
- **GitHub Repository:** [0xpix/Hei-DataHub](https://github.com/0xpix/Hei-DataHub)
- **Textual Framework:** [textual.textualize.io](https://textual.textualize.io/)
- **SQLite FTS5:** [sqlite.org/fts5.html](https://www.sqlite.org/fts5.html)

---

## 🤝 Get Help & Contribute

- **Questions?** → [GitHub Discussions](https://github.com/0xpix/Hei-DataHub/discussions)
- **Found a bug?** → [Report Issue](https://github.com/0xpix/Hei-DataHub/issues)
- **Tutorial unclear?** → [Suggest improvement](https://github.com/0xpix/Hei-DataHub/issues)

---

## 🎓 Ready to Start?

Begin your journey here:

**→ [What is Hei-DataHub?](01-what-is-hei-datahub.md)**

Or jump directly to:
- [Architecture Overview](01-architecture.md)
- [Setup Guide](02-setup.md)
- [Building the TUI](tui/01-layout-basics.md)

---

**Happy learning!** 🚀
