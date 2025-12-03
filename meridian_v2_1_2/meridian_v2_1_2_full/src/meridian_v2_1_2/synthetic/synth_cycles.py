"""
Synthetic Cycle Generator for Meridian v2.1.2

Cycle component with distortions for FLD stress testing.
"""

import numpy as np


def generate_cycle_component(
    length: int,
    amplitude: float = 0.03,
    period: int = 120,
    deform: bool = True,
    seed: int = 42
) -> np.ndarray:
    """
    Generate cycle component.
    
    Can include:
    - Phase shifts
    - Amplitude variations
    - Distortions (for FLD stress testing)
    
    Args:
        length: Number of days
        amplitude: Cycle amplitude
        period: Cycle period in days
        deform: Whether to add distortions
        seed: Random seed
    
    Returns:
        np.ndarray of cycle values
    """
    np.random.seed(seed)
    
    t = np.arange(length)
    
    # Base cycle
    cycle = amplitude * np.sin(2 * np.pi * t / period)
    
    if deform:
        # Add amplitude modulation
        amp_modulation = 1.0 + 0.3 * np.sin(2 * np.pi * t / (period * 3))
        cycle = cycle * amp_modulation
        
        # Add phase distortion
        phase_noise = np.cumsum(np.random.randn(length) * 0.01)
        cycle_with_noise = amplitude * np.sin(2 * np.pi * (t + phase_noise) / period)
        
        # Blend
        cycle = 0.7 * cycle + 0.3 * cycle_with_noise
    
    return cycle

