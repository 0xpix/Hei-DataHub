# Assets Directory

This directory contains images, screenshots, and other assets for the Hei-DataHub documentation.

## Contents

- **Screenshots:** TUI screenshots for tutorials and guides
- **Diagrams:** Architecture diagrams, flow charts
- **Logos:** Project logos and branding assets

## Adding Assets

When adding assets:

1. Use descriptive filenames (e.g., `home-screen-search.png`, not `screenshot1.png`)
2. Optimize images for web (compress, resize if needed)
3. Keep file sizes reasonable (< 500 KB per image)
4. Use PNG for screenshots, SVG for diagrams when possible

## Usage in Docs

Reference assets using relative paths:

```markdown
![Home Screen](assets/home-screen.png)
```

Or with HTML for sizing:

```html
<img src="assets/architecture-diagram.svg" alt="Architecture" width="600">
```
