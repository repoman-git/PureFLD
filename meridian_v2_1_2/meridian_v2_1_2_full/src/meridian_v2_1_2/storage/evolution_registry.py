"""
Evolution Registry

Storage and retrieval for strategy evolution runs.
Tracks generations, candidates, and fitness history.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import shutil


# Registry location
REGISTRY_PATH = Path(__file__).parent.parent.parent.parent / "data" / "evolution_runs.json"


def save_evolution_run(evolution_data: Dict[str, Any]) -> bool:
    """
    Save evolution run to registry.
    
    Args:
        evolution_data: Evolution result dictionary
    
    Returns:
        True if successful
    """
    try:
        # Create backup if registry exists
        if REGISTRY_PATH.exists():
            backup_path = REGISTRY_PATH.with_suffix('.json.backup')
            shutil.copy(REGISTRY_PATH, backup_path)
        
        # Load existing runs
        runs = load_all_evolution_runs()
        
        # Add new run
        runs.append(evolution_data)
        
        # Ensure data directory exists
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        with open(REGISTRY_PATH, 'w') as f:
            json.dump(runs, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error saving evolution run: {e}")
        return False


def load_all_evolution_runs() -> List[Dict[str, Any]]:
    """
    Load all evolution runs from registry.
    
    Returns:
        List of evolution run dictionaries (sorted by timestamp, newest first)
    """
    try:
        if not REGISTRY_PATH.exists():
            return []
        
        with open(REGISTRY_PATH, 'r') as f:
            runs = json.load(f)
        
        # Sort by timestamp (newest first)
        runs.sort(key=lambda r: r.get('timestamp', ''), reverse=True)
        
        return runs
        
    except Exception as e:
        print(f"Error loading evolution runs: {e}")
        return []


def load_evolution_by_id(evolution_id: str) -> Optional[Dict[str, Any]]:
    """
    Load specific evolution run by ID.
    
    Args:
        evolution_id: Evolution run ID
    
    Returns:
        Evolution data or None if not found
    """
    runs = load_all_evolution_runs()
    
    for run in runs:
        if run.get('evolution_id') == evolution_id:
            return run
    
    return None


def delete_evolution_run(evolution_id: str) -> bool:
    """
    Delete evolution run from registry.
    
    Args:
        evolution_id: Evolution run ID to delete
    
    Returns:
        True if successful
    """
    try:
        runs = load_all_evolution_runs()
        
        # Filter out the run to delete
        filtered_runs = [r for r in runs if r.get('evolution_id') != evolution_id]
        
        if len(filtered_runs) == len(runs):
            return False  # Run not found
        
        # Save updated registry
        with open(REGISTRY_PATH, 'w') as f:
            json.dump(filtered_runs, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error deleting evolution run: {e}")
        return False


def get_evolution_stats() -> Dict[str, Any]:
    """
    Get summary statistics for evolution registry.
    
    Returns:
        Dictionary with stats
    """
    runs = load_all_evolution_runs()
    
    if not runs:
        return {
            'total_runs': 0,
            'total_generations': 0,
            'strategies': {}
        }
    
    # Count by strategy
    strategies = {}
    total_generations = 0
    
    for run in runs:
        strategy_name = run.get('strategy_name', 'Unknown')
        strategies[strategy_name] = strategies.get(strategy_name, 0) + 1
        total_generations += run.get('generations', 0)
    
    return {
        'total_runs': len(runs),
        'total_generations': total_generations,
        'strategies': strategies,
        'avg_generations': total_generations / len(runs) if runs else 0
    }


def get_best_evolved_params(strategy_name: str, n: int = 5) -> List[Dict[str, Any]]:
    """
    Get the best evolved parameter sets for a strategy.
    
    Args:
        strategy_name: Strategy to get params for
        n: Number of top param sets to return
    
    Returns:
        List of top parameter dictionaries with fitness scores
    """
    runs = load_all_evolution_runs()
    
    # Filter by strategy
    strategy_runs = [r for r in runs if r.get('strategy_name') == strategy_name]
    
    # Extract best candidates
    candidates = []
    for run in strategy_runs:
        best = run.get('best_candidate', {})
        if best:
            candidates.append({
                'params': best.get('params', {}),
                'fitness': best.get('fitness', 0),
                'metrics': best.get('metrics', {}),
                'evolution_id': run.get('evolution_id'),
                'timestamp': run.get('timestamp')
            })
    
    # Sort by fitness
    candidates.sort(key=lambda c: c['fitness'], reverse=True)
    
    return candidates[:n]


