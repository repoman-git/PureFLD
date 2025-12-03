#!/usr/bin/env python3
"""
Build Backlog Script

Generates BACKLOG.md from project files.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from meridian_v2_1_2.backlog import (
    BacklogConfig,
    BacklogBuilder,
    BacklogWriter
)

def main():
    """Build backlog"""
    print("🔍 Building project backlog...")
    
    # Configure
    config = BacklogConfig()
    config.scan_paths = [
        "src/meridian_v2_1_2/",
        "notebooks/",
        "docs/",
        "tests/"
    ]
    
    # Build
    builder = BacklogBuilder(config)
    registry = builder.build()
    
    print(f"✅ Found {len(registry.tasks)} tasks")
    
    # Get statistics
    stats = registry.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Total: {stats['total_tasks']}")
    print(f"   TODO: {stats['todo']}")
    print(f"   In Progress: {stats['in_progress']}")
    print(f"   Done: {stats['done']}")
    print(f"   Phases: {stats['phases']}")
    print(f"   Orphans: {stats['orphans']}")
    
    # Write backlog
    writer = BacklogWriter(registry, config)
    output = writer.write(Path("BACKLOG.md"))
    
    print(f"\n✅ Backlog written to: {output}")
    
    # Show phases
    phases = registry.get_all_phases()
    if phases:
        print(f"\n📋 Phases found: {min(phases)} - {max(phases)}")

if __name__ == '__main__':
    main()

