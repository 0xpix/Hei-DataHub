#!/usr/bin/env python3
"""
Quick version system test for Hei-DataHub.
Run this to verify version.yaml → version.py works correctly.
"""

import sys
from pathlib import Path

# Add src to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

try:
    from hei_datahub.version import (
        BUILD_NUMBER,
        CODENAME,
        GITHUB_URL,
        RELEASE_DATE,
        __version__,
        __version_info__,
    )

    print("✅ Version module imported successfully!")
    print()
    print(f"  Version:      {__version__}")
    print(f"  Version Info: {__version_info__}")
    print(f"  Codename:     {CODENAME}")
    print(f"  Release Date: {RELEASE_DATE}")
    print(f"  Build Number: {BUILD_NUMBER}")
    print(f"  GitHub:       {GITHUB_URL}")
    print()

    # Check version.yaml
    import yaml
    version_yaml = ROOT / "version.yaml"

    if version_yaml.exists():
        with open(version_yaml) as f:
            config = yaml.safe_load(f)

        print("✅ version.yaml loaded successfully!")
        print()
        print(f"  YAML version:  {config['version']}")
        print(f"  YAML codename: {config['codename']}")
        print()

        # Verify consistency
        if __version__ == config['version']:
            print("✅ Version module matches version.yaml!")
        else:
            print(f"❌ MISMATCH: module={__version__}, yaml={config['version']}")
            sys.exit(1)

        if CODENAME == config['codename']:
            print("✅ Codename matches version.yaml!")
        else:
            print(f"❌ MISMATCH: module={CODENAME}, yaml={config['codename']}")
            sys.exit(1)
    else:
        print(f"⚠️  {version_yaml} not found")

    print()
    print("=" * 60)
    print("🎉 All version checks passed!")
    print("=" * 60)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
