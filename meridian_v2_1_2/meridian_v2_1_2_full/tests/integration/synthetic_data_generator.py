"""
Synthetic Data Generator for Testing

Generates realistic market data for integration tests.

This ensures tests use data that's sufficient for:
- Cycle analysis (needs 200+ bars)
- Regime classification (needs 250+ bars)
- Volatility modeling (needs rolling windows)
- Portfolio optimization

Author: Meridian Team
Date: December 4, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple


class SyntheticDataGenerator:
    """
    Generate realistic synthetic market data for testing.
    
    Data includes:
    - Cyclical patterns (simulating Hurst cycles)
    - Trend components
    - Volatility clustering
    - Realistic price levels
    
    Example:
        >>> gen = SyntheticDataGenerator(seed=42)
        >>> prices = gen.generate_price_series(n_bars=250, base_price=1800)
        >>> multi = gen.generate_multi_asset(assets=['SPY', 'TLT'], n_bars=250)
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)
    
    def generate_price_series(
        self,
        n_bars: int = 250,
        base_price: float = 1800,
        cycle_amplitude: float = 15,
        trend: float = 0.05,
        noise: float = 1.5
    ) -> pd.Series:
        """
        Generate a single price series with cycle characteristics.
        
        Args:
            n_bars: Number of bars (minimum 200 recommended)
            base_price: Starting price level
            cycle_amplitude: Amplitude of cyclical component
            trend: Trend slope (0.05 = 5% drift)
            noise: Random noise level
            
        Returns:
            Price series with realistic cycle patterns
        """
        if n_bars < 200:
            print(f"⚠️  Warning: {n_bars} bars may be too few for cycle analysis (recommend 200+)")
        
        # Create date index
        index = pd.date_range("2020-01-01", periods=n_bars, freq='D')
        
        # Cyclical component (multiple harmonics)
        t = np.linspace(0, 20 * np.pi, n_bars)
        cycle = (
            cycle_amplitude * np.sin(t) +              # Dominant cycle
            cycle_amplitude * 0.5 * np.sin(t * 2) +   # First harmonic
            cycle_amplitude * 0.25 * np.sin(t * 0.5)  # Longer cycle
        )
        
        # Trend component
        trend_component = np.linspace(0, base_price * trend, n_bars)
        
        # Noise
        noise_component = np.random.normal(0, noise, n_bars)
        
        # Combine
        price = base_price + cycle + trend_component + noise_component
        
        return pd.Series(price, index=index)
    
    def generate_multi_asset(
        self,
        assets: list,
        n_bars: int = 250,
        correlations: Dict[Tuple[str, str], float] = None
    ) -> Dict[str, pd.Series]:
        """
        Generate multiple correlated asset series.
        
        Args:
            assets: List of asset symbols
            n_bars: Number of bars
            correlations: Optional correlation structure
            
        Returns:
            Dictionary of {symbol: price_series}
        """
        price_dict = {}
        base_prices = {
            'SPY': 400,
            'QQQ': 350,
            'TLT': 110,
            'GLD': 180,
            'SLV': 24,
            'USO': 70,
            'DXY': 102
        }
        
        for i, symbol in enumerate(assets):
            base = base_prices.get(symbol, 100)
            
            # Vary parameters slightly for each asset
            cycle_amp = 10 + i * 2
            trend = 0.03 + i * 0.01
            noise = 1.0 + i * 0.3
            
            # Add phase shift for some correlation structure
            phase_shift = i * 0.2 * np.pi
            
            index = pd.date_range("2020-01-01", periods=n_bars, freq='D')
            t = np.linspace(0, 20 * np.pi, n_bars) + phase_shift
            
            cycle = (
                cycle_amp * np.sin(t) +
                cycle_amp * 0.4 * np.sin(t * 2)
            )
            
            trend_comp = np.linspace(0, base * trend, n_bars)
            noise_comp = np.random.normal(0, noise, n_bars)
            
            price = base + cycle + trend_comp + noise_comp
            price_dict[symbol] = pd.Series(price, index=index)
        
        return price_dict
    
    def generate_with_regime_shifts(
        self,
        n_bars: int = 300,
        base_price: float = 1800
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Generate price series with clear regime shifts.
        
        Returns:
            (prices, regime_labels)
        """
        index = pd.date_range("2020-01-01", periods=n_bars, freq='D')
        
        # Create regime structure
        regime_length = n_bars // 4
        regimes = []
        prices = []
        
        t_start = 0
        for i in range(4):
            # Alternate between trending and cyclical
            if i % 2 == 0:
                # Cyclical regime
                t = np.linspace(0, 5 * np.pi, regime_length)
                segment = 20 * np.sin(t) + np.random.normal(0, 1, regime_length)
                regimes.extend([1] * regime_length)  # CYCLICAL
            else:
                # Trending regime
                segment = np.linspace(0, 30, regime_length) + np.random.normal(0, 2, regime_length)
                regimes.extend([0] * regime_length)  # TRENDING
            
            prices.extend(segment)
            t_start += regime_length
        
        # Pad if needed
        if len(prices) < n_bars:
            diff = n_bars - len(prices)
            prices.extend([0] * diff)
            regimes.extend([1] * diff)
        
        price_series = pd.Series(base_price + np.array(prices[:n_bars]), index=index)
        regime_series = pd.Series(regimes[:n_bars], index=index)
        
        return price_series, regime_series


# Convenience instance
generator = SyntheticDataGenerator()

