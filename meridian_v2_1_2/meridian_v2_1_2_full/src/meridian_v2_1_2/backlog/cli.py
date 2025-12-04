"""
Backlog CLI for Meridian v2.1.2

Command-line interface for backlog management.
"""

import argparse
from pathlib import Path

from .backlog_config import BacklogConfig
from .backlog_builder import BacklogBuilder
from .backlog_writer import BacklogWriter
from .backlog_parser import TaskStatus


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Meridian Backlog Manager")
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build backlog')
    build_parser.add_argument('--output', '-o', type=str, help='Output file')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--phase', '-p', type=int, help='Filter by phase')
    list_parser.add_argument('--status', '-s', type=str, help='Filter by status')
    
    # Mark command
    mark_parser = subparsers.add_parser('mark', help='Mark task status')
    mark_parser.add_argument('task_id', type=str, help='Task ID')
    mark_parser.add_argument('status', type=str, choices=['TODO', 'IN_PROGRESS', 'DONE'])
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if args.command == 'build':
        build_backlog(args.output)
    elif args.command == 'list':
        list_tasks(args.phase, args.status)
    elif args.command == 'mark':
        mark_task(args.task_id, args.status)
    elif args.command == 'stats':
        show_stats()
    else:
        parser.print_help()


def build_backlog(output_file: str = None):
    """Build and write backlog"""
    print("Building backlog...")
    
    config = BacklogConfig()
    builder = BacklogBuilder(config)
    registry = builder.build()
    
    print(f"Found {len(registry.tasks)} tasks")
    
    writer = BacklogWriter(registry, config)
    
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = Path(config.backlog_filename)
    
    result_path = writer.write(output_path)
    
    print(f"Backlog written to: {result_path}")


def list_tasks(phase: int = None, status: str = None):
    """List tasks"""
    config = BacklogConfig()
    builder = BacklogBuilder(config)
    registry = builder.build()
    
    tasks = []
    
    if phase is not None:
        tasks = registry.get_tasks_by_phase(phase)
    else:
        tasks = list(registry.tasks.values())
    
    if status:
        status_enum = TaskStatus[status]
        tasks = [t for t in tasks if t.status == status_enum]
    
    print(f"\nFound {len(tasks)} tasks:\n")
    
    for task in tasks:
        status_icon = {
            TaskStatus.TODO: "⭕",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.DONE: "✅"
        }.get(task.status, "❓")
        
        phase_str = f"P{task.phase:02d}" if task.phase else "ORPHAN"
        
        print(f"{status_icon} [{phase_str}] {task.id}: {task.title}")


def mark_task(task_id: str, status: str):
    """Mark task status"""
    config = BacklogConfig()
    builder = BacklogBuilder(config)
    registry = builder.build()
    
    status_enum = TaskStatus[status]
    
    if registry.update_task_status(task_id, status_enum):
        print(f"✅ Task {task_id} marked as {status}")
        
        # Rebuild backlog
        writer = BacklogWriter(registry, config)
        writer.write()
        print("Backlog updated")
    else:
        print(f"❌ Task {task_id} not found")


def show_stats():
    """Show statistics"""
    config = BacklogConfig()
    builder = BacklogBuilder(config)
    registry = builder.build()
    
    stats = registry.get_statistics()
    
    print("\n📊 Backlog Statistics\n")
    print(f"Total Tasks: {stats['total_tasks']}")
    print(f"  TODO: {stats['todo']}")
    print(f"  In Progress: {stats['in_progress']}")
    print(f"  Done: {stats['done']}")
    print(f"\nPriority:")
    print(f"  High: {stats['high_priority']}")
    print(f"  Medium: {stats['medium_priority']}")
    print(f"  Low: {stats['low_priority']}")
    print(f"\nPhases: {stats['phases']}")
    print(f"Orphans: {stats['orphans']}")


if __name__ == '__main__':
    main()


