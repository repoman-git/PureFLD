"""Evolution Dashboard"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_strategy_evolution_dashboard(fitness_history, title="Strategy Evolution Progress"):
    """Plot fitness evolution over generations"""
    fig = make_subplots(rows=1, cols=1, subplot_titles=["Fitness Over Generations"])
    
    fig.add_trace(go.Scatter(
        x=list(range(len(fitness_history))),
        y=fitness_history,
        mode="lines+markers",
        name="Best Fitness",
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(height=500, title=title, template="plotly_white",
                     xaxis_title="Generation", yaxis_title="Fitness Score")
    fig.show()

