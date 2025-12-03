"""
Backlog Parser for Meridian v2.1.2

Extracts tasks from various sources (files, comments, docs).
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class TaskStatus(str, Enum):
    """Task status"""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Priority(str, Enum):
    """Task priority"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Task:
    """Task data structure"""
    id: str
    phase: Optional[int]
    title: str
    module: Optional[str]
    priority: Priority
    status: TaskStatus
    dependencies: List[str]
    source_file: Optional[str] = None
    line_number: Optional[int] = None


class BacklogParser:
    """
    Parses tasks from multiple sources.
    
    Extracts from:
    - Phase specification files
    - Documentation files
    - Code TODO comments
    """
    
    def __init__(self, config):
        """
        Initialize backlog parser.
        
        Args:
            config: BacklogConfig instance
        """
        self.config = config
    
    def parse_file(self, file_path: Path) -> List[Task]:
        """
        Parse tasks from a single file.
        
        Args:
            file_path: Path to file
        
        Returns:
            List of extracted tasks
        """
        tasks = []
        
        try:
            content = file_path.read_text()
            
            # Detect phase number from filename
            phase = self._extract_phase_from_filename(file_path)
            
            # Extract markdown tasks
            if file_path.suffix == '.md':
                tasks.extend(self._parse_markdown_tasks(content, file_path, phase))
            
            # Extract TODO comments
            if self.config.include_todo_comments:
                tasks.extend(self._parse_todo_comments(content, file_path, phase))
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return tasks
    
    def _extract_phase_from_filename(self, file_path: Path) -> Optional[int]:
        """Extract phase number from filename"""
        # Try pattern like PHASE_37.md or phase_37.md
        match = re.search(r'phase[_-]?(\d+)', file_path.name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return None
    
    def _parse_markdown_tasks(
        self,
        content: str,
        file_path: Path,
        phase: Optional[int]
    ) -> List[Task]:
        """Parse markdown checkbox tasks"""
        tasks = []
        
        # Pattern: - [ ] Task or - [x] Task
        pattern = r'^[\s]*-\s*\[([ xX])\]\s*(.+)$'
        
        for i, line in enumerate(content.split('\n'), 1):
            match = re.match(pattern, line)
            if match:
                is_done = match.group(1).lower() == 'x'
                title = match.group(2).strip()
                
                # Try to get relative path, fall back to absolute
                try:
                    module_path = str(file_path.relative_to(Path.cwd()))
                except ValueError:
                    module_path = str(file_path)
                
                task = Task(
                    id=self._generate_temp_id(phase, i),
                    phase=phase,
                    title=title,
                    module=module_path if file_path.exists() else None,
                    priority=self._infer_priority(title),
                    status=TaskStatus.DONE if is_done else TaskStatus.TODO,
                    dependencies=[],
                    source_file=str(file_path),
                    line_number=i
                )
                
                tasks.append(task)
        
        return tasks
    
    def _parse_todo_comments(
        self,
        content: str,
        file_path: Path,
        phase: Optional[int]
    ) -> List[Task]:
        """Parse TODO comments from code"""
        tasks = []
        
        # Build pattern from configured prefixes
        prefixes = '|'.join(self.config.todo_prefixes)
        pattern = rf'#\s*({prefixes}):\s*(.+)$'
        
        for i, line in enumerate(content.split('\n'), 1):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                prefix = match.group(1)
                title = match.group(2).strip()
                
                # Check for phase specification in comment
                phase_match = re.search(r'P(?:HASE)?[-_]?(\d+)', title, re.IGNORECASE)
                if phase_match:
                    task_phase = int(phase_match.group(1))
                else:
                    task_phase = phase
                
                # Try to get relative path, fall back to absolute
                try:
                    module_path = str(file_path.relative_to(Path.cwd()))
                except ValueError:
                    module_path = str(file_path)
                
                task = Task(
                    id=self._generate_temp_id(task_phase, i),
                    phase=task_phase,
                    title=title,
                    module=module_path if file_path.exists() else None,
                    priority=self._infer_priority(title),
                    status=TaskStatus.TODO,
                    dependencies=[],
                    source_file=str(file_path),
                    line_number=i
                )
                
                tasks.append(task)
        
        return tasks
    
    def _generate_temp_id(self, phase: Optional[int], line: int) -> str:
        """Generate temporary task ID"""
        if phase:
            return f"P{phase:02d}-T{line:04d}"
        else:
            return f"ORPHAN-T{line:04d}"
    
    def _infer_priority(self, title: str) -> Priority:
        """Infer priority from title keywords"""
        title_lower = title.lower()
        
        # Check high priority keywords
        for keyword in self.config.high_priority_keywords:
            if keyword in title_lower:
                return Priority.HIGH
        
        # Check medium priority keywords
        for keyword in self.config.medium_priority_keywords:
            if keyword in title_lower:
                return Priority.MEDIUM
        
        return Priority.LOW

