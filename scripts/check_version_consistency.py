#!/usr/bin/env python3
"""
Version consistency checker for Hei-DataHub.

Verifies that version information from version.yaml is correctly
referenced across all documentation and configuration files.

This replaces the old sync_version.py approach - now version.yaml
is the single source of truth read at runtime by Python.

This script only CHECKS consistency, it does not modify files.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import yaml
except ImportError:
    print("Error: pyyaml is required. Install with: pip install pyyaml")
    sys.exit(1)

# Project root
ROOT = Path(__file__).parent.parent.absolute()
VERSION_YAML = ROOT / "version.yaml"


def load_version_config() -> dict:
    """Load version configuration from version.yaml."""
    if not VERSION_YAML.exists():
        print(f"❌ Error: {VERSION_YAML} not found")
        sys.exit(1)

    with open(VERSION_YAML, 'r') as f:
        config = yaml.safe_load(f)

    required = ['version', 'codename', 'release_date']
    missing = [k for k in required if k not in config]
    if missing:
        print(f"❌ Error: Missing required fields in version.yaml: {', '.join(missing)}")
        sys.exit(1)

    return config


def check_pyproject_toml(config: dict) -> Tuple[bool, List[str]]:
    """Check that pyproject.toml has correct version."""
    pyproject_path = ROOT / "pyproject.toml"
    issues = []

    if not pyproject_path.exists():
        issues.append(f"❌ {pyproject_path} not found")
        return False, issues

    content = pyproject_path.read_text()

    # Check version line
    version_pattern = r'^version\s*=\s*"([^"]+)"'
    match = re.search(version_pattern, content, re.MULTILINE)

    if not match:
        issues.append(f"❌ {pyproject_path}: version field not found")
        return False, issues

    found_version = match.group(1)
    expected_version = config['version']

    if found_version != expected_version:
        issues.append(f"❌ {pyproject_path}: version mismatch")
        issues.append(f"   Expected: {expected_version}")
        issues.append(f"   Found:    {found_version}")
        return False, issues

    return True, []


def check_readme(config: dict) -> Tuple[bool, List[str]]:
    """Check that README.md mentions the current version."""
    readme_path = ROOT / "README.md"
    issues = []

    if not readme_path.exists():
        issues.append(f"⚠️  {readme_path} not found (optional check)")
        return True, issues  # Not critical

    content = readme_path.read_text()
    version = config['version']

    # Just check if version is mentioned somewhere
    if version not in content:
        issues.append(f"⚠️  {readme_path}: version {version} not found")
        issues.append(f"   Consider updating README.md with current version")
        return True, issues  # Warning, not error

    return True, []


def check_docs_version_include(config: dict) -> Tuple[bool, List[str]]:
    """Check that docs/_includes/version.md has correct version."""
    version_md_path = ROOT / "docs" / "_includes" / "version.md"
    issues = []

    if not version_md_path.exists():
        issues.append(f"⚠️  {version_md_path} not found (optional)")
        return True, issues

    content = version_md_path.read_text()
    version = config['version']
    codename = config['codename']

    # Check if either template variables OR actual values are present
    has_template = "{{ project_version }}" in content or "{{ project_codename }}" in content
    has_actual = version in content and codename in content

    if not has_template and not has_actual:
        issues.append(f"❌ {version_md_path}: missing version information")
        issues.append(f"   Should contain either template vars or: {version}, {codename}")
        return False, issues

    return True, []


def check_python_version_module(config: dict) -> Tuple[bool, List[str]]:
    """Check that version.py can load version.yaml correctly."""
    version_py_path = ROOT / "src" / "mini_datahub" / "version.py"
    issues = []

    if not version_py_path.exists():
        issues.append(f"❌ {version_py_path} not found")
        return False, issues

    content = version_py_path.read_text()

    # Check that it loads from version.yaml
    if "version.yaml" not in content or "yaml.safe_load" not in content:
        issues.append(f"❌ {version_py_path}: does not load from version.yaml")
        issues.append(f"   Module should read version.yaml at runtime")
        return False, issues

    # Try to import and check values
    try:
        sys.path.insert(0, str(ROOT / "src"))
        from mini_datahub.version import __version__, CODENAME

        if __version__ != config['version']:
            issues.append(f"❌ version.py: __version__ mismatch")
            issues.append(f"   Expected: {config['version']}")
            issues.append(f"   Got:      {__version__}")
            return False, issues

        if CODENAME != config['codename']:
            issues.append(f"❌ version.py: CODENAME mismatch")
            issues.append(f"   Expected: {config['codename']}")
            issues.append(f"   Got:      {CODENAME}")
            return False, issues

    except Exception as e:
        issues.append(f"❌ Failed to import version.py: {e}")
        return False, issues

    return True, []


def check_no_legacy_version_file(config: dict) -> Tuple[bool, List[str]]:
    """Check that old _version.py doesn't exist."""
    legacy_path = ROOT / "src" / "mini_datahub" / "_version.py"
    issues = []

    if legacy_path.exists():
        issues.append(f"❌ {legacy_path} should not exist")
        issues.append(f"   Legacy _version.py found - should be deleted")
        issues.append(f"   Version info is now read from version.yaml at runtime")
        return False, issues

    return True, []


def main():
    print("=" * 70)
    print("Hei-DataHub Version Consistency Check")
    print("=" * 70)
    print()

    # Load version config
    print(f"📖 Loading version config from: {VERSION_YAML}")
    config = load_version_config()

    print(f"   Version:  {config['version']}")
    print(f"   Codename: {config['codename']}")
    print(f"   Date:     {config['release_date']}")
    print()

    # Run checks
    checks = [
        ("pyproject.toml version", check_pyproject_toml),
        ("README.md mentions version", check_readme),
        ("docs/_includes/version.md", check_docs_version_include),
        ("version.py loads correctly", check_python_version_module),
        ("No legacy _version.py", check_no_legacy_version_file),
    ]

    all_passed = True
    all_issues = []

    for check_name, check_func in checks:
        print(f"🔍 Checking {check_name}...")
        passed, issues = check_func(config)

        if passed:
            print(f"   ✅ Passed")
        else:
            print(f"   ❌ Failed")
            all_passed = False

        if issues:
            for issue in issues:
                print(f"   {issue}")
            all_issues.extend(issues)

        print()

    # Summary
    print("=" * 70)
    if all_passed:
        print("✅ All version consistency checks passed!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ Version consistency checks failed!")
        print()
        print("Issues found:")
        for issue in all_issues:
            if issue.startswith("❌"):
                print(issue)
        print()
        print("Please fix the issues above and try again.")
        print("=" * 70)
        sys.exit(1)


if __name__ == '__main__':
    main()
