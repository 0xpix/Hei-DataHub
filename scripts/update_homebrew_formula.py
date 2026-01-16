#!/usr/bin/env python3
"""
Update Homebrew Formula for Hei-DataHub.
Usage: python3 update_homebrew_formula.py <path_to_rb> <version> <arm_sha> <intel_sha>
"""
import sys
import re
from pathlib import Path

def update_formula(path, version, arm_sha, intel_sha):
    print(f"Updating formula at {path}")
    print(f"New version:  {version}")
    print(f"ARM64 SHA:    {arm_sha}")
    print(f"Intel SHA:    {intel_sha}")

    p = Path(path)
    if not p.exists():
        print(f"Error: File {path} not found.")
        sys.exit(1)

    content = p.read_text()
    lines = content.splitlines()
    new_lines = []

    state = "normal" # normal, inside_arm, inside_intel

    # URL templates - Ensure these match the actual release asset names
    # As defined in build_macos.sh: hei-datahub-${VERSION}-macos-${ARCH}.tar.gz
    base_url = f"https://github.com/0xpix/Hei-DataHub/releases/download/{version}"
    arm_url = f"{base_url}/hei-datahub-{version}-macos-arm64.tar.gz"
    intel_url = f"{base_url}/hei-datahub-{version}-macos-x86_64.tar.gz"

    for line in lines:
        stripped = line.strip()
        original_line = line

        # Update version (global scope)
        if state == "normal" and stripped.startswith('version "'):
            # Preserve indentation
            line = re.sub(r'version "[^"]+"', f'version "{version}"', line)
            if line != original_line:
                print("Updated version")

        # State transitions based on standard Homebrew 'on_macos' block structure
        if "if Hardware::CPU.arm?" in line:
            state = "inside_arm"
        elif state == "inside_arm" and line.strip() == "else":
            state = "inside_intel"
        elif state == "inside_intel" and line.strip() == "end":
            state = "normal"

        # Update inside blocks
        if state == "inside_arm":
            if stripped.startswith('url "'):
                line = re.sub(r'url "[^"]+"', f'url "{arm_url}"', line)
                if line != original_line:
                    print("Updated ARM URL")
            elif stripped.startswith('sha256 "'):
                line = re.sub(r'sha256 "[^"]+"', f'sha256 "{arm_sha}"', line)
                if line != original_line:
                    print("Updated ARM SHA")

        elif state == "inside_intel":
            if stripped.startswith('url "'):
                line = re.sub(r'url "[^"]+"', f'url "{intel_url}"', line)
                if line != original_line:
                    print("Updated Intel URL")
            elif stripped.startswith('sha256 "'):
                line = re.sub(r'sha256 "[^"]+"', f'sha256 "{intel_sha}"', line)
                if line != original_line:
                    print("Updated Intel SHA")

        new_lines.append(line)

    p.write_text("\n".join(new_lines) + "\n")
    print("Formula updated successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 update_homebrew_formula.py <path_to_rb> <version> <arm_sha> <intel_sha>")
        sys.exit(1)

    update_formula(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
