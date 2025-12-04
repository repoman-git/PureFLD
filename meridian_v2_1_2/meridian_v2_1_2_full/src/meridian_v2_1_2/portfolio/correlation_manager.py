"""
Correlation Management for Meridian v2.1.2

Manage portfolio risk through correlation awareness.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

from ..config import PortfolioConfig


def compute_correlation_matrix(
    prices: Dict[str, pd.Series],
    lookback: int = 90
) -> pd.DataFrame:
    """
    Compute rolling correlation matrix for assets.
    
    Args:
        prices: Dictionary of price series
        lookback: Rolling window for correlation
    
    Returns:
        pd.DataFrame: Correlation matrix (latest values)
    """
    # Align all price series to common index
    price_df = pd.DataFrame(prices)
    
    # Compute returns
    returns = price_df.pct_change().fillna(0)
    
    # Compute correlation on recent data
    if len(returns) < lookback:
        lookback = len(returns)
    
    recent_returns = returns.iloc[-lookback:]
    corr_matrix = recent_returns.corr()
    
    return corr_matrix


def manage_correlation_risk(
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series],
    config: PortfolioConfig
) -> Dict[str, pd.Series]:
    """
    Manage correlation risk by reducing weights of highly correlated positions.
    
    If two assets are highly correlated (>max_correlation), reduces their combined weight.
    
    Args:
        positions: Position sizes per symbol
        prices: Prices per symbol
        config: Portfolio configuration
    
    Returns:
        Dict[str, pd.Series]: Correlation-adjusted positions
    """
    if not config.use_correlation_matrix or len(positions) < 2:
        return positions
    
    # Compute correlation matrix
    corr_matrix = compute_correlation_matrix(prices, config.correlation_lookback)
    
    # Find highly correlated pairs
    high_corr_pairs = _find_high_correlation_pairs(corr_matrix, config.max_correlation)
    
    if len(high_corr_pairs) == 0:
        return positions  # No action needed
    
    # Reduce weights of correlated assets
    adjusted = positions.copy()
    
    for symbol1, symbol2, corr in high_corr_pairs:
        # Reduce both by factor based on correlation strength
        reduction_factor = 1.0 - (corr - config.max_correlation) / (1.0 - config.max_correlation)
        reduction_factor = max(0.5, reduction_factor)  # Don't reduce below 50%
        
        if symbol1 in adjusted:
            adjusted[symbol1] = adjusted[symbol1] * reduction_factor
        if symbol2 in adjusted:
            adjusted[symbol2] = adjusted[symbol2] * reduction_factor
    
    return adjusted


def _find_high_correlation_pairs(
    corr_matrix: pd.DataFrame,
    threshold: float
) -> List[Tuple[str, str, float]]:
    """
    Find pairs of assets with correlation above threshold.
    
    Returns:
        List of tuples: [(symbol1, symbol2, correlation), ...]
    """
    pairs = []
    
    symbols = corr_matrix.columns.tolist()
    
    for i, sym1 in enumerate(symbols):
        for j, sym2 in enumerate(symbols):
            if i >= j:  # Skip diagonal and duplicates
                continue
            
            corr = corr_matrix.loc[sym1, sym2]
            
            if abs(corr) > threshold:
                pairs.append((sym1, sym2, corr))
    
    return pairs


