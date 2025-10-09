#!/usr/bin/env python3
"""
One-time migration script: Replace hardcoded version/codename with MkDocs macros.

This script walks through Markdown files and replaces visible occurrences of the
current version and codename with MkDocs macro placeholders.

Features:
- Protects code blocks (triple backticks) and inline code (single backticks)
- Skips historical/changelog content
- Dry-run by default, requires --apply to make changes
- Reports all changes before applying

Usage:
    python tools/migrate_markdown_version_codename.py           # Dry run
    python tools/migrate_markdown_version_codename.py --apply   # Apply changes

Exit codes:
    0 - Success (changes found and applied, or dry-run completed)
    1 - No changes needed (may indicate mis-detection)
    2 - Error occurred
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Current version and codename to replace
CURRENT_VERSION = "0.57.1-beta"
CURRENT_CODENAME = "Renovation"

# Patterns to replace (will be escaped for regex)
VERSION_PATTERNS = [
    "0.57.1-beta",
    "0.57.0-beta",
]

# Files/patterns to skip (historical content)
SKIP_PATTERNS = [
    "**/changelog.md",
    "**/CHANGELOG.md",
    "**/release-notes.md",
    "**/RELEASE_NOTES.md",
    # Don't skip whats-new as it contains current version references
]

# Directories to search
SEARCH_DIRS = ["docs/"]


def is_in_code_block(text: str, pos: int) -> bool:
    """Check if position is inside a code block (triple backticks or inline code)."""
    # Check for triple backticks
    before_text = text[:pos]
    triple_count = before_text.count("```")
    if triple_count % 2 == 1:  # Odd number means we're inside a code block
        return True

    # Check for inline code (single backticks on the same line)
    # Find the line containing this position
    line_start = text.rfind('\n', 0, pos) + 1
    line_end = text.find('\n', pos)
    if line_end == -1:
        line_end = len(text)

    line = text[line_start:line_end]
    pos_in_line = pos - line_start

    # Count backticks before this position in the line
    backtick_count = line[:pos_in_line].count('`')
    return backtick_count % 2 == 1


def should_skip_file(filepath: Path) -> bool:
    """Check if file should be skipped based on patterns."""
    for pattern in SKIP_PATTERNS:
        if filepath.match(pattern):
            return True

    # Check if filename suggests it's historical
    filename_lower = filepath.name.lower()
    if any(x in filename_lower for x in ["changelog", "release-note", "history"]):
        return True

    return False


def replace_in_markdown(content: str, version: str, codename: str) -> Tuple[str, int]:
    """
    Replace version and codename in markdown content, avoiding code blocks.

    Returns:
        Tuple of (modified_content, replacement_count)
    """
    replacements = 0
    result = content

    # Replace version patterns (but not in code blocks)
    for pattern in VERSION_PATTERNS:
        escaped_pattern = re.escape(pattern)

        # Find all occurrences
        matches = list(re.finditer(escaped_pattern, result))

        # Process in reverse to maintain positions
        for match in reversed(matches):
            if not is_in_code_block(result, match.start()):
                # Replace with macro
                result = result[:match.start()] + "{{ project_version }}" + result[match.end():]
                replacements += 1

    # Replace codename (but not in code blocks, headings with historical context)
    # Be more selective with codename - only replace when it appears as standalone or in quotes
    codename_patterns = [
        f'"{codename}"',
        f'`{codename}`',
        f' {codename} ',
        f' {codename}.',
        f' {codename},',
        f':{codename}',
        f': {codename}',
    ]

    for pattern in codename_patterns:
        if '`' not in pattern:  # Skip patterns with backticks (inline code)
            matches = list(re.finditer(re.escape(pattern), result))

            for match in reversed(matches):
                if not is_in_code_block(result, match.start()):
                    # Preserve surrounding punctuation
                    matched_text = match.group()
                    prefix = matched_text[:matched_text.index(codename)]
                    suffix = matched_text[matched_text.index(codename) + len(codename):]

                    replacement = f'{prefix}{{{{ project_codename }}}}{suffix}'
                    result = result[:match.start()] + replacement + result[match.end():]
                    replacements += 1

    return result, replacements


def process_directory(directory: Path, apply: bool = False) -> List[Tuple[Path, int]]:
    """
    Process all markdown files in directory.

    Returns:
        List of (filepath, replacement_count) tuples
    """
    changes = []

    for md_file in directory.rglob("*.md"):
        if should_skip_file(md_file):
            continue

        try:
            content = md_file.read_text(encoding="utf-8")
            new_content, count = replace_in_markdown(content, CURRENT_VERSION, CURRENT_CODENAME)

            if count > 0:
                changes.append((md_file, count))

                if apply:
                    md_file.write_text(new_content, encoding="utf-8")

        except Exception as e:
            print(f"Error processing {md_file}: {e}", file=sys.stderr)
            continue

    return changes


def main():
    parser = argparse.ArgumentParser(
        description="Migrate hardcoded version/codename to MkDocs macros"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run)"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("Markdown Version/Codename Migration Script")
    print("=" * 70)
    print(f"Current version: {CURRENT_VERSION}")
    print(f"Current codename: {CURRENT_CODENAME}")
    print(f"Mode: {'APPLY CHANGES' if args.apply else 'DRY RUN'}")
    print("=" * 70)
    print()

    all_changes = []

    for search_dir in SEARCH_DIRS:
        path = Path(search_dir)
        if not path.exists():
            print(f"Warning: Directory {search_dir} not found, skipping.")
            continue

        print(f"Scanning {search_dir}...")
        changes = process_directory(path, apply=args.apply)
        all_changes.extend(changes)

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if not all_changes:
        print("❌ No changes found!")
        print()
        print("This might indicate:")
        print("  - Version/codename already migrated")
        print("  - Incorrect version/codename constants")
        print("  - Files already using macros")
        return 1

    print(f"Files to modify: {len(all_changes)}")
    print()

    total_replacements = 0
    for filepath, count in sorted(all_changes):
        try:
            rel_path = filepath.relative_to(Path.cwd())
        except ValueError:
            rel_path = filepath
        print(f"  {rel_path}: {count} replacements")
        total_replacements += count

    print()
    print(f"Total replacements: {total_replacements}")
    print()

    if not args.apply:
        print("=" * 70)
        print("This was a DRY RUN - no files were modified")
        print("Run with --apply to make changes")
        print("=" * 70)
    else:
        print("=" * 70)
        print("✅ Changes applied successfully!")
        print("=" * 70)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAborted by user", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"\n\nFatal error: {e}", file=sys.stderr)
        sys.exit(2)
