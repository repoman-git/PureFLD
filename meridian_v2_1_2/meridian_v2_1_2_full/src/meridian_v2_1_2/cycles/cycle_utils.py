"""
Cycle Utilities for Meridian v2.1.2

Helper functions for cycle analysis and processing.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional


def normalize_series(series: pd.Series) -> pd.Series:
    """
    Normalize series to 0-1 range.
    
    Args:
        series: Input series
    
    Returns:
        pd.Series: Normalized series
    """
    if len(series) == 0:
        return series
    
    min_val = series.min()
    max_val = series.max()
    
    if max_val == min_val:
        return pd.Series(0.5, index=series.index)
    
    normalized = (series - min_val) / (max_val - min_val)
    return normalized


def smooth_series(series: pd.Series, window: int = 5) -> pd.Series:
    """
    Smooth series using simple moving average.
    
    Args:
        series: Input series
        window: Smoothing window size
    
    Returns:
        pd.Series: Smoothed series
    """
    return series.rolling(window=window, min_periods=1, center=False).mean()


def cycle_phase(
    series: pd.Series,
    cycle_length: int
) -> pd.Series:
    """
    Compute cycle phase (0 to 2π) based on position within cycle.
    
    Args:
        series: Price or indicator series
        cycle_length: Cycle length in bars
    
    Returns:
        pd.Series: Phase angle in radians (0 to 2π)
    """
    # Simple approximation: position within cycle length
    phases = []
    for i in range(len(series)):
        position_in_cycle = i % cycle_length
        phase_angle = (position_in_cycle / cycle_length) * 2 * np.pi
        phases.append(phase_angle)
    
    return pd.Series(phases, index=series.index, name='phase')


def compute_cycle_phase_normalized(
    composite_cycle: pd.Series,
    cycle_length: int
) -> pd.Series:
    """
    Compute normalized cycle phase (0.0 to 1.0).
    
    Uses composite cycle and recent extrema to determine phase:
    - 0.0 = trough (cycle bottom)
    - 0.5 = peak (cycle top)
    - 1.0 = trough again (full cycle)
    
    Args:
        composite_cycle: Composite cycle series
        cycle_length: Dominant cycle length
    
    Returns:
        pd.Series: Normalized phase (0.0 to 1.0)
    
    Notes:
        - Deterministic calculation
        - Based on rolling window extrema
        - Suitable for strategy gating
    """
    if len(composite_cycle) < cycle_length:
        # Not enough data, return neutral phase
        return pd.Series(0.5, index=composite_cycle.index)
    
    phases = []
    
    for i in range(len(composite_cycle)):
        # Look at recent cycle window
        start_idx = max(0, i - cycle_length + 1)
        window = composite_cycle.iloc[start_idx:i+1]
        
        if len(window) < 2:
            phases.append(0.5)
            continue
        
        # Find local min and max in window
        local_min = window.min()
        local_max = window.max()
        
        current_value = composite_cycle.iloc[i]
        
        # Normalize position between min and max
        if local_max != local_min:
            # Linear interpolation between min (0.0) and max (0.5)
            # Then from max (0.5) to min (1.0)
            normalized_pos = (current_value - local_min) / (local_max - local_min)
            
            # Convert to phase (0.0=trough, 0.5=peak, 1.0=trough)
            # Simple approximation using normalized position
            if normalized_pos < 0.5:
                phase = normalized_pos  # Rising: 0.0 to 0.25
            else:
                phase = 0.5 + (normalized_pos - 0.5)  # Falling: 0.5 to 1.0
            
            phases.append(phase)
        else:
            phases.append(0.5)  # Neutral if no range
    
    return pd.Series(phases, index=composite_cycle.index, name='cycle_phase')


def compute_cycle_score(
    phase: pd.Series,
    amplitude: pd.Series,
    max_amplitude: Optional[float] = None
) -> pd.Series:
    """
    Compute cycle quality score from phase and amplitude.
    
    Score formula:
        phase_score = cos(phase × 2π)  # +1 at trough, -1 at peak
        amplitude_score = amplitude / max_amplitude (normalized)
        cycle_score = 0.7 × phase_score + 0.3 × amplitude_score
    
    Args:
        phase: Cycle phase series (0.0 to 1.0)
        amplitude: Cycle amplitude series
        max_amplitude: Maximum amplitude for normalization (auto if None)
    
    Returns:
        pd.Series: Cycle score (-1 to +1)
        
    Interpretation:
        +1.0: Strong bullish (trough, rising amplitude)
        0.0: Neutral
        -1.0: Strong bearish (peak, falling amplitude)
    """
    if not phase.index.equals(amplitude.index):
        raise ValueError("Phase and amplitude indices must match")
    
    # Phase score: cos(phase × 2π)
    # This gives +1 at phase=0 (trough), -1 at phase=0.5 (peak)
    phase_score = np.cos(phase * 2 * np.pi)
    
    # Amplitude score: normalize amplitude
    if max_amplitude is None:
        max_amplitude = amplitude.max()
    
    if max_amplitude > 0:
        amplitude_score = amplitude / max_amplitude
    else:
        amplitude_score = pd.Series(0, index=amplitude.index)
    
    # Combine: 70% phase, 30% amplitude
    cycle_score = 0.7 * phase_score + 0.3 * amplitude_score
    
    cycle_score.name = 'cycle_score'
    return cycle_score


def find_zero_crossings(series: pd.Series) -> pd.Series:
    """
    Find zero crossings in series.
    
    Args:
        series: Input series
    
    Returns:
        pd.Series: +1 for upward crossing, -1 for downward, 0 otherwise
    """
    crossings = pd.Series(0, index=series.index)
    
    for i in range(1, len(series)):
        if series.iloc[i-1] < 0 and series.iloc[i] >= 0:
            crossings.iloc[i] = 1  # Upward crossing
        elif series.iloc[i-1] > 0 and series.iloc[i] <= 0:
            crossings.iloc[i] = -1  # Downward crossing
    
    return crossings


def cycle_amplitude(
    series: pd.Series,
    cycle_length: int
) -> float:
    """
    Estimate cycle amplitude.
    
    Args:
        series: Price series
        cycle_length: Cycle length
    
    Returns:
        float: Estimated amplitude (half peak-to-trough range)
    """
    if len(series) < cycle_length:
        return 0.0
    
    # Take last cycle_length bars
    recent = series.iloc[-cycle_length:]
    
    # Amplitude = (max - min) / 2
    amplitude = (recent.max() - recent.min()) / 2.0
    
    return float(amplitude)


def cycle_stability(
    series: pd.Series,
    cycle_length: int,
    num_cycles: int = 3
) -> float:
    """
    Measure cycle stability (consistency of amplitude and period).
    
    Args:
        series: Price series
        cycle_length: Expected cycle length
        num_cycles: Number of cycles to analyze
    
    Returns:
        float: Stability score (0-1, higher is more stable)
    """
    required_bars = cycle_length * num_cycles
    
    if len(series) < required_bars:
        return 0.0
    
    # Analyze last N cycles
    recent = series.iloc[-required_bars:]
    
    # Break into cycles
    amplitudes = []
    for i in range(num_cycles):
        start_idx = i * cycle_length
        end_idx = (i + 1) * cycle_length
        cycle_data = recent.iloc[start_idx:end_idx]
        
        amp = (cycle_data.max() - cycle_data.min()) / 2.0
        amplitudes.append(amp)
    
    # Stability = 1 - (coefficient of variation)
    if len(amplitudes) > 1 and np.mean(amplitudes) > 0:
        cv = np.std(amplitudes) / np.mean(amplitudes)
        stability = max(0, 1 - cv)
    else:
        stability = 0.0
    
    return float(stability)

