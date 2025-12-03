"""
Backtest Registry

JSON-based storage for backtest run history and results.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil

# Registry file location
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
REGISTRY_DIR = PROJECT_ROOT / "data"
REGISTRY_FILE = REGISTRY_DIR / "backtest_runs.json"


def _ensure_registry_exists():
    """Ensure registry directory and file exist"""
    REGISTRY_DIR.mkdir(exist_ok=True)
    if not REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, 'w') as f:
            json.dump({"runs": [], "metadata": {"created": datetime.now().isoformat()}}, f, indent=2)


def _load_registry() -> Dict:
    """Load the entire registry"""
    _ensure_registry_exists()
    try:
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading registry: {e}")
        return {"runs": [], "metadata": {}}


def _save_registry(registry: Dict):
    """Save the entire registry"""
    _ensure_registry_exists()
    try:
        # Create backup
        if REGISTRY_FILE.exists():
            backup_file = REGISTRY_DIR / f"backtest_runs_backup.json"
            shutil.copy(REGISTRY_FILE, backup_file)
        
        # Save new version
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(registry, f, indent=2)
    except Exception as e:
        print(f"Error saving registry: {e}")


def save_run(result: Dict[str, Any]) -> bool:
    """
    Save a backtest run to the registry.
    
    Args:
        result: Dictionary containing run results (from BacktestResult.to_dict())
    
    Returns:
        bool: Success status
    """
    try:
        registry = _load_registry()
        
        # Add run to registry
        run_entry = {
            'run_id': result.get('run_id'),
            'timestamp': result.get('timestamp'),
            'strategy_name': result.get('strategy_name'),
            'params': result.get('params', {}),
            'metrics': result.get('metrics', {}),
            'success': result.get('success', False),
            'error': result.get('error'),
            'num_trades': len(result.get('trades', [])),
            # Store summary equity curve (first, last, min, max)
            'equity_summary': {
                'initial': result['equity_curve'][0] if result.get('equity_curve') else 0,
                'final': result['equity_curve'][-1] if result.get('equity_curve') else 0,
                'peak': max(result.get('equity_curve', [0])),
                'trough': min(result.get('equity_curve', [0]))
            }
        }
        
        registry['runs'].append(run_entry)
        registry['metadata']['last_updated'] = datetime.now().isoformat()
        registry['metadata']['total_runs'] = len(registry['runs'])
        
        _save_registry(registry)
        return True
        
    except Exception as e:
        print(f"Error saving run: {e}")
        return False


def load_all_runs() -> List[Dict[str, Any]]:
    """
    Load all backtest runs from the registry.
    
    Returns:
        List of run dictionaries, sorted by timestamp (newest first)
    """
    try:
        registry = _load_registry()
        runs = registry.get('runs', [])
        
        # Sort by timestamp (newest first)
        runs_sorted = sorted(
            runs,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )
        
        return runs_sorted
        
    except Exception as e:
        print(f"Error loading runs: {e}")
        return []


def load_run_by_id(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Load a specific run by its ID.
    
    Args:
        run_id: Unique run identifier
    
    Returns:
        Run dictionary or None if not found
    """
    try:
        runs = load_all_runs()
        for run in runs:
            if run.get('run_id') == run_id:
                return run
        return None
        
    except Exception as e:
        print(f"Error loading run {run_id}: {e}")
        return None


def delete_run(run_id: str) -> bool:
    """
    Delete a run from the registry.
    
    Args:
        run_id: Unique run identifier
    
    Returns:
        bool: Success status
    """
    try:
        registry = _load_registry()
        
        # Filter out the run to delete
        original_count = len(registry['runs'])
        registry['runs'] = [r for r in registry['runs'] if r.get('run_id') != run_id]
        
        if len(registry['runs']) < original_count:
            registry['metadata']['last_updated'] = datetime.now().isoformat()
            registry['metadata']['total_runs'] = len(registry['runs'])
            _save_registry(registry)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error deleting run {run_id}: {e}")
        return False


def get_registry_stats() -> Dict[str, Any]:
    """
    Get summary statistics about the registry.
    
    Returns:
        Dictionary with stats
    """
    try:
        registry = _load_registry()
        runs = registry.get('runs', [])
        
        if not runs:
            return {
                'total_runs': 0,
                'successful_runs': 0,
                'failed_runs': 0,
                'strategies': {},
                'date_range': None
            }
        
        successful = sum(1 for r in runs if r.get('success', False))
        failed = len(runs) - successful
        
        # Count strategies
        strategies = {}
        for run in runs:
            strat = run.get('strategy_name', 'Unknown')
            strategies[strat] = strategies.get(strat, 0) + 1
        
        # Date range
        timestamps = [r.get('timestamp', '') for r in runs if r.get('timestamp')]
        date_range = None
        if timestamps:
            date_range = {
                'earliest': min(timestamps),
                'latest': max(timestamps)
            }
        
        return {
            'total_runs': len(runs),
            'successful_runs': successful,
            'failed_runs': failed,
            'strategies': strategies,
            'date_range': date_range,
            'registry_file': str(REGISTRY_FILE)
        }
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {'error': str(e)}


def search_runs(
    strategy_name: Optional[str] = None,
    min_sharpe: Optional[float] = None,
    success_only: bool = True
) -> List[Dict[str, Any]]:
    """
    Search runs with filters.
    
    Args:
        strategy_name: Filter by strategy
        min_sharpe: Minimum Sharpe ratio
        success_only: Only show successful runs
    
    Returns:
        Filtered list of runs
    """
    runs = load_all_runs()
    
    filtered = runs
    
    if strategy_name:
        filtered = [r for r in filtered if r.get('strategy_name') == strategy_name]
    
    if success_only:
        filtered = [r for r in filtered if r.get('success', False)]
    
    if min_sharpe is not None:
        filtered = [r for r in filtered if r.get('metrics', {}).get('sharpe_ratio', 0) >= min_sharpe]
    
    return filtered

