"""Allocation Optimizer - Enforces constraints"""
import pandas as pd

class AllocationOptimizer:
    def __init__(self, max_exposure: float = 1.0, max_single_position: float = 0.3):
        self.max_exposure = max_exposure
        self.max_single_position = max_single_position
    
    def optimize(self, weights: pd.DataFrame) -> pd.DataFrame:
        """Apply exposure and position size constraints"""
        # Cap individual positions
        weights_capped = weights.clip(-self.max_single_position, self.max_single_position)
        
        # Scale total exposure
        total_exposure = weights_capped.abs().sum(axis=1)
        scale = self.max_exposure / (total_exposure + 1e-10)
        scale = scale.clip(upper=1.0)  # Only scale down
        
        return weights_capped.mul(scale, axis=0)

