"""
Pairs Selector

Identifies tradable pairs based on cycle synchronization and correlation.

Logic:
1. Compute cycle correlation between all pairs
2. Identify lead/lag relationships
3. Filter for sufficient liquidity and volatility
4. Rank pairs by cycle stability and tradability

Key Metrics:
- Cycle correlation (Pearson on cycle phase)
- Lead/lag offset (time shift that maximizes correlation)
- Spread volatility (for position sizing)
- Mean reversion half-life (optimal holding period)

Author: Meridian Team
Date: December 4, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats, signal
from ..hurst.intermarket_engine import IntermarketCycleEngine
from ..hurst.hurst_phasing import HurstPhasingEngine


@dataclass
class PairCandidate:
    """Container for a pair trading candidate"""
    lead_asset: str
    lag_asset: str
    correlation: float
    lead_lag_days: int
    spread_volatility: float
    half_life: float
    score: float
    
    def __repr__(self):
        return (f"PairCandidate({self.lead_asset}/{self.lag_asset}, "
                f"corr={self.correlation:.3f}, lag={self.lead_lag_days}, "
                f"score={self.score:.3f})")


class PairsSelector:
    """
    Selects tradable pairs based on cycle synchronization.
    
    The selector analyzes cycle relationships between instruments and identifies
    pairs that:
    - Have high cycle correlation (> 0.6)
    - Show consistent lead/lag relationships
    - Have mean-reverting spread characteristics
    - Are liquid enough for trading
    
    Example:
        >>> selector = PairsSelector(min_correlation=0.6)
        >>> price_dict = {
        ...     'GLD': gold_prices,
        ...     'SLV': silver_prices,
        ...     'TLT': treasury_prices,
        ...     'DXY': dollar_prices
        ... }
        >>> pairs = selector.select_pairs(price_dict, top_n=5)
        >>> for pair in pairs:
        ...     print(pair)
    """
    
    def __init__(
        self,
        min_correlation: float = 0.6,
        max_lead_lag_days: int = 10,
        min_half_life: float = 5,
        max_half_life: float = 60,
        cycle_periods: List[int] = [20, 40, 80]
    ):
        """
        Initialize pairs selector.
        
        Args:
            min_correlation: Minimum cycle correlation to consider
            max_lead_lag_days: Maximum lead/lag to consider (days)
            min_half_life: Minimum mean reversion half-life (days)
            max_half_life: Maximum mean reversion half-life (days)
            cycle_periods: Cycle periods to analyze
        """
        self.min_correlation = min_correlation
        self.max_lead_lag_days = max_lead_lag_days
        self.min_half_life = min_half_life
        self.max_half_life = max_half_life
        self.cycle_periods = cycle_periods
        
        self.intermarket_engine = IntermarketCycleEngine(cycle_periods=cycle_periods)
        self.phasing_engine = HurstPhasingEngine(nominal_periods=cycle_periods)
    
    def select_pairs(
        self,
        price_dict: Dict[str, pd.Series],
        top_n: int = 10
    ) -> List[PairCandidate]:
        """
        Select top N tradable pairs from price dictionary.
        
        Args:
            price_dict: Dictionary mapping symbol -> price series
            top_n: Number of top pairs to return
            
        Returns:
            List of PairCandidate objects, sorted by score (best first)
        """
        # Step 1: Compute cycle phases for all instruments
        phases = self._compute_cycle_phases(price_dict)
        
        # Step 2: Compute pairwise relationships
        candidates = []
        symbols = list(price_dict.keys())
        
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                candidate = self._analyze_pair(
                    sym1, sym2,
                    phases[sym1], phases[sym2],
                    price_dict[sym1], price_dict[sym2]
                )
                
                if candidate and candidate.score > 0:
                    candidates.append(candidate)
        
        # Step 3: Sort by score and return top N
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:top_n]
    
    def _compute_cycle_phases(
        self,
        price_dict: Dict[str, pd.Series]
    ) -> Dict[str, pd.DataFrame]:
        """
        Compute cycle phases for all instruments.
        
        Returns:
            Dictionary mapping symbol -> DataFrame with phase columns
        """
        phases = {}
        
        for symbol, prices in price_dict.items():
            phase_results = {}
            
            for period in self.cycle_periods:
                try:
                    result = self.phasing_engine.compute_phase(prices, period)
                    phase_results[f'phase_{period}'] = result.get('phase', pd.Series(0, index=prices.index))
                except Exception as e:
                    # Fallback to zero phase if computation fails
                    phase_results[f'phase_{period}'] = pd.Series(0, index=prices.index)
            
            phases[symbol] = pd.DataFrame(phase_results)
        
        return phases
    
    def _analyze_pair(
        self,
        sym1: str,
        sym2: str,
        phases1: pd.DataFrame,
        phases2: pd.DataFrame,
        prices1: pd.Series,
        prices2: pd.Series
    ) -> Optional[PairCandidate]:
        """
        Analyze a single pair for tradability.
        
        Returns:
            PairCandidate if pair meets criteria, None otherwise
        """
        # Align indices
        common_idx = phases1.index.intersection(phases2.index)
        if len(common_idx) < 100:
            return None
        
        phases1 = phases1.loc[common_idx]
        phases2 = phases2.loc[common_idx]
        prices1 = prices1.loc[common_idx]
        prices2 = prices2.loc[common_idx]
        
        # Compute average phase correlation across all cycle periods
        correlations = []
        lead_lags = []
        
        for col in phases1.columns:
            if col in phases2.columns:
                corr, lag = self._compute_lead_lag(
                    phases1[col].values,
                    phases2[col].values
                )
                correlations.append(corr)
                lead_lags.append(lag)
        
        if not correlations:
            return None
        
        avg_correlation = np.mean(correlations)
        avg_lead_lag = int(np.median(lead_lags))
        
        # Filter by correlation threshold
        if avg_correlation < self.min_correlation:
            return None
        
        if abs(avg_lead_lag) > self.max_lead_lag_days:
            return None
        
        # Determine lead/lag relationship
        if avg_lead_lag > 0:
            lead_asset, lag_asset = sym1, sym2
        else:
            lead_asset, lag_asset = sym2, sym1
            avg_lead_lag = -avg_lead_lag
        
        # Compute spread characteristics
        spread = self._compute_spread(prices1, prices2)
        spread_vol = spread.std()
        half_life = self._compute_half_life(spread)
        
        # Filter by half-life
        if half_life < self.min_half_life or half_life > self.max_half_life:
            return None
        
        # Compute trading score
        score = self._compute_pair_score(
            avg_correlation,
            avg_lead_lag,
            spread_vol,
            half_life
        )
        
        return PairCandidate(
            lead_asset=lead_asset,
            lag_asset=lag_asset,
            correlation=avg_correlation,
            lead_lag_days=avg_lead_lag,
            spread_volatility=spread_vol,
            half_life=half_life,
            score=score
        )
    
    def _compute_lead_lag(
        self,
        series1: np.ndarray,
        series2: np.ndarray
    ) -> Tuple[float, int]:
        """
        Compute optimal lead/lag and correlation between two series.
        
        Returns:
            (correlation, lag_days)
        """
        # Compute cross-correlation
        correlation = signal.correlate(series1, series2, mode='full')
        lags = signal.correlation_lags(len(series1), len(series2), mode='full')
        
        # Find lag with maximum correlation (within bounds)
        valid_mask = np.abs(lags) <= self.max_lead_lag_days
        valid_corr = correlation[valid_mask]
        valid_lags = lags[valid_mask]
        
        if len(valid_corr) == 0:
            return 0.0, 0
        
        max_idx = np.argmax(np.abs(valid_corr))
        best_lag = valid_lags[max_idx]
        
        # Compute actual correlation at this lag
        if best_lag >= 0:
            s1 = series1[best_lag:]
            s2 = series2[:len(s1)]
        else:
            s2 = series2[-best_lag:]
            s1 = series1[:len(s2)]
        
        if len(s1) > 1:
            actual_corr = np.corrcoef(s1, s2)[0, 1]
        else:
            actual_corr = 0.0
        
        return actual_corr, int(best_lag)
    
    def _compute_spread(
        self,
        prices1: pd.Series,
        prices2: pd.Series
    ) -> pd.Series:
        """
        Compute normalized spread between two price series.
        
        Uses simple price ratio approach.
        """
        # Normalize both series to start at 100
        norm1 = 100 * prices1 / prices1.iloc[0]
        norm2 = 100 * prices2 / prices2.iloc[0]
        
        # Spread is the difference
        spread = norm1 - norm2
        
        return spread
    
    def _compute_half_life(self, spread: pd.Series) -> float:
        """
        Compute mean reversion half-life using Ornstein-Uhlenbeck.
        
        Returns:
            Half-life in days (or periods)
        """
        # Remove NaN values
        spread = spread.dropna()
        
        if len(spread) < 20:
            return np.inf
        
        # Fit AR(1) model: spread[t] = a + b*spread[t-1] + error
        spread_lag = spread.shift(1).dropna()
        spread_curr = spread.iloc[1:]
        
        # Align
        common_idx = spread_lag.index.intersection(spread_curr.index)
        spread_lag = spread_lag.loc[common_idx]
        spread_curr = spread_curr.loc[common_idx]
        
        if len(spread_lag) < 10:
            return np.inf
        
        # Linear regression
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                spread_lag.values,
                spread_curr.values
            )
            
            # Half-life = -ln(2) / ln(slope)
            if slope <= 0 or slope >= 1:
                return np.inf
            
            half_life = -np.log(2) / np.log(slope)
            
            return half_life
            
        except Exception:
            return np.inf
    
    def _compute_pair_score(
        self,
        correlation: float,
        lead_lag_days: int,
        spread_vol: float,
        half_life: float
    ) -> float:
        """
        Compute overall trading score for a pair.
        
        Higher score = better trading opportunity
        
        Scoring factors:
        - High correlation (good)
        - Low lead_lag days (easier to trade)
        - Moderate spread volatility (tradable range)
        - Optimal half_life (10-30 days ideal)
        """
        # Correlation score (0-1)
        corr_score = max(0, correlation)
        
        # Lead/lag score (penalize large lags)
        lag_score = 1.0 / (1.0 + lead_lag_days / 5.0)
        
        # Half-life score (peak at 20 days)
        optimal_half_life = 20
        half_life_score = np.exp(-((half_life - optimal_half_life) ** 2) / (2 * 15 ** 2))
        
        # Spread volatility score (normalized, higher vol = higher potential)
        vol_score = min(1.0, spread_vol / 10.0)
        
        # Weighted combination
        score = (
            0.4 * corr_score +
            0.2 * lag_score +
            0.3 * half_life_score +
            0.1 * vol_score
        )
        
        return score
    
    def get_pair_statistics(
        self,
        pair: PairCandidate,
        price_dict: Dict[str, pd.Series]
    ) -> Dict:
        """
        Get detailed statistics for a specific pair.
        
        Args:
            pair: PairCandidate object
            price_dict: Dictionary of price series
            
        Returns:
            Dictionary with detailed statistics
        """
        prices1 = price_dict[pair.lead_asset]
        prices2 = price_dict[pair.lag_asset]
        
        # Align indices
        common_idx = prices1.index.intersection(prices2.index)
        prices1 = prices1.loc[common_idx]
        prices2 = prices2.loc[common_idx]
        
        spread = self._compute_spread(prices1, prices2)
        
        return {
            'lead_asset': pair.lead_asset,
            'lag_asset': pair.lag_asset,
            'correlation': pair.correlation,
            'lead_lag_days': pair.lead_lag_days,
            'spread_mean': spread.mean(),
            'spread_std': spread.std(),
            'spread_min': spread.min(),
            'spread_max': spread.max(),
            'half_life': pair.half_life,
            'score': pair.score,
            'data_points': len(spread)
        }

