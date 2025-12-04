#!/usr/bin/env python3
"""
Meridian Architecture Diagram Auto-Update Script
Version: 3.0.0

This script:
- Adds version headers to all .mmd diagram files
- Validates Mermaid syntax
- Renders diagrams to PNG/SVG (requires mmdc CLI)
- Keeps architecture documentation synchronized

Usage:
    python3 scripts/update_architecture_diagrams.py

Requirements:
    npm install -g @mermaid-js/mermaid-cli
"""

import os
import subprocess
from pathlib import Path

VERSION_HEADER = """%% Meridian Quant Platform
%% Diagram Version: v3.0.0
%% Auto-generated and maintained by update_architecture_diagrams.py
%% DO NOT EDIT DIAGRAM CONTENT MANUALLY

"""

# Paths
ROOT = Path(__file__).resolve().parents[1]
ARCH_DIR = ROOT / "docs" / "architecture"
RENDER_DIR = ARCH_DIR / "rendered"

# Diagram files to process
MMD_FILES = [
    "Meridian_Full_Architecture.mmd",
    "Meridian_Data_Flow_Map.mmd",
    "Meridian_Docker_Architecture.mmd",
    "Meridian_Pipeline_Flow.mmd",
    "Meridian_Developer_Workflow.mmd",
    "Meridian_CICD_Diagram.mmd",
]


def ensure_header(path: Path) -> bool:
    """Add version header to diagram file if missing."""
    content = path.read_text()
    
    if not content.startswith("%% Meridian"):
        print(f"  ✅ Adding version header to {path.name}")
        path.write_text(VERSION_HEADER + content)
        return True
    else:
        print(f"  ✓ Header already present in {path.name}")
        return False


def validate_mermaid_syntax(path: Path) -> bool:
    """Validate Mermaid syntax (basic check)."""
    content = path.read_text()
    
    # Basic validation checks
    if "```mermaid" not in content:
        print(f"  ❌ Missing ```mermaid block in {path.name}")
        return False
    
    if "flowchart" not in content:
        print(f"  ⚠️  Warning: No flowchart declaration in {path.name}")
    
    return True


def render_file(path: Path) -> bool:
    """Render .mmd file to PNG and SVG using mmdc CLI."""
    basename = path.stem
    png_file = RENDER_DIR / f"{basename}.png"
    svg_file = RENDER_DIR / f"{basename}.svg"
    
    try:
        # Check if mmdc is installed
        subprocess.run(["mmdc", "--version"], 
                      capture_output=True, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  ⚠️  mmdc CLI not installed - skipping render for {path.name}")
        print(f"      Install: npm install -g @mermaid-js/mermaid-cli")
        return False
    
    try:
        # Render to PNG
        subprocess.run(["mmdc", "-i", str(path), "-o", str(png_file)], 
                      capture_output=True,
                      check=True)
        print(f"  ✅ Rendered {basename}.png")
        
        # Render to SVG
        subprocess.run(["mmdc", "-i", str(path), "-o", str(svg_file)],
                      capture_output=True,
                      check=True)
        print(f"  ✅ Rendered {basename}.svg")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to render {path.name}: {e}")
        return False


def main():
    """Main execution function."""
    print("🔧 Meridian Architecture Diagram Update Script v3.0.0\n")
    
    # Ensure rendered directory exists
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Working directory: {ARCH_DIR}\n")
    
    # Process each diagram file
    updated_count = 0
    rendered_count = 0
    
    for filename in MMD_FILES:
        path = ARCH_DIR / filename
        
        if not path.exists():
            print(f"❌ File not found: {filename}")
            continue
        
        print(f"Processing: {filename}")
        
        # Add/check version header
        if ensure_header(path):
            updated_count += 1
        
        # Validate syntax
        validate_mermaid_syntax(path)
        
        # Render to PNG/SVG
        if render_file(path):
            rendered_count += 1
        
        print()  # Blank line between files
    
    # Summary
    print("=" * 60)
    print(f"✅ Complete!")
    print(f"   Files processed: {len(MMD_FILES)}")
    print(f"   Headers updated: {updated_count}")
    print(f"   Files rendered: {rendered_count}")
    print(f"   Output directory: {RENDER_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

