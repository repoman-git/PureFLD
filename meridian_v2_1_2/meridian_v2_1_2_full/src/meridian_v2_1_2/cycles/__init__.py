"""
Cycles Module for Meridian v2.1.2

Cycle phasing engine based on Hurst cycle theory and FLD projections.
"""

from .dominant_cycle import estimate_dominant_cycle
from .nominal_model import build_nominal_cycle_map
from .turning_points import detect_turning_points
from .fld_projection import project_fld
from .composite_cycle import build_composite_cycle
from .cycle_utils import (
    normalize_series,
    smooth_series,
    cycle_phase,
    compute_cycle_phase_normalized,
    compute_cycle_score,
    find_zero_crossings,
    cycle_amplitude,
    cycle_stability
)

__all__ = [
    'estimate_dominant_cycle',
    'build_nominal_cycle_map',
    'detect_turning_points',
    'project_fld',
    'build_composite_cycle',
    'normalize_series',
    'smooth_series',
    'cycle_phase',
    'compute_cycle_phase_normalized',
    'compute_cycle_score',
    'find_zero_crossings',
    'cycle_amplitude',
    'cycle_stability',
]

