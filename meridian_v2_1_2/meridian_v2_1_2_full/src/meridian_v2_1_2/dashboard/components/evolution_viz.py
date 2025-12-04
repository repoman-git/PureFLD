"""
Evolution Visualization Components

Plotly charts for genetic algorithm visualization.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Dict, Any


def plot_fitness_curve(history: List[Dict[str, Any]]) -> go.Figure:
    """
    Plot fitness evolution over generations.
    
    Shows best and mean fitness per generation.
    
    Args:
        history: List of generation history dicts
    
    Returns:
        Plotly Figure
    """
    generations = [h['generation'] for h in history]
    best_fitness = [h['best_fitness'] for h in history]
    mean_fitness = [h['mean_fitness'] for h in history]
    
    fig = go.Figure()
    
    # Best fitness line
    fig.add_trace(go.Scatter(
        x=generations,
        y=best_fitness,
        mode='lines+markers',
        name='Best Fitness',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    # Mean fitness line
    fig.add_trace(go.Scatter(
        x=generations,
        y=mean_fitness,
        mode='lines+markers',
        name='Population Mean',
        line=dict(color='blue', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Fitness Evolution Over Generations",
        xaxis_title="Generation",
        yaxis_title="Fitness Score",
        hovermode='x unified',
        template='plotly_white',
        height=450
    )
    
    return fig


def plot_population_scatter(
    population: List[Dict[str, Any]],
    x_metric: str = 'sharpe_ratio',
    y_metric: str = 'total_return'
) -> go.Figure:
    """
    Scatter plot of population in metric space.
    
    Visualizes trade-offs (e.g., Sharpe vs Return, Return vs Drawdown).
    
    Args:
        population: List of candidate dictionaries
        x_metric: Metric for x-axis
        y_metric: Metric for y-axis
    
    Returns:
        Plotly Figure
    """
    x_values = []
    y_values = []
    fitness_values = []
    labels = []
    
    for i, candidate in enumerate(population):
        metrics = candidate.get('metrics', {})
        x_values.append(metrics.get(x_metric, 0))
        y_values.append(metrics.get(y_metric, 0))
        fitness_values.append(candidate.get('fitness', 0))
        labels.append(f"Candidate {i+1}<br>Fitness: {candidate.get('fitness', 0):.2f}")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='markers',
        marker=dict(
            size=12,
            color=fitness_values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Fitness"),
            line=dict(width=1, color='white')
        ),
        text=labels,
        hovertemplate='%{text}<br>%{xaxis.title.text}: %{x:.3f}<br>%{yaxis.title.text}: %{y:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"Population Distribution: {x_metric.title()} vs {y_metric.title()}",
        xaxis_title=x_metric.replace('_', ' ').title(),
        yaxis_title=y_metric.replace('_', ' ').title(),
        template='plotly_white',
        height=500
    )
    
    return fig


def compare_best_equity_curves(
    curve0: List[float],
    curve_final: List[float],
    labels: tuple = ("Generation 0", "Final Generation")
) -> go.Figure:
    """
    Compare equity curves from first and last generation.
    
    Args:
        curve0: Equity curve from generation 0 best
        curve_final: Equity curve from final generation best
        labels: Tuple of (label0, label_final)
    
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # Generation 0 curve
    if curve0:
        fig.add_trace(go.Scatter(
            x=list(range(len(curve0))),
            y=curve0,
            mode='lines',
            name=labels[0],
            line=dict(color='lightblue', width=2, dash='dot')
        ))
    
    # Final generation curve
    if curve_final:
        fig.add_trace(go.Scatter(
            x=list(range(len(curve_final))),
            y=curve_final,
            mode='lines',
            name=labels[1],
            line=dict(color='green', width=3)
        ))
    
    fig.update_layout(
        title="Equity Curve Comparison: Evolution Progress",
        xaxis_title="Time Steps",
        yaxis_title="Equity ($)",
        hovermode='x unified',
        template='plotly_white',
        height=450
    )
    
    return fig


def plot_param_evolution(history: List[Dict[str, Any]], param_name: str) -> go.Figure:
    """
    Track how a specific parameter evolved over generations.
    
    Args:
        history: Evolution history
        param_name: Parameter to track
    
    Returns:
        Plotly Figure
    """
    generations = []
    param_values = []
    
    for h in history:
        if param_name in h.get('best_params', {}):
            generations.append(h['generation'])
            param_values.append(h['best_params'][param_name])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=generations,
        y=param_values,
        mode='lines+markers',
        name=param_name,
        line=dict(width=2),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title=f"Parameter Evolution: {param_name}",
        xaxis_title="Generation",
        yaxis_title=param_name.replace('_', ' ').title(),
        template='plotly_white',
        height=350
    )
    
    return fig


def plot_diversity_metric(history: List[Dict[str, Any]]) -> go.Figure:
    """
    Plot population diversity over generations.
    
    Uses standard deviation of fitness as diversity proxy.
    
    Args:
        history: Evolution history
    
    Returns:
        Plotly Figure
    """
    generations = [h['generation'] for h in history]
    diversity = [h.get('std_fitness', 0) for h in history]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=generations,
        y=diversity,
        mode='lines+markers',
        fill='tozeroy',
        name='Population Diversity',
        line=dict(color='purple', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Population Diversity Over Time",
        xaxis_title="Generation",
        yaxis_title="Fitness Std Dev",
        template='plotly_white',
        height=350
    )
    
    return fig


def create_evolution_dashboard(evolution_result: Dict[str, Any]) -> Dict[str, go.Figure]:
    """
    Create complete dashboard of evolution visualizations.
    
    Args:
        evolution_result: Evolution result dictionary
    
    Returns:
        Dictionary of figure name -> Plotly Figure
    """
    history = evolution_result.get('history', [])
    
    figures = {}
    
    # Fitness curve
    if history:
        figures['fitness_curve'] = plot_fitness_curve(history)
        figures['diversity'] = plot_diversity_metric(history)
    
    # Population scatter (if final population available)
    final_pop = evolution_result.get('final_population', [])
    if final_pop:
        # Convert to serializable format if needed
        pop_data = []
        for candidate in final_pop:
            if isinstance(candidate, dict):
                pop_data.append(candidate)
            else:
                # Dataclass, convert to dict
                pop_data.append({
                    'params': candidate.params if hasattr(candidate, 'params') else {},
                    'fitness': candidate.fitness if hasattr(candidate, 'fitness') else 0,
                    'metrics': candidate.metrics if hasattr(candidate, 'metrics') else {}
                })
        
        figures['population_scatter'] = plot_population_scatter(pop_data)
    
    return figures


