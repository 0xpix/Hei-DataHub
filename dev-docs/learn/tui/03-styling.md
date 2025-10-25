# Styling & Themes

**Learning Goal**: Master TCSS (Textual CSS) and create beautiful, themed interfaces.

By the end of this page, you'll:
- Understand TCSS syntax and selectors
- Know how to apply colors, borders, padding, and layout
- Create custom themes
- Debug styling issues

---

## What is TCSS?

**TCSS** = **Textual CSS** — A CSS-like language for styling terminal UIs.

### CSS vs. TCSS

| CSS (Web) | TCSS (Terminal) |
|-----------|-----------------|
| `color: #ff0000;` | `color: #ff0000;` ✅ Same! |
| `background: #000;` | `background: #000;` ✅ Same! |
| `padding: 10px 20px;` | `padding: 1 2;` ⚠️ Different! (rows/cols) |
| `border: 1px solid #fff;` | `border: solid #fff;` ⚠️ No px! |

**Key difference:** TCSS uses **rows and columns**, not pixels.

---

## Basic TCSS Syntax

### Example: Styling a Search Input

**File:** `src/mini_datahub/ui/styles/home.tcss`

```css
#search-input {
    border: solid $accent;
    background: $surface;
    color: $primary;
    padding: 1 2;
    margin: 1 0;
}
```

**Breakdown:**

| Property | Value | Meaning |
|----------|-------|---------|
| `border:` | `solid $accent` | Solid border using accent color |
| `background:` | `$surface` | Background color from theme |
| `color:` | `$primary` | Text color from theme |
| `padding:` | `1 2` | 1 row top/bottom, 2 cols left/right |
| `margin:` | `1 0` | 1 row top/bottom, 0 cols left/right |

---

## Selectors

### By ID

```css
#search-input {
    /* Targets: <Input id="search-input"> */
    border: solid cyan;
}
```

### By Class

```css
.filter-badge {
    /* Targets: <Static classes="filter-badge"> */
    background: $accent;
}
```

### By Type

```css
DataTable {
    /* Targets: ALL DataTable widgets */
    height: 100%;
}

Button {
    /* Targets: ALL Button widgets */
    background: $primary;
}
```

### Pseudo-classes

```css
Button:hover {
    background: $accent;
}

Button:focus {
    border: double $primary;
}
```

---

## Layout Properties

### Dimensions

```css
#main-container {
    width: 80;     /* 80 columns wide */
    height: 50%;   /* 50% of parent height */
    max-width: 100;
    min-height: 10;
}
```

### Padding & Margin

```css
/* Padding: space INSIDE the border */
#widget {
    padding: 1;        /* 1 row/col all sides */
    padding: 1 2;      /* 1 row (top/bottom), 2 cols (left/right) */
    padding: 1 2 3 4;  /* top right bottom left */
}

/* Margin: space OUTSIDE the border */
#widget {
    margin: 1 0;  /* 1 row top/bottom, no side margins */
}
```

---

## Colors

### Direct Colors

```css
#widget {
    color: #fb4934;           /* Hex */
    background: rgb(255, 0, 0); /* RGB */
    border: solid #fff;       /* Shorthand hex */
}
```

### Theme Variables

```css
#widget {
    color: $primary;      /* From theme */
    background: $surface;
    border: solid $accent;
}
```

**Available theme variables:**
- `$primary` — Main brand color
- `$secondary` — Secondary color
- `$accent` — Accent/highlight color
- `$background` — App background
- `$surface` — Widget background
- `$panel` — Panel/container background
- `$error` — Error state
- `$success` — Success state
- `$warning` — Warning state

---

## Borders

### Border Styles

```css
#widget {
    border: solid $primary;    /* ┌─┐│└─┘ */
    border: heavy $accent;     /* ┏━┓┃┗━┛ */
    border: double $secondary; /* ╔═╗║╚═╝ */
    border: rounded $accent;   /* ╭─╮│╰─╯ */
    border: dashed $primary;   /* ┌╌┐╎└╌┘ */
}
```

### Border Sides

```css
#widget {
    border-left: solid $primary;
    border-right: solid $accent;
    border-top: heavy $secondary;
    border-bottom: double $primary;
}
```

---

## Text Styling

```css
#title {
    text-align: center;        /* left | center | right */
    text-style: bold;          /* bold | italic | underline */
    text-style: bold italic;   /* Multiple styles */
}

#heading {
    text-style: reverse;       /* Swap fg/bg colors */
}
```

---

## Real Example: Home Screen

**File:** `src/mini_datahub/ui/styles/home.tcss`

```css
/* Logo banner */
#banner {
    text-align: center;
    padding: 1 0;
    background: $panel;
}

/* Search input */
#search-input {
    border: solid $accent;
    background: $surface;
    padding: 1 2;
    margin: 1 0;
}

#search-input:focus {
    border: double $primary;  /* Double border when focused */
}

/* Results table */
DataTable {
    height: 100%;
    border: solid $accent;
}

DataTable:focus .datatable--cursor {
    background: $accent;      /* Highlight selected row */
}

/* Filter badges */
.filter-badge {
    margin: 0 1 0 0;
    padding: 1 2;
    background: $accent;
    color: white;
    border: rounded $accent;
}
```

---

## Theme System

### Built-in Themes

**File:** `src/mini_datahub/ui/theme.py`

```python
THEMES = {
    "gruvbox": {
        "primary": "#fb4934",
        "secondary": "#b8bb26",
        "accent": "#fabd2f",
        "background": "#282828",
        "surface": "#3c3836",
        "panel": "#1d2021",
        "error": "#fb4934",
        "success": "#b8bb26",
        "warning": "#fabd2f",
    },
    "dark": {
        "primary": "#61afef",
        "secondary": "#98c379",
        "accent": "#c678dd",
        "background": "#282c34",
        "surface": "#3e4451",
        "panel": "#21252b",
    },
    # ... more themes
}
```

---

### How Themes Work

**1. User selects theme** in `config.toml`:
```toml
[app]
theme = "gruvbox"
```

**2. App loads theme** at startup:
```python
# ui/theme.py
def get_current_theme() -> dict:
    config = get_config()
    theme_name = config.get_theme_name()  # "gruvbox"
    return THEMES[theme_name]
```

**3. TCSS uses theme variables**:
```css
#search-input {
    background: $surface;  /* Replaced with #3c3836 (gruvbox) */
}
```

---

### Creating a Custom Theme

**1. Edit `config.toml`:**

```toml
[app]
theme = "custom"

[theme.custom]
primary = "#ff6b6b"
secondary = "#4ecdc4"
accent = "#ffe66d"
background = "#1a1a2e"
surface = "#16213e"
panel = "#0f3460"
error = "#e63946"
success = "#06ffa5"
warning = "#ffbe0b"
```

**2. Restart the app** — your custom theme is applied!

---

## Responsive Design

### Conditional Styles

```css
/* Default */
#container {
    width: 100%;
}

/* When terminal is narrow */
@media (max-width: 80) {
    #container {
        width: 100%;
        padding: 0;
    }
}

/* When terminal is wide */
@media (min-width: 120) {
    #container {
        width: 80%;
        padding: 2;
    }
}
```

---

## Layout Modes

### Flex (default)

```css
Horizontal {
    layout: horizontal;  /* Row */
}

Vertical {
    layout: vertical;    /* Column */
}
```

### Grid

```css
Grid {
    grid-size: 2 3;  /* 2 columns, 3 rows */
    grid-gutter: 1;  /* Space between cells */
}
```

---

## Debugging Styles

### 1. Textual DevTools

```bash
textual run --dev hei-datahub
```

**Features:**
- Live CSS editing
- Widget tree inspector
- Style property viewer

---

### 2. Add Visible Borders

Temporarily add borders to see widget boundaries:

```css
* {
    border: solid red;  /* All widgets */
}
```

---

### 3. Use Background Colors

```css
#container {
    background: red;    /* See the container size */
}

#child {
    background: blue;   /* See the child size */
}
```

---

## Common Patterns

### Centering Content

```css
#centered {
    align: center middle;  /* Horizontal and vertical center */
}
```

---

### Full-Height Container

```css
#main {
    height: 100%;
}
```

---

### Fixed Header/Footer

```css
Header {
    dock: top;
    height: 3;
}

Footer {
    dock: bottom;
    height: 3;
}
```

---

### Scrollable Content

```css
#content {
    height: 100%;
    overflow-y: auto;  /* Vertical scrollbar */
}
```

---

## Real-World Example: Retro Badge Colors

**File:** `src/mini_datahub/ui/styles/home.tcss` (Lines 60-90)

```css
/* Retro color palette for badges */
.badge-retro-teal {
    background: #5a9a8a;
    color: #ffffff;
    border: rounded #5a9a8a;
    padding: 0 1;
}

.badge-retro-coral {
    background: #c97064;
    color: #ffffff;
    border: rounded #c97064;
    padding: 0 1;
}

.badge-retro-sage {
    background: #8b9a7a;
    color: #ffffff;
    border: rounded #8b9a7a;
    padding: 0 1;
}
```

**Usage in code:**

```python
# Assign colors to badges
colors = ["retro-teal", "retro-coral", "retro-sage"]
badge = Static(tag_name, classes=f"badge-{colors[index % len(colors)]}")
```

---

## What You've Learned

✅ **TCSS** is CSS for terminals (similar syntax, different units)
✅ **Selectors**: `#id`, `.class`, `Type`, `:pseudo-class`
✅ **Colors**: Hex, RGB, or theme variables (`$primary`)
✅ **Borders**: `solid`, `heavy`, `double`, `rounded`
✅ **Layout**: `padding`, `margin`, `align`, `layout`
✅ **Themes**: Defined in `theme.py`, selected in `config.toml`
✅ **Debugging**: Use `--dev` mode, temporary borders, or background colors

---

## Try It Yourself

### Exercise 1: Change the Accent Color

**1. Edit `config.toml`:**

```toml
[theme.gruvbox]
accent = "#00ff00"  # Bright green
```

**2. Restart the app** — all `$accent` styles turn green!

---

### Exercise 2: Create a Highlighted Table Row

**1. Edit `home.tcss`:**

```css
DataTable:focus .datatable--cursor {
    background: #ff0000;  /* Red highlight */
    color: #ffffff;
    text-style: bold;
}
```

**2. Restart** — selected row is now bold red!

---

### Exercise 3: Add a Custom Border

**1. Edit `home.tcss`:**

```css
#search-input:focus {
    border: heavy $primary;  /* Thick border when focused */
    background: $accent;
}
```

---

## Next Steps

Now that your TUI looks great, let's make it **interactive**!

**Next:** [Keyboard Shortcuts & Events](04-keybindings.md)

---

## Further Reading

- [Textual CSS Reference](https://textual.textualize.io/styles/)
- [Textual Themes Guide](https://textual.textualize.io/guide/design/)
- [Hei-DataHub Theme System](../../ui/theming.md)
