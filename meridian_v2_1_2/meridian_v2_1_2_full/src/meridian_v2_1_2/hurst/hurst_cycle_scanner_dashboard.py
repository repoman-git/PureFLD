"""
Cycle Scanner Dashboard (Plotly)

Interactive heatmap showing cycle strength across multiple instruments.
Identifies cross-instrument cycle synchronization.
"""

import plotly.graph_objs as go


def plot_cycle_scanner(scan_results, title="Cycle Scanner Dashboard"):
    """
    Create heatmap of cycle strength across instruments.
    
    Args:
        scan_results: Results from CycleScanner.scan()
        title: Dashboard title
    
    Returns:
        Plotly figure
    
    Example:
        >>> from meridian_v2_1_2.hurst import CycleScanner
        >>> from meridian_v2_1_2.hurst.hurst_cycle_scanner_dashboard import plot_cycle_scanner
        >>> 
        >>> scanner = CycleScanner()
        >>> results = scanner.scan(price_dict)
        >>> 
        >>> fig = plot_cycle_scanner(results)
        >>> fig.show()
    """
    cycles = sorted({
        c for sym in scan_results for (c, _) in scan_results[sym]["ranked_cycles"]
    })

    symbols = list(scan_results.keys())

    # Build matrix of cycle scores
    matrix = []
    for sym in symbols:
        row = []
        res = scan_results[sym]
        cycle_score = {c: s for (c, s) in res["ranked_cycles"]}

        for c in cycles:
            row.append(cycle_score.get(c, 0))
        matrix.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=cycles,
        y=symbols,
        colorscale="Viridis",
        colorbar=dict(title="Cycle Strength"),
        hovertemplate='Symbol: %{y}<br>Cycle: %{x} days<br>Strength: %{z:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Cycle Length (days)",
        yaxis_title="Symbol",
        height=700,
        template="plotly_white"
    )

    return fig


def plot_synchrony_network(synchrony_map, min_symbols=2, title="Cycle Synchronization Network"):
    """
    Visualize cycle synchronization across instruments.
    
    Shows which cycles are shared by multiple instruments.
    
    Args:
        synchrony_map: Results from CycleScanner.synchrony_map()
        min_symbols: Minimum number of symbols to show cycle
        title: Chart title
    
    Returns:
        Plotly figure
    """
    # Filter to cycles shared by multiple instruments
    shared_cycles = {
        cycle: symbols 
        for cycle, symbols in synchrony_map.items() 
        if len(symbols) >= min_symbols
    }
    
    if not shared_cycles:
        return None
    
    # Create bar chart of synchronized cycles
    cycles = []
    counts = []
    avg_scores = []
    
    for cycle, symbols in sorted(shared_cycles.items()):
        cycles.append(cycle)
        counts.append(len(symbols))
        avg_scores.append(np.mean([score for _, score in symbols]))
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=cycles,
        y=counts,
        marker=dict(
            color=avg_scores,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Avg Strength")
        ),
        hovertemplate='Cycle: %{x} days<br>Instruments: %{y}<br>Avg Strength: %{marker.color:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Cycle Period (days)",
        yaxis_title="Number of Instruments Sharing Cycle",
        template="plotly_white",
        height=500
    )
    
    return fig


