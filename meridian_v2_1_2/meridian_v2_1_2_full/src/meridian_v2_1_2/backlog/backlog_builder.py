"""
Backlog Builder for Meridian v2.1.2

Orchestrates task extraction and registry population.
"""

from pathlib import Path
from typing import List

from .backlog_config import BacklogConfig
from .backlog_parser import BacklogParser
from .backlog_registry import BacklogRegistry


class BacklogBuilder:
    """
    Orchestrates backlog construction.
    
    Pipeline:
    1. Scan configured paths
    2. Parse tasks from each file
    3. Add to registry
    4. Generate backlog model
    """
    
    def __init__(self, config: BacklogConfig = None):
        """
        Initialize backlog builder.
        
        Args:
            config: Optional BacklogConfig
        """
        self.config = config or BacklogConfig()
        self.parser = BacklogParser(self.config)
        self.registry = BacklogRegistry()
    
    def build(self) -> BacklogRegistry:
        """
        Build complete backlog.
        
        Returns:
            Populated BacklogRegistry
        """
        # Scan all configured paths
        for scan_path in self.config.scan_paths:
            path = Path(scan_path)
            
            if not path.exists():
                continue
            
            # Walk directory
            if path.is_dir():
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        self._process_file(file_path)
            elif path.is_file():
                self._process_file(path)
        
        return self.registry
    
    def _process_file(self, file_path: Path):
        """Process single file"""
        # Skip certain files
        if self._should_skip(file_path):
            return
        
        try:
            tasks = self.parser.parse_file(file_path)
            
            for task in tasks:
                self.registry.add_task(task)
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        # Skip hidden files
        if file_path.name.startswith('.'):
            return True
        
        # Skip __pycache__
        if '__pycache__' in file_path.parts:
            return True
        
        # Skip .pyc files
        if file_path.suffix == '.pyc':
            return True
        
        # Skip large binary files
        if file_path.suffix in ['.db', '.sqlite', '.pkl', '.npy']:
            return True
        
        return False

