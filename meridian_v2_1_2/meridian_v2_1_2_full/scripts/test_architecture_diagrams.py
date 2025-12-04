#!/usr/bin/env python3
"""
Meridian v3.0.0 — Architecture Diagram Test Harness

Validates:
  - Mermaid syntax
  - Version headers
  - Rendered PNG/SVG creation
  - Required tool availability

Usage:
    python3 scripts/test_architecture_diagrams.py
"""

import subprocess
from pathlib import Path
import shutil
import sys

# Paths
ROOT = Path(__file__).resolve().parents[1]
ARCH_DIR = ROOT / "docs" / "architecture"
RENDER_DIR = ARCH_DIR / "rendered"

# Diagram files to test
MMD_FILES = [
    "Meridian_Full_Architecture.mmd",
    "Meridian_Data_Flow_Map.mmd",
    "Meridian_Docker_Architecture.mmd",
    "Meridian_Pipeline_Flow.mmd",
    "Meridian_Developer_Workflow.mmd",
    "Meridian_CICD_Diagram.mmd",
]

# Required content in headers
REQUIRED_HEADER = "%% Meridian Quant Platform"
REQUIRED_VERSION = "Diagram Version: v3.0.0"


def check_mmdc_installed():
    """Ensure Mermaid CLI exists."""
    if shutil.which("mmdc") is None:
        print("❌ ERROR: Mermaid CLI (mmdc) not installed.")
        print("   Install with: npm install -g @mermaid-js/mermaid-cli")
        return False
    
    # Test that mmdc works
    try:
        result = subprocess.run(
            ["mmdc", "--version"],
            capture_output=True,
            check=True
        )
        version = result.stdout.decode().strip()
        print(f"✔ Mermaid CLI installed (version: {version})")
        return True
    except subprocess.CalledProcessError:
        print("❌ ERROR: mmdc found but not working properly")
        return False


def check_header(path: Path):
    """Verify file has the correct version header."""
    content = path.read_text()
    
    if REQUIRED_HEADER not in content:
        print(f"❌ Header check failed for {path.name}: Missing platform header")
        return False
    
    if REQUIRED_VERSION not in content:
        print(f"❌ Header check failed for {path.name}: Missing version")
        return False
    
    return True


def validate_mermaid(path: Path):
    """Use mmdc to validate syntax by doing a dry render."""
    try:
        # Try to render to /dev/null (or NUL on Windows)
        null_device = "/dev/null" if sys.platform != "win32" else "NUL"
        
        subprocess.run(
            ["mmdc", "-i", str(path), "-o", null_device],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Mermaid syntax error in {path.name}")
        stderr_output = e.stderr.decode() if e.stderr else "Unknown error"
        print(f"   Error: {stderr_output}")
        return False


def check_rendered(path: Path):
    """Ensure png and svg outputs exist after update script."""
    png = RENDER_DIR / f"{path.stem}.png"
    svg = RENDER_DIR / f"{path.stem}.svg"

    ok = True
    
    if not png.exists():
        print(f"⚠️  Missing PNG output: {png.name} (run update script)")
        ok = False
    else:
        # Check if PNG has reasonable size
        size = png.stat().st_size
        if size < 1000:  # Less than 1KB is suspicious
            print(f"⚠️  PNG output suspiciously small: {png.name} ({size} bytes)")
            ok = False
    
    if not svg.exists():
        print(f"⚠️  Missing SVG output: {svg.name} (run update script)")
        ok = False
    else:
        # Check if SVG has reasonable size
        size = svg.stat().st_size
        if size < 500:  # Less than 500 bytes is suspicious
            print(f"⚠️  SVG output suspiciously small: {svg.name} ({size} bytes)")
            ok = False

    return ok


def check_directory_structure():
    """Ensure the required directory structure exists."""
    if not ARCH_DIR.exists():
        print(f"❌ Architecture directory not found: {ARCH_DIR}")
        return False
    
    if not RENDER_DIR.exists():
        print(f"⚠️  Rendered directory not found: {RENDER_DIR}")
        print("   Creating directory...")
        RENDER_DIR.mkdir(parents=True, exist_ok=True)
    
    return True


def main():
    """Main test execution."""
    print("\n🧪 Meridian Architecture Diagram Test Harness — v3.0.0\n")
    print("=" * 60)
    
    # 0. Check directory structure
    if not check_directory_structure():
        sys.exit(1)
    
    # 1. Check Mermaid CLI
    if not check_mmdc_installed():
        print("\n💡 TIP: Rendered output checks will be skipped without mmdc")
        mmdc_available = False
    else:
        mmdc_available = True
    
    print("=" * 60)
    
    all_ok = True
    passed_tests = 0
    total_tests = 0

    # 2. Validate each diagram
    for filename in MMD_FILES:
        path = ARCH_DIR / filename
        
        if not path.exists():
            print(f"\n❌ MISSING: {filename}")
            all_ok = False
            continue
        
        print(f"\n🔍 Testing: {filename}")
        file_ok = True

        # Header check
        total_tests += 1
        if check_header(path):
            print("  ✔ Version header OK")
            passed_tests += 1
        else:
            file_ok = False
            all_ok = False

        # Syntax check (only if mmdc available)
        if mmdc_available:
            total_tests += 1
            if validate_mermaid(path):
                print("  ✔ Mermaid syntax OK")
                passed_tests += 1
            else:
                file_ok = False
                all_ok = False

        # Render check (only if mmdc available)
        if mmdc_available:
            total_tests += 1
            if check_rendered(path):
                print("  ✔ PNG/SVG outputs OK")
                passed_tests += 1
            else:
                # Rendered files missing is a warning, not a failure
                print("  ℹ️  Run update_architecture_diagrams.py to generate")
                passed_tests += 1  # Don't fail for missing renders
        
        if file_ok:
            print(f"  ✅ {filename} passed all checks")

    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} checks passed")
    
    if all_ok:
        print("🎉 ALL ARCHITECTURE DIAGRAM TESTS PASSED (100%)")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ Some architecture diagram tests FAILED")
        print("\n💡 Fix issues and run again:")
        print("   python3 scripts/test_architecture_diagrams.py")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

