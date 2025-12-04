"""
Backlog Configuration for Meridian v2.1.2

Controls backlog extraction and management behavior.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class BacklogConfig:
    """
    Configuration for backlog management system.
    
    Controls task extraction, parsing, and output generation.
    """
    
    # Master switch
    enabled: bool = True
    
    # Scan paths for task extraction
    scan_paths: List[str] = field(default_factory=lambda: [
        "docs/",
        "phases/",
        "src/meridian_v2_1_2/",
    ])
    
    # Task extraction behavior
    include_todo_comments: bool = True
    todo_prefixes: List[str] = field(default_factory=lambda: [
        "TODO",
        "PHASE_TASK",
        "BACKLOG",
        "FIXME",
        "NOTE"
    ])
    
    # Phase detection
    phase_file_patterns: List[str] = field(default_factory=lambda: [
        "PHASE_*.md",
        "phase_*.md",
        "Phase*.md"
    ])
    
    # Output configuration
    backlog_filename: str = "BACKLOG.md"
    sort_by_phase: bool = True
    sort_by_priority: bool = True
    include_orphans: bool = True
    
    # Priority rules (simple v1)
    high_priority_keywords: List[str] = field(default_factory=lambda: [
        "critical",
        "urgent",
        "security",
        "risk",
        "safety"
    ])
    
    medium_priority_keywords: List[str] = field(default_factory=lambda: [
        "test",
        "fix",
        "improve"
    ])


