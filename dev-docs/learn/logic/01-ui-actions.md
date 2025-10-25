# Linking UI to Data

**Learning Goal**: Understand how user actions flow from UI → Services → Infrastructure → Database.

*(This page is under construction. Check back soon!)*

## Preview

This tutorial covers:
- The data flow architecture
- How `action_*` methods call Services
- How Services coordinate Core + Infrastructure
- Handling success/error responses
- Updating UI with results
- Managing loading states

## Example Flow

```
User presses Enter on a row
  ↓
action_open_details() fires
  ↓
Calls catalog.get_dataset(id)
  ↓
Service queries Infrastructure
  ↓
Infrastructure hits SQLite DB
  ↓
Results flow back up
  ↓
UI renders details screen
```

**Next:** [Loading & Searching Data](02-database.md)
