# Two-Level Autocomplete Demo

## How It Works

### Level 1: Field Name Completion

When you start typing a field name, it autocompletes to the full field name with colon:

```
You type: so
Press Tab →
Result: source:
         ↑
    Cursor is here, ready for you to type the value
```

**All Field Names:**
- `so` → `source:`
- `pro` → `project:`
- `ta` → `tag:`
- `ow` → `owner:`
- `si` → `size:`
- `fo` → `format:`
- `ty` → `type:`

### Level 2: Field Value Completion

After the colon, it suggests actual values from your datasets:

```
You type: source:go
Press Tab →
Result: source:google.com
                       ↑
                 Completed value from your data
```

**Example Workflow:**

```
Step 1: Type "so"
        [so]

Step 2: Press Tab
        [source:]
                ↑ cursor here

Step 3: Type "goo"
        [source:goo]

Step 4: Press Tab
        [source:google.com ]
                           ↑ space added, ready for next filter
```

## Real Usage Examples

### Example 1: Find datasets from a specific source

```
Type: so         → Tab → source:
Type: hei        → Tab → source:heibox
Result: Shows all datasets from heibox
```

### Example 2: Filter by project

```
Type: pro        → Tab → project:
Type: ML         → Tab → project:ML-Research
Result: Shows all ML-Research datasets
```

### Example 3: Multiple filters

```
Type: pro        → Tab → project:
Type: Deep       → Tab → project:DeepLearning
                        [project:DeepLearning ]

Type: si         → Tab → size:
Type: l          → Tab → size:large
Result: [project:DeepLearning size:large]
        Shows large DeepLearning datasets
```

### Example 4: With free text

```
Type: ta         → Tab → tag:
Type: neur       → Tab → tag:neural
                        [tag:neural ]

Type: network
Result: [tag:neural network]
        ↑              ↑
     filter      free text search
```

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ Search Input                                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  User types: "so"                                       │
│  ──────────────────────────────────────────────────►    │
│  Suggester detects: typing field name                   │
│  ──────────────────────────────────────────────────►    │
│  Shows: "source:"                                       │
│  ──────────────────────────────────────────────────►    │
│  User presses Tab                                       │
│  ──────────────────────────────────────────────────►    │
│  Input becomes: "source:"                               │
│                                                          │
│  User types: "go"                                       │
│  ──────────────────────────────────────────────────►    │
│  Suggester detects: typing field value                  │
│  ──────────────────────────────────────────────────►    │
│  Queries database for sources matching "go"             │
│  ──────────────────────────────────────────────────►    │
│  Shows: "source:google.com"                             │
│  ──────────────────────────────────────────────────►    │
│  User presses Tab                                       │
│  ──────────────────────────────────────────────────►    │
│  Input becomes: "source:google.com "                    │
│                                                          │
│  Ready for next filter or free text!                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

- **Tab** or **→ (Right Arrow)**: Accept suggestion
- **Keep typing**: Refines the suggestion
- **Space after value**: Moves to next filter
- **Esc**: Dismiss suggestion

## Smart Features

### Prefix Matching
```
Type "sou" → suggests "source:"  ✅
Type "src" → no match           ❌ (doesn't match any field)
```

### Case Insensitive
```
Type "SO"   → suggests "source:"  ✅
Type "SoU"  → suggests "source:"  ✅
Type "Pro"  → suggests "project:" ✅
```

### Stops at Exact Match
```
Type "source"    → suggests "source:"  ✅
Type "source:"   → now suggesting values, not field name
Type "source:go" → suggests "source:google.com"
```

## Tips for Fast Searching

1. **Learn the shortcuts**: Just 2-3 letters + Tab for most fields
   - `so` + Tab = `source:`
   - `pr` + Tab = `project:`
   - `ta` + Tab = `tag:`

2. **Chain filters quickly**:
   ```
   pr[Tab]ML[Tab] ta[Tab]neur[Tab] neural
   → project:ML-Research tag:neural neural
   ```

3. **Use size buckets**:
   ```
   si[Tab]l[Tab]
   → size:large
   ```

4. **Mix with free text**:
   ```
   pr[Tab]Data[Tab] dataset analysis
   → project:DataScience dataset analysis
   ```

## Troubleshooting

**Q: I typed "so" but it's not suggesting anything**
- Make sure you're in the search input
- Try typing one more letter: "sou"
- Check that Tab key is working

**Q: After "source:" it's not suggesting my values**
- Values come from your indexed datasets
- Make sure datasets are indexed: `hei-datahub index status`
- Try typing more characters to filter suggestions

**Q: Can I use this with multiple filters?**
- Yes! Each filter word is independent
- `project:ML source:heibox` works perfectly
- The autocomplete always works on the last word you're typing

---

**Enjoy lightning-fast filter entry!** ⚡
