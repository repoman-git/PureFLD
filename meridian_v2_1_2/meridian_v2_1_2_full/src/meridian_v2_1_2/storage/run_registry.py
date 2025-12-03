"""
Run Registry for Meridian v2.1.2

Tracks every system run with versioned metadata.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import subprocess


class RunRegistry:
    """
    Registry for tracking system runs.
    
    Each run gets a unique ID and comprehensive metadata:
    - Timestamp
    - Strategy version
    - Config snapshot
    - Git hash
    - Performance summary
    - Warnings
    - Model risk score
    """
    
    def __init__(self, runs_dir: str = "runs"):
        """
        Initialize run registry.
        
        Args:
            runs_dir: Directory for run logs
        """
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
    
    def log_run(
        self,
        run_type: str,
        config: Dict[str, Any],
        performance: Optional[Dict[str, float]] = None,
        warnings: Optional[list] = None,
        model_risk_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a system run.
        
        Args:
            run_type: Type of run (research/paper/live)
            config: Configuration snapshot
            performance: Performance metrics
            warnings: List of warnings
            model_risk_score: Model risk rating
            metadata: Additional metadata
        
        Returns:
            Run ID
        """
        # Generate run ID with microseconds to ensure uniqueness
        timestamp = datetime.now()
        run_id = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        
        # Get git hash if available
        git_hash = self._get_git_hash()
        
        # Build run record
        run_record = {
            'run_id': run_id,
            'timestamp': timestamp.isoformat(),
            'run_type': run_type,
            'git_hash': git_hash,
            'config': config,
            'performance': performance or {},
            'warnings': warnings or [],
            'model_risk_score': model_risk_score,
            'metadata': metadata or {}
        }
        
        # Save run log
        log_file = self.runs_dir / f"{run_id}-run.json"
        with open(log_file, 'w') as f:
            json.dump(run_record, f, indent=2, default=str)
        
        return run_id
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve run record.
        
        Args:
            run_id: Run ID
        
        Returns:
            Run record dict or None
        """
        log_file = self.runs_dir / f"{run_id}-run.json"
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def list_runs(
        self,
        run_type: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        List recent runs.
        
        Args:
            run_type: Filter by run type
            limit: Maximum number to return
        
        Returns:
            List of run records
        """
        run_files = sorted(self.runs_dir.glob("*-run.json"), reverse=True)
        
        runs = []
        for run_file in run_files[:limit]:
            with open(run_file, 'r') as f:
                run_record = json.load(f)
                
                if run_type is None or run_record.get('run_type') == run_type:
                    runs.append(run_record)
        
        return runs
    
    def _get_git_hash(self) -> Optional[str]:
        """Get current git commit hash if available"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None


def log_run(
    run_type: str,
    config: Dict[str, Any],
    performance: Optional[Dict[str, float]] = None,
    **kwargs
) -> str:
    """
    Convenience function to log a run.
    
    Args:
        run_type: Run type
        config: Config dict
        performance: Performance metrics
        **kwargs: Additional arguments
    
    Returns:
        Run ID
    """
    registry = RunRegistry()
    return registry.log_run(run_type, config, performance, **kwargs)

