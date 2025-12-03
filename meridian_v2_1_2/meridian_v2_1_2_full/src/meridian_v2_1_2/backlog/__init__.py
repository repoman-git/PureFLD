"""
Backlog Manager for Meridian v2.1.2

Centralized task extraction, tracking, and reporting system.
"""

from .backlog_config import BacklogConfig
from .backlog_parser import BacklogParser, Task, TaskStatus, Priority
from .backlog_registry import BacklogRegistry
from .backlog_builder import BacklogBuilder
from .backlog_writer import BacklogWriter

__all__ = [
    'BacklogConfig',
    'BacklogParser',
    'Task',
    'TaskStatus',
    'Priority',
    'BacklogRegistry',
    'BacklogBuilder',
    'BacklogWriter',
]

