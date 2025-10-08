# Customizing Badge Styles

The search badge styles are now separated into an external CSS file for easy customization.

## Location

The badge styles are in: `src/mini_datahub/ui/views/home_screen.tcss`

## Modifying Badge Height

To change the height of the search badges, edit the `.filter-badge` section:

```css
.filter-badge {
    margin: 0 1 0 0;
    padding: 0 1;        /* Change vertical padding (first number) to adjust height */
    background: $accent;
    border: solid $accent-darken-2;
    width: auto;
    height: auto;        /* Can set explicit height like: height: 3; */
}
```

### Examples

**Taller badges:**
```css
.filter-badge {
    padding: 1 1;    /* Increase first number for more vertical padding */
    height: 3;       /* Or set explicit height */
}
```

**Shorter badges:**
```css
.filter-badge {
    padding: 0 1;    /* Default: minimal vertical padding */
    height: 1;       /* Compact height */
}
```

## Modifying Badge Colors

The retro color palette classes are also in the same file:

```css
.badge-retro-teal {
    background: #5a9a8a;  /* Change background color */
    color: #ffffff;       /* Change text color */
    border: solid #4a7a6a; /* Change border color */
}
```

You can:
- Modify existing colors
- Add new color classes (remember to update the Python code in `home.py` to include them)
- Adjust border thickness: `border: thick solid #color`

## After Making Changes

1. Save the `.tcss` file
2. Reinstall the package:
   ```bash
   uv tool install --force .
   ```
3. Restart the app:
   ```bash
   hei-datahub
   ```

## Tips

- Textual CSS uses terminal cell units (not pixels)
- `padding: 1 2` means 1 cell vertical, 2 cells horizontal
- `height: 3` means 3 terminal rows
- Use `$accent`, `$primary`, `$panel` for theme-aware colors
- Test with different terminal themes to ensure readability
