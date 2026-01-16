#!/usr/bin/env python3
"""
Check consistency across version files.
Files checked:
- version.yaml
- src/hei_datahub/version.yaml
- pyproject.toml
"""
import sys
from pathlib import Path
import yaml

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: This script requires Python 3.11+ (tomllib) or 'tomli' package installed.")
        print("Install with: pip install tomli")
        sys.exit(1)

def main():
    root = Path(__file__).parent.parent

    # Files to check
    root_version_yaml = root / "version.yaml"
    pkg_version_yaml = root / "src/hei_datahub/version.yaml"
    pyproject_toml = root / "pyproject.toml"

    versions = {}

    # 1. Root version.yaml
    if root_version_yaml.exists():
        with open(root_version_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            versions["version.yaml"] = data.get("version")
    else:
        print(f"WARNING: {root_version_yaml} not found")

    # 2. Package version.yaml
    if pkg_version_yaml.exists():
        with open(pkg_version_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            versions["src/hei_datahub/version.yaml"] = data.get("version")
    else:
        print(f"WARNING: {pkg_version_yaml} not found")

    # 3. pyproject.toml
    if pyproject_toml.exists():
        with open(pyproject_toml, "rb") as f:
            data = tomllib.load(f)
            versions["pyproject.toml"] = data.get("project", {}).get("version")
    else:
        print(f"WARNING: {pyproject_toml} not found")

    # Check consistency
    if not versions:
        print("No version files found!")
        sys.exit(1)

    reference_file = next(iter(versions))
    reference_version = versions[reference_file]

    print(f"Reference version ({reference_file}): {reference_version}")
    print("-" * 40)

    failed = False
    for fname, version in versions.items():
        if version != reference_version:
            print(f"MISMATCH: {fname:<30} {version}")
            failed = True
        else:
            print(f"MATCH:    {fname:<30} {version}")

    if failed:
        sys.exit(1)

    print("-" * 40)
    print("SUCCESS: All versions match.")

if __name__ == "__main__":
    main()
