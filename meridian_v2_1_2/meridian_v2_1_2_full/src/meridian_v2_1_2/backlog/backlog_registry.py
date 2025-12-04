"""
Backlog Registry for Meridian v2.1.2

Central registry for all tasks with deduplication and stable IDs.
"""

from typing import Dict, List, Optional
from collections import defaultdict

from .backlog_parser import Task, TaskStatus, Priority


class BacklogRegistry:
    """
    Central registry for all backlog tasks.
    
    Handles:
    - Task deduplication
    - Stable ID generation
    - Task grouping by phase
    - Dependency tracking
    """
    
    def __init__(self):
        """Initialize backlog registry"""
        self.tasks: Dict[str, Task] = {}
        self.tasks_by_phase: Dict[Optional[int], List[Task]] = defaultdict(list)
        self.id_counter = 0
    
    def add_task(self, task: Task) -> str:
        """
        Add task to registry.
        
        Args:
            task: Task to add
        
        Returns:
            Stable task ID
        """
        # Generate stable ID if needed
        if task.id.startswith('TEMP-') or task.id.startswith('ORPHAN-'):
            task.id = self._generate_stable_id(task.phase)
        
        # Check for duplicates
        existing = self._find_duplicate(task)
        if existing:
            # Merge with existing
            return existing.id
        
        # Add to registry
        self.tasks[task.id] = task
        self.tasks_by_phase[task.phase].append(task)
        
        return task.id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_phase(self, phase: Optional[int]) -> List[Task]:
        """Get all tasks for a phase"""
        return self.tasks_by_phase.get(phase, [])
    
    def get_all_phases(self) -> List[int]:
        """Get all phase numbers"""
        phases = [p for p in self.tasks_by_phase.keys() if p is not None]
        return sorted(phases)
    
    def get_orphan_tasks(self) -> List[Task]:
        """Get tasks with no phase assignment"""
        return self.tasks_by_phase.get(None, [])
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New status
        
        Returns:
            True if updated
        """
        task = self.get_task(task_id)
        if task:
            task.status = status
            return True
        return False
    
    def _generate_stable_id(self, phase: Optional[int]) -> str:
        """Generate stable task ID"""
        self.id_counter += 1
        
        if phase:
            return f"P{phase:02d}-T{self.id_counter:03d}"
        else:
            return f"ORPHAN-T{self.id_counter:03d}"
    
    def _find_duplicate(self, task: Task) -> Optional[Task]:
        """Find duplicate task"""
        for existing in self.tasks.values():
            # Same title and phase = duplicate
            if (existing.title == task.title and 
                existing.phase == task.phase):
                return existing
        
        return None
    
    def get_statistics(self) -> Dict[str, int]:
        """Get registry statistics"""
        total = len(self.tasks)
        by_status = defaultdict(int)
        by_priority = defaultdict(int)
        
        for task in self.tasks.values():
            by_status[task.status.value] += 1
            by_priority[task.priority.value] += 1
        
        return {
            'total_tasks': total,
            'todo': by_status.get('TODO', 0),
            'in_progress': by_status.get('IN_PROGRESS', 0),
            'done': by_status.get('DONE', 0),
            'high_priority': by_priority.get('HIGH', 0),
            'medium_priority': by_priority.get('MEDIUM', 0),
            'low_priority': by_priority.get('LOW', 0),
            'phases': len([p for p in self.tasks_by_phase.keys() if p is not None]),
            'orphans': len(self.get_orphan_tasks())
        }


