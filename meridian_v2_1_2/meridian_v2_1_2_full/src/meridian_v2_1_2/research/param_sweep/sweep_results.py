"""
Sweep Results Handler for Meridian v2.1.2

Stores, analyzes, and exports parameter sweep results.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

from .sweep_config import SweepConfig


class SweepResults:
    """
    Stores and analyzes parameter sweep results.
    
    Provides ranking, filtering, and export capabilities.
    """
    
    def __init__(self, config: SweepConfig):
        """
        Initialize sweep results.
        
        Args:
            config: SweepConfig instance
        """
        self.config = config
        self.results: List[Dict[str, Any]] = []
    
    def add_result(self, params: Dict[str, Any], metrics: Dict[str, float]):
        """
        Add result from single run.
        
        Args:
            params: Parameter dictionary
            metrics: Performance metrics
        """
        result = {**params, **metrics}
        self.results.append(result)
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get results as pandas DataFrame"""
        return pd.DataFrame(self.results)
    
    def rank_by_metric(self, metric: str = None, ascending: bool = False) -> pd.DataFrame:
        """
        Rank results by metric.
        
        Args:
            metric: Metric to rank by (default: primary_metric from config)
            ascending: Sort order
        
        Returns:
            Sorted DataFrame
        """
        if metric is None:
            metric = self.config.primary_metric
        
        df = self.get_dataframe()
        
        if metric not in df.columns:
            raise ValueError(f"Metric {metric} not found in results")
        
        return df.sort_values(by=metric, ascending=ascending)
    
    def get_top_n(self, n: int = 10, metric: str = None) -> pd.DataFrame:
        """
        Get top N parameter sets.
        
        Args:
            n: Number of results to return
            metric: Metric to rank by
        
        Returns:
            Top N results
        """
        ranked = self.rank_by_metric(metric=metric, ascending=False)
        return ranked.head(n)
    
    def get_best_params(self, metric: str = None) -> Dict[str, Any]:
        """
        Get best parameter set.
        
        Args:
            metric: Metric to optimize
        
        Returns:
            Best parameter dictionary
        """
        ranked = self.rank_by_metric(metric=metric, ascending=False)
        return ranked.iloc[0].to_dict()
    
    def summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics"""
        df = self.get_dataframe()
        
        metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']
        
        stats = {}
        for metric in metrics:
            if metric in df.columns:
                stats[metric] = {
                    'mean': float(df[metric].mean()),
                    'std': float(df[metric].std()),
                    'min': float(df[metric].min()),
                    'max': float(df[metric].max()),
                    'median': float(df[metric].median())
                }
        
        return stats
    
    def export(self, output_dir: str = None):
        """
        Export results to files.
        
        Args:
            output_dir: Output directory path
        """
        if output_dir is None:
            output_dir = self.config.output_dir
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export full results
        df = self.get_dataframe()
        df.to_csv(output_path / 'sweep_results.csv', index=False)
        
        # Export top N
        top_n = self.get_top_n(n=self.config.save_top_n)
        top_n.to_csv(output_path / 'top_results.csv', index=False)
        
        # Export best params
        best = self.get_best_params()
        with open(output_path / 'best_params.json', 'w') as f:
            json.dump(best, f, indent=2)
        
        # Export summary
        stats = self.summary_statistics()
        with open(output_path / 'summary_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Results exported to: {output_path}")
        print(f"   - sweep_results.csv ({len(df)} rows)")
        print(f"   - top_results.csv ({len(top_n)} rows)")
        print(f"   - best_params.json")
        print(f"   - summary_stats.json")

