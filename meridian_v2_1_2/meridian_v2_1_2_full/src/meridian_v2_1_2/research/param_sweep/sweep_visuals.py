"""
Sweep Visualizations for Meridian v2.1.2

Creates charts and heatmaps for parameter sweep analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

from .sweep_results import SweepResults


class SweepVisualizer:
    """
    Creates visualizations for parameter sweep results.
    
    Generates:
    - Parameter vs metric scatter plots
    - Heatmaps
    - Distribution plots
    - Pareto frontiers
    """
    
    def __init__(self, results: SweepResults):
        """
        Initialize visualizer.
        
        Args:
            results: SweepResults instance
        """
        self.results = results
        self.df = results.get_dataframe()
    
    def plot_parameter_vs_metric(
        self,
        param: str,
        metric: str = 'sharpe_ratio',
        figsize: tuple = (10, 6)
    ):
        """
        Plot parameter vs metric scatter.
        
        Args:
            param: Parameter name
            metric: Metric name
            figsize: Figure size
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.scatter(self.df[param], self.df[metric], alpha=0.6, s=50)
        ax.set_xlabel(param)
        ax.set_ylabel(metric)
        ax.set_title(f'{metric} vs {param}')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_heatmap(
        self,
        param_x: str,
        param_y: str,
        metric: str = 'sharpe_ratio',
        figsize: tuple = (10, 8)
    ):
        """
        Plot parameter heatmap.
        
        Args:
            param_x: X-axis parameter
            param_y: Y-axis parameter
            metric: Metric for heatmap values
            figsize: Figure size
        """
        # Pivot data
        pivot = self.df.pivot_table(
            values=metric,
            index=param_y,
            columns=param_x,
            aggfunc='mean'
        )
        
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.3f',
            cmap='RdYlGn',
            ax=ax,
            cbar_kws={'label': metric}
        )
        
        ax.set_title(f'{metric} Heatmap: {param_x} vs {param_y}')
        
        plt.tight_layout()
        return fig
    
    def plot_metric_distribution(
        self,
        metric: str = 'sharpe_ratio',
        figsize: tuple = (10, 6)
    ):
        """
        Plot metric distribution.
        
        Args:
            metric: Metric name
            figsize: Figure size
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.hist(self.df[metric], bins=30, alpha=0.7, edgecolor='black')
        ax.axvline(self.df[metric].mean(), color='red', linestyle='--', 
                   label=f'Mean: {self.df[metric].mean():.3f}')
        ax.set_xlabel(metric)
        ax.set_ylabel('Frequency')
        ax.set_title(f'{metric} Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_pareto_frontier(
        self,
        metric_x: str = 'total_return',
        metric_y: str = 'max_drawdown',
        figsize: tuple = (10, 6)
    ):
        """
        Plot Pareto frontier.
        
        Args:
            metric_x: X-axis metric (to maximize)
            metric_y: Y-axis metric (to minimize, shown as negative)
            figsize: Figure size
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Scatter all points
        ax.scatter(
            self.df[metric_x],
            -self.df[metric_y],  # Negate drawdown for visualization
            alpha=0.5,
            s=50,
            label='All runs'
        )
        
        # Find Pareto frontier
        # (maximize return, minimize drawdown = maximize -drawdown)
        pareto_points = []
        for i, row in self.df.iterrows():
            is_pareto = True
            for j, other in self.df.iterrows():
                if i != j:
                    if (other[metric_x] >= row[metric_x] and 
                        other[metric_y] <= row[metric_y] and
                        (other[metric_x] > row[metric_x] or other[metric_y] < row[metric_y])):
                        is_pareto = False
                        break
            if is_pareto:
                pareto_points.append(i)
        
        if pareto_points:
            pareto_df = self.df.loc[pareto_points]
            ax.scatter(
                pareto_df[metric_x],
                -pareto_df[metric_y],
                color='red',
                s=100,
                marker='*',
                label='Pareto frontier',
                zorder=5
            )
        
        ax.set_xlabel(metric_x)
        ax.set_ylabel(f'-{metric_y}')
        ax.set_title('Pareto Frontier')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_summary_report(self, output_dir: str = None):
        """
        Create comprehensive visual report.
        
        Args:
            output_dir: Output directory for plots
        """
        if output_dir is None:
            output_dir = self.results.config.output_dir
        
        output_path = Path(output_dir) / 'charts'
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Distribution plots
        for metric in ['sharpe_ratio', 'total_return', 'max_drawdown']:
            if metric in self.df.columns:
                fig = self.plot_metric_distribution(metric)
                fig.savefig(output_path / f'{metric}_distribution.png', dpi=150)
                plt.close(fig)
        
        # Pareto frontier
        fig = self.plot_pareto_frontier()
        fig.savefig(output_path / 'pareto_frontier.png', dpi=150)
        plt.close(fig)
        
        print(f"✅ Charts saved to: {output_path}")


