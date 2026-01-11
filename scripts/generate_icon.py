#!/usr/bin/env python3
"""
Generate Windows .ico file from SVG source.

This script converts an SVG file to a high-resolution PNG and then
creates a multi-size ICO file suitable for Windows applications.

Usage:
    python scripts/generate_icon.py

Requirements:
    - cairosvg (for SVG to PNG conversion)
    - Pillow (for ICO generation)

Install with:
    pip install cairosvg pillow
"""

import os
import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
SVG_DIR = ASSETS_DIR / "svg"
PNG_DIR = ASSETS_DIR / "png"
ICON_OUTPUT_DIR = ASSETS_DIR / "icons"

# Source and output files
SOURCE_SVG = SVG_DIR / "Hei-datahub-logo-H.svg"
HIRES_PNG = PNG_DIR / "icon_1024.png"
OUTPUT_ICO = ICON_OUTPUT_DIR / "hei-datahub.ico"
# Also copy to installers dir for NSIS
INSTALLER_ICO = PROJECT_ROOT / "scripts" / "installers" / "hei-datahub.ico"

# ICO sizes (must include common Windows sizes)
# Order from largest to smallest for quality
ICO_SIZES = [256, 128, 64, 48, 32, 24, 16]


def convert_svg_to_png(svg_path: Path, png_path: Path, size: int = 1024) -> bool:
    """Convert SVG to high-resolution PNG.

    Args:
        svg_path: Path to source SVG file
        png_path: Path for output PNG file
        size: Target size in pixels (square)

    Returns:
        True if successful, False otherwise
    """
    try:
        import cairosvg
    except ImportError:
        print("❌ Error: cairosvg not installed")
        print("   Install with: pip install cairosvg")
        return False

    if not svg_path.exists():
        print(f"❌ Error: SVG file not found: {svg_path}")
        return False

    # Ensure output directory exists
    png_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📐 Converting SVG to {size}x{size} PNG...")
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=size,
        output_height=size,
    )
    print(f"   ✓ Created: {png_path}")
    return True


def create_ico_from_png(png_path: Path, ico_path: Path, sizes: list[int]) -> bool:
    """Create multi-size ICO from PNG source.

    Args:
        png_path: Path to high-resolution source PNG
        ico_path: Path for output ICO file
        sizes: List of icon sizes to include (e.g., [256, 128, 64, 48, 32, 24, 16])

    Returns:
        True if successful, False otherwise
    """
    try:
        from PIL import Image
    except ImportError:
        print("❌ Error: Pillow not installed")
        print("   Install with: pip install pillow")
        return False

    if not png_path.exists():
        print(f"❌ Error: PNG file not found: {png_path}")
        return False

    # Ensure output directory exists
    ico_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎨 Creating ICO with sizes: {sizes}")

    # Open the source image
    with Image.open(png_path) as source:
        # Convert to RGBA if needed
        if source.mode != 'RGBA':
            source = source.convert('RGBA')

        # Generate all sizes (high quality downsampling)
        icons = []
        for size in sorted(sizes, reverse=True):  # Largest first
            print(f"   📏 Generating {size}x{size}...")
            resized = source.resize((size, size), Image.Resampling.LANCZOS)
            icons.append(resized)

        # Save as ICO with all sizes
        # The first image in the list should be the largest for best quality
        icons[0].save(
            str(ico_path),
            format='ICO',
            sizes=[(img.width, img.height) for img in icons],
            append_images=icons[1:]
        )

    print(f"   ✓ Created: {ico_path}")
    return True


def main():
    """Main function to generate Windows icon."""
    print("=" * 60)
    print("🖼️  HEI-DataHub Windows Icon Generator")
    print("=" * 60)
    print()

    # Step 1: Convert SVG to high-res PNG
    print("Step 1: SVG → High-Resolution PNG")
    print("-" * 40)
    if not convert_svg_to_png(SOURCE_SVG, HIRES_PNG, size=1024):
        print("❌ Failed to convert SVG to PNG")
        return 1
    print()

    # Step 2: Create multi-size ICO
    print("Step 2: PNG → Multi-Size ICO")
    print("-" * 40)
    if not create_ico_from_png(HIRES_PNG, OUTPUT_ICO, ICO_SIZES):
        print("❌ Failed to create ICO file")
        return 1
    print()

    # Step 3: Copy to installers directory for NSIS
    print("Step 3: Copy ICO to installers directory")
    print("-" * 40)
    import shutil
    INSTALLER_ICO.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT_ICO, INSTALLER_ICO)
    print(f"   ✓ Copied to: {INSTALLER_ICO}")
    print()

    # Summary
    print("=" * 60)
    print("✅ Icon generation complete!")
    print()
    print("Generated files:")
    print(f"   • PNG (1024x1024): {HIRES_PNG}")
    print(f"   • ICO (multi-size): {OUTPUT_ICO}")
    print(f"   • ICO (installer):  {INSTALLER_ICO}")
    print()
    print("ICO includes sizes: " + ", ".join(f"{s}x{s}" for s in ICO_SIZES))
    print()
    print("Use the ICO in your Windows builds:")
    print(f'   pyinstaller --icon="{OUTPUT_ICO}" ...')
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
